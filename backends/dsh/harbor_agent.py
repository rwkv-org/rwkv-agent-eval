"""DSH + dsh-rwkv-plugin as a Harbor installed agent.

    PYTHONPATH=. harbor run -p tasks/<task> -a backends.dsh.harbor_agent:DshRwkv \
        --ak rwkv_url=http://host:8000 [--ak rwkv_model=<id>] \
        [--ak plugin_dir=../dsh-rwkv-plugin] [--ak dsh_version=0.2.1-rc.5] [--ak max_steps=12] \
        [--ak time_zone=Asia/Shanghai]

No network install inside the task container:
  install()    uploads .cache/rae-node-<dsh>-linux-<arch>.tar.gz (Node + DSH +
               pnpm, built by backends/dsh/build-toolchain.sh) to /opt/rae-node.
  configure()  copies environment/workspace into /app when the task runs on
               the shared prebuilt image (bank/prebuilt.py: no per-task
               build, so /app starts empty), then uploads the local plugin checkout (every trial, so the run
               records exactly that commit) and adds it to the headless profile
               with `dsh plugin add`, the same path a user install takes.
  run()        the plugin's scripts/headless.ts --installed, once per user
               turn (turns from /rae/turns.json if the task ships one, joined
               with --session-id). Per turn: events-N.jsonl, final-N.txt,
               ws-N.json; overall events.jsonl and final.txt (last reply,
               the backend contract in the README).

Model id and backend (lightning / irwkv) come from the endpoint's /v1/models;
--ak rwkv_model is only needed when it serves several. Each trial writes
/logs/agent/provenance.json on the host side: server reply, toolchain sha256,
full plugin and eval HEADs with their uncommitted diffs, Harbor version.

The task image needs glibc (Debian/Ubuntu based) and must reach the endpoint.
"""
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import shlex
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

EVAL_ROOT = Path(__file__).resolve().parents[2]
BASE_IMAGE = 'rae-eval-base:py312-slim'  # bank/prebuilt.py BASE_IMAGE
TOOLCHAIN = '/opt/rae-node'
PLUGIN = '/installed-agent/dsh-rwkv-plugin'
HOME = '/installed-agent/dsh-home'
ENV = {'PATH': f'{TOOLCHAIN}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
       'DSH_HOME': HOME, 'DSH_TELEMETRY_DISABLED': '1', 'DSH_PERMISSION_MODE': 'danger-full-access'}
PLUGIN_FILES = ('package.json', 'cordis.patch.yml', 'lib', 'scripts')
# Web replay overlay: lives inside the DSH package so `@deepseek-ai/dsh-web` resolves.
REPLAY = f'{TOOLCHAIN}/lib/node_modules/@deepseek-ai/dsh/rae-web-replay.mjs'
# Rows appended to the headless profile so the prompt and tools match how the
# training data was made (rwkv-agent-pipeline scripts/run.ts writeProfile):
# the @path section from file-reference-local, and web tools answered from an
# archive (no archive: empty search, 404 fetch, as non-web training cases saw).
EXTRA_PATCH = f'''- insert:
    - id: rae-web-replay
      name: "file://{REPLAY}"
    - id: file-reference-local
      name: '@deepseek-ai/dsh-file-reference-local'
- id: web
  config:
    searchProvider: replay
    fetchProvider: replay
- id: web-fetch-http
  disabled: true
'''
# After turn N (argv[1]): final-N.txt (last `final` event), session-N.txt, and
# ws-N.json, sha256 of every file under /app, so the verifier can check
# per-turn expectations (e.g. a read-only turn left files alone).
TURN_JS = r'''
const fs=require('fs'),path=require('path'),crypto=require('crypto');const n=process.argv[1];
let t='',s='';for(const x of fs.readFileSync(`/logs/agent/events-${n}.jsonl`,'utf8').split('\n')){
try{const e=JSON.parse(x);if(e.type==='final')t=e.text||'';if(e.type==='session'&&e.sessionId)s=e.sessionId}catch{}}
fs.writeFileSync(`/logs/agent/final-${n}.txt`,t);fs.writeFileSync(`/logs/agent/session-${n}.txt`,s);
const h={};const skip=new Set(['node_modules','.git','__pycache__']);
(function w(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){if(skip.has(e.name))continue;const p=path.join(d,e.name);
if(e.isDirectory())w(p);else if(e.isFile())h[path.relative('/app',p)]=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')}})('/app');
fs.writeFileSync(`/logs/agent/ws-${n}.json`,JSON.stringify(h))
'''


def _git(path, *args):
    p = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ''


def _commit(path):
    """Short HEAD, with `*` when the checkout has uncommitted changes."""
    return _git(path, 'rev-parse', '--short', 'HEAD') + ('*' if _git(path, 'status', '--porcelain') else '')


def _checkout(path):
    """Full HEAD plus the uncommitted diff and untracked files, so a `*` commit
    can still be reproduced from the run directory."""
    return {'path': str(path), 'head': _git(path, 'rev-parse', 'HEAD'),
            'diff': _git(path, 'diff', 'HEAD'),
            'untracked': _git(path, 'ls-files', '--others', '--exclude-standard').splitlines()}


def _served_models(base_url, wait_sec=900, key=''):
    """GET <base>/v1/models: what the endpoint actually serves, so the run
    records the server's model id rather than whatever was typed on the CLI.
    Retries for up to wait_sec (--ak endpoint_wait_sec), so an inference server
    restart pauses new trials instead of failing the whole job."""
    url = base_url.rstrip('/')
    if not url.endswith('/v1'):
        url += '/v1'
    deadline = time.monotonic() + wait_sec
    while True:
        try:
            req = urllib.request.Request(url + '/models', headers={'Authorization': f'Bearer {key}'} if key else {})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except (OSError, ValueError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(15)


_SHA = {}


def _sha256(path):
    """sha256 of a file, cached per (path, mtime, size): the toolchain is 237 MB."""
    st = path.stat()
    key = (str(path), st.st_mtime_ns, st.st_size)
    if key not in _SHA:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        _SHA[key] = h.hexdigest()
    return _SHA[key]


def _harbor_version():
    try:
        return importlib.metadata.version('harbor')
    except importlib.metadata.PackageNotFoundError:
        return '-'


class DshRwkv(BaseInstalledAgent):
    def __init__(self, logs_dir: Path, rwkv_url: str = "", rwkv_model: str = '', rwkv_backend: str = '',
                 plugin_dir: str = '', dsh_version: str = 'dsh-8bd07339', arch: str = '',
                 max_steps: int | str | None = None, adapter: str | None = None, trace: str | bool = True,
                 persona_model: str = 'rwkv7-g1l-13.3b', endpoint_wait_sec: int | str = 900,
                 time_zone: str = '', plugin_config: str = '', container_url: str = '',
                 api_key_env: str = 'RWKV_API_KEY', **kwargs):
        super().__init__(logs_dir, **kwargs)
        if not rwkv_url:
            raise ValueError('DshRwkv needs --ak rwkv_url=...')
        # Engine credential (rwkv_lightning --password / iRWKV bearer key): read from the
        # host env var named by api_key_env, given to DSH only as process env (headless.ts
        # --api-key-env), never on a command line or in job JSON. Unset = open engine.
        self.api_key_env = api_key_env
        self.api_key = os.environ.get(api_key_env, '') if api_key_env else ''
        # The endpoint is the source of truth for model id and backend kind;
        # --ak rwkv_model / rwkv_backend are only checked against it.
        self.served = _served_models(rwkv_url, int(endpoint_wait_sec), self.api_key)
        models = {m['id']: m for m in self.served.get('data', [])}
        if not rwkv_model:
            if len(models) != 1:
                raise ValueError(f'endpoint serves {sorted(models)}; pick one with --ak rwkv_model=...')
            rwkv_model = next(iter(models))
        elif rwkv_model not in models:
            raise ValueError(f'endpoint does not serve {rwkv_model!r}; it serves {sorted(models)}')
        owned_by = models[rwkv_model].get('owned_by', '')
        # rwkv_lightning reports itself as "rwkv_lighting_cuda" (sic); accept both spellings.
        inferred = 'lightning' if ('lightning' in owned_by or 'lighting' in owned_by) else 'irwkv'
        if rwkv_backend and rwkv_backend != inferred:
            raise ValueError(f'--ak rwkv_backend={rwkv_backend} but the endpoint is {owned_by!r} ({inferred})')
        self.rwkv_url, self.rwkv_model, self.rwkv_backend = rwkv_url, rwkv_model, inferred
        # DSH runs inside the task container: the engine as reached from there
        # (e.g. http://172.17.0.1:8000 when rwkv_url is a host loopback address).
        self.container_url = container_url or rwkv_url
        self.plugin_dir = Path(plugin_dir or EVAL_ROOT.parent / 'dsh-rwkv-plugin').resolve()
        self.dsh_version, self.arch = dsh_version, arch
        self.max_steps, self.adapter = max_steps, adapter
        # RWKV traces (exact prompt bytes + raw output per request) to /logs/agent/trace:
        # how prompt parity with the training data is checked. On by default.
        self.trace = str(trace).lower() not in ('0', 'false', 'no', '')
        # The model name the system prompt states. Training data was made with
        # "rwkv7-g1l-13.3b" for every row, so keep that by default for prompt parity.
        self.persona_model = persona_model
        # Date line at the end of the system prompt, in this zone (also DSH's TZ,
        # so bash's `date` agrees). Off by default: models trained on data from
        # before 2026-11-10 never saw the line. Turn it on for models trained on
        # dated data (rwkv-agent-pipeline qc rule date-line), e.g. Asia/Shanghai.
        self.time_zone = time_zone
        # Experiment only: a JSON file (path relative to the eval root, or absolute) of extra
        # rwkv-llm config keys, e.g. taskContract / toolOverrides. Breaks training parity.
        self.plugin_config_path = plugin_config
        self.plugin_config = {}
        if plugin_config:
            path = Path(plugin_config)
            self.plugin_config = json.loads((path if path.is_absolute() else EVAL_ROOT / path).read_text())
        self.plugin_commit = _commit(self.plugin_dir)
        self.eval_commit = _commit(EVAL_ROOT)
        self.toolchain_sha256 = ''

    @staticmethod
    def name() -> str:
        return 'dsh-rwkv'

    def version(self) -> str | None:
        # Shown in Harbor's result.json; report.py parses these `key value` pairs.
        # The full record (diffs, toolchain hash, /v1/models reply) is provenance.json.
        return (f'dsh {self.dsh_version}; plugin {self.plugin_commit}; eval {self.eval_commit}; '
                f'model {self.rwkv_model}; backend {self.rwkv_backend}; adapter {self.adapter or "-"}; '
                f'persona {self.persona_model}; date {self.time_zone or "off"}; '
                f'plugin_config {self.plugin_config_path or "-"}; '
                f'harbor {_harbor_version()}')

    def _write_provenance(self) -> None:
        record = {
            'model': self.rwkv_model, 'backend': self.rwkv_backend, 'adapter': self.adapter,
            'endpoint': self.rwkv_url, 'container_endpoint': self.container_url,
            'api_key_env': self.api_key_env if self.api_key else None, 'served_models': self.served,
            'max_steps': self.max_steps, 'dsh_version': self.dsh_version,
            'persona_model': self.persona_model, 'time_zone': self.time_zone, 'extra_patch': EXTRA_PATCH,
            'plugin_config_path': self.plugin_config_path, 'plugin_config': self.plugin_config,
            'web_replay_sha256': _sha256(EVAL_ROOT / 'backends/dsh/web-replay.mjs'),
            'toolchain_mounted': getattr(self, 'toolchain_mounted', False),
            'workspace_seeded': getattr(self, 'workspace_seeded', False),
            'toolchain_sha256': self.toolchain_sha256, 'harbor_version': _harbor_version(),
            'plugin': _checkout(self.plugin_dir), 'eval': _checkout(EVAL_ROOT),
            'host': {'platform': platform.platform(), 'python': platform.python_version()},
        }
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.logs_dir / 'provenance.json').write_text(json.dumps(record, ensure_ascii=False, indent=1))

    async def _upload_tar(self, environment: BaseEnvironment, local: Path, dest_dir: str):
        remote = f'/tmp/{local.name}'
        await environment.upload_file(local, remote)
        await self.exec_as_root(environment, command=(
            f'mkdir -p {shlex.quote(dest_dir)} && tar -xzf {remote} -C {shlex.quote(dest_dir)} && rm -f {remote}'))

    async def install(self, environment: BaseEnvironment) -> None:
        arch = self.arch
        if not arch:
            res = await environment.exec(command='uname -m')
            arch = {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(res.stdout.strip(), res.stdout.strip())
        tgz = EVAL_ROOT / '.cache' / f'rae-node-{self.dsh_version}-linux-{arch}.tar.gz'
        if not tgz.exists():
            raise FileNotFoundError(f'{tgz} missing: run backends/dsh/build-toolchain.sh {self.dsh_version} linux/{arch}')
        self.toolchain_sha256 = _sha256(tgz)
        # A toolchain mounted read-only at /opt/rae-node (scripts/prepare-toolchain.sh
        # + harbor run --mounts) skips the per-trial 237 MB upload and unpack, the
        # bottleneck at high concurrency. Its marker must name this exact tarball
        # and replay plugin, or the trial falls back to uploading.
        res = await self.exec_as_root(environment, command=f'cat {TOOLCHAIN}/RAE_TOOLCHAIN 2>/dev/null || true')
        try:
            marker = json.loads(res.stdout or '')
        except json.JSONDecodeError:
            marker = {}
        want = {'label': self.dsh_version, 'tarball_sha256': self.toolchain_sha256,
                'replay_sha256': _sha256(EVAL_ROOT / 'backends/dsh/web-replay.mjs')}
        self.toolchain_mounted = all(marker.get(k) == v for k, v in want.items())
        if marker and not self.toolchain_mounted:
            raise RuntimeError(f'{TOOLCHAIN} is mounted but stale ({marker} != {want}): rerun scripts/prepare-toolchain.sh')
        if not self.toolchain_mounted:
            await self._upload_tar(environment, tgz, '/opt')
        # DSH runs inside the container: the engine must be reachable from there.
        # Fail now rather than score every turn of a broken connection as a wrong answer.
        probe = ('const u=process.env.RAE_URL.replace(/\\/+$/,"");const v=u.endsWith("/v1")?u:u+"/v1";'
                 'const k=process.env.RAE_KEY;fetch(v+"/models",{headers:k?{Authorization:"Bearer "+k}:{},signal:AbortSignal.timeout(15000)})'
                 '.then(r=>{console.log("rae-endpoint "+r.status);process.exit(r.ok?0:3)})'
                 '.catch(e=>{console.log("rae-endpoint "+e.message);process.exit(3)})')
        res = await environment.exec(command=f'{TOOLCHAIN}/bin/node -e {shlex.quote(probe)} || true',
                                     env={'RAE_URL': self.container_url, 'RAE_KEY': self.api_key})
        out = (res.stdout or '').strip()
        if 'rae-endpoint 200' not in out:
            raise RuntimeError(f'engine {self.container_url} not reachable from the task container ({out or "no output"}); '
                               'bind it to the docker bridge (e.g. 172.17.0.1) and pass --ak container_url=...')

    async def setup(self, environment: BaseEnvironment) -> None:
        # Harbor 0.25.0 documents configure() but never calls it; run it here
        # (once, in case a later release starts calling it after install()).
        await super().setup(environment)
        await self.configure(environment)

    async def configure(self, environment: BaseEnvironment) -> None:
        if getattr(self, '_configured', False):
            return
        self._configured = True
        await self._seed_workspace(environment)
        with tempfile.TemporaryDirectory() as tmp:
            tgz = Path(tmp) / 'dsh-rwkv-plugin.tar.gz'
            with tarfile.open(tgz, 'w:gz') as tar:
                for part in PLUGIN_FILES:
                    tar.add(self.plugin_dir / part, arcname=part)
                meta = json.dumps({'commit': self.plugin_commit}).encode()
                info = tarfile.TarInfo('rae-plugin-commit.json')
                info.size = len(meta)
                tar.addfile(info, io.BytesIO(meta))
            await self._upload_tar(environment, tgz, PLUGIN)
        owner = ''
        if environment.default_user is not None:
            owner = f' && chown -R {shlex.quote(str(environment.default_user))} /installed-agent'
        if not getattr(self, 'toolchain_mounted', False):  # a mounted toolchain already has it (checked in install)
            await environment.upload_file(EVAL_ROOT / 'backends/dsh/web-replay.mjs', REPLAY)
        with tempfile.TemporaryDirectory() as tmp:
            patch = Path(tmp) / 'extra-patch.yml'
            patch.write_text(EXTRA_PATCH)
            await environment.upload_file(patch, '/installed-agent/extra-patch.yml')
        await self.exec_as_root(environment, command=f'chmod 644 /installed-agent/extra-patch.yml; chmod 644 {REPLAY} 2>/dev/null; mkdir -p {HOME}{owner}')
        await self.exec_as_agent(environment, env=ENV, command=(
            f'dsh plugin --profile headless add {PLUGIN} > /logs/agent/plugin-add.txt 2>&1 '
            '|| { cat /logs/agent/plugin-add.txt; exit 1; }'))
        self._write_provenance()

    async def _seed_workspace(self, environment: BaseEnvironment) -> None:
        """Prebuilt-image tasks (task.toml docker_image, bank/prebuilt.py) start
        with an empty /app: copy the task's environment/workspace in, which is
        what the per-task image's `COPY workspace/ /app/` did. A task image
        built the old way already has it (every workspace holds at least .keep)."""
        self.workspace_seeded = False
        workspace = Path(environment.environment_dir) / 'workspace'
        # Only tasks on the shared image: OSS tasks keep their own Dockerfile
        # and may have no /app at all.
        if environment.task_env_config.docker_image != BASE_IMAGE or not workspace.is_dir():
            return
        res = await self.exec_as_root(environment, command='ls -A /app 2>/dev/null | head -1 || true')
        if (res.stdout or '').strip():
            return
        await environment.upload_dir(workspace, '/app')
        self.workspace_seeded = True

    @with_prompt_template
    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        flags = ['--installed', f'--home {HOME}', '--dsh dsh',
                 f'--backend {shlex.quote(self.rwkv_backend)}', f'--base-url {shlex.quote(self.container_url)}',
                 f'--model {shlex.quote(self.rwkv_model)}']
        if self.max_steps:
            flags.append(f'--max-steps {int(self.max_steps)}')
        if self.adapter:
            flags.append(f'--adapter {shlex.quote(self.adapter)}')
        if self.trace:
            flags.append('--trace-dir /logs/agent/trace')
        run_env = dict(ENV)
        if self.api_key:
            flags.append('--api-key-env RWKV_API_KEY')
            run_env['RWKV_API_KEY'] = self.api_key
        if self.time_zone:
            flags.append(f'--current-date --time-zone {shlex.quote(self.time_zone)}')
        if self.plugin_config:
            flags.append(f'--plugin-config {shlex.quote(json.dumps(self.plugin_config, ensure_ascii=False))}')
        flags += [f'--model-id {shlex.quote(self.persona_model)}', '--extra-patch /installed-agent/extra-patch.yml']
        # Multi-turn tasks ship their scripted turns as environment/turns.json (a
        # JSON list of prompts; turn 1 is the instruction); web tasks ship
        # archived responses as environment/web.json. Both are read on the host:
        # a prebuilt-image task never has them in the container, and an image
        # built the old way copied them to /rae, which is deleted before the
        # agent starts so it cannot read later turns.
        env_dir = Path(environment.environment_dir)
        shipped = {name: (env_dir / name).read_text() for name in ('turns.json', 'web.json') if (env_dir / name).is_file()}
        await self.exec_as_root(environment, command='rm -rf /rae')
        try:
            turns = [str(t) for t in json.loads(shipped.get('turns.json', ''))] or [instruction]
        except (json.JSONDecodeError, TypeError):
            turns = [instruction]
        archive = shipped.get('web.json', '').strip() or '{}'
        session = ''
        statuses = []
        for n, text in enumerate(turns, 1):
            resume = f' --session-id {shlex.quote(session)}' if session else ''
            web = f'/tmp/rae-web-{n}.json'
            with tempfile.TemporaryDirectory() as tmp:
                local = Path(tmp) / 'web.json'
                local.write_text(archive)
                await environment.upload_file(local, web)
            await self.exec_as_root(environment, command=f'chmod 644 {web}')
            res = await self.exec_as_agent(environment, env={**run_env, 'RAE_WEB_ARCHIVE': web}, command=(
                f'printf %s {shlex.quote(text)} | node {PLUGIN}/scripts/headless.ts {" ".join(flags)}{resume} - '
                f'> /logs/agent/events-{n}.jsonl 2> /logs/agent/stderr-{n}.txt; status=$?; '
                f'node -e {shlex.quote(TURN_JS)} {n}; rm -f {web}; echo "rae-status $status"'))
            out = res.stdout or ''
            statuses.append(int(out.rsplit('rae-status ', 1)[1].split()[0]) if 'rae-status ' in out else 1)
            session = (await self.exec_as_agent(environment, env=ENV, command=(
                f'cat /logs/agent/session-{n}.txt 2>/dev/null'))).stdout.strip() or session
            if not session:
                break  # no session to continue: later turns would start from scratch
        # Processes the kernel killed at the container's memory cap (cgroup v2
        # memory.events; prebuilt tasks set memory_mb). runner/oom_tasks.py
        # counts them per task, so a task that keeps hitting the cap can be
        # told apart from one run whose model-written code ran away.
        res = await self.exec_as_root(environment, command="awk '/^oom_kill /{print $2}' /sys/fs/cgroup/memory.events 2>/dev/null || true")
        try:
            oom_kills = int((res.stdout or '').strip() or 0)
        except ValueError:
            oom_kills = 0
        # final.txt / events.jsonl keep the single-turn contract: last reply, all events.
        last = len(statuses)
        await self.exec_as_agent(environment, env=ENV, command=(
            f'cp /logs/agent/final-{last}.txt /logs/agent/final.txt; '
            f'cat $(ls /logs/agent/events-*.jsonl | sort -t- -k2 -n) > /logs/agent/events.jsonl; '
            # the generated profile holds the engine credential (apiKey row): copy it without that line
            f"grep -v '^ *apiKey:' {HOME}/profiles/headless/cordis.patch.yml > /logs/agent/dsh-patch.yml 2>/dev/null; "
            f'printf %s {shlex.quote(json.dumps({"turns": len(turns), "ran": last, "status": statuses, "oom_kills": oom_kills}))} '
            '> /logs/agent/turns.json; '
            f'exit {next((x for x in statuses if x), 0)}'))

    def populate_context_post_run(self, context: AgentContext) -> None:
        events = self.logs_dir / 'events.jsonl'
        if not events.exists():
            return
        out = inp = 0
        for line in events.read_text().splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            usage = e.get('usage') if e.get('type') == 'status' else None
            if usage:
                out += usage.get('outputTokens', 0)
                inp += usage.get('inputTokens', 0)
        context.n_output_tokens, context.n_input_tokens = out, inp
