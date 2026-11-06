"""DSH + dsh-rwkv-plugin as a Harbor installed agent.

    PYTHONPATH=. harbor run -p tasks/<task> -a backends.dsh.harbor_agent:DshRwkv \
        --ak rwkv_url=http://host:8000 [--ak rwkv_model=<id>] \
        [--ak plugin_dir=../dsh-rwkv-plugin] [--ak dsh_version=0.2.1-rc.5] [--ak max_steps=12]

No network install inside the task container:
  install()    uploads .cache/rae-node-<dsh>-linux-<arch>.tar.gz (Node + DSH +
               pnpm, built by backends/dsh/build-toolchain.sh) to /opt/rae-node.
  configure()  uploads the local plugin checkout (every trial, so the run
               records exactly that commit) and adds it to the headless profile
               with `dsh plugin add`, the same path a user install takes.
  run()        the plugin's scripts/headless.ts --installed. Events go to
               /logs/agent/events.jsonl, the final message to
               /logs/agent/final.txt (the backend contract in the README).

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
import platform
import shlex
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

EVAL_ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = '/opt/rae-node'
PLUGIN = '/installed-agent/dsh-rwkv-plugin'
HOME = '/installed-agent/dsh-home'
ENV = {'PATH': f'{TOOLCHAIN}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
       'DSH_HOME': HOME, 'DSH_TELEMETRY_DISABLED': '1', 'DSH_PERMISSION_MODE': 'danger-full-access'}
PLUGIN_FILES = ('package.json', 'cordis.patch.yml', 'lib', 'scripts')


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


def _served_models(base_url):
    """GET <base>/v1/models: what the endpoint actually serves, so the run
    records the server's model id rather than whatever was typed on the CLI."""
    url = base_url.rstrip('/')
    if not url.endswith('/v1'):
        url += '/v1'
    with urllib.request.urlopen(url + '/models', timeout=15) as r:
        return json.loads(r.read())


def _harbor_version():
    try:
        return importlib.metadata.version('harbor')
    except importlib.metadata.PackageNotFoundError:
        return '-'


class DshRwkv(BaseInstalledAgent):
    def __init__(self, logs_dir: Path, rwkv_url: str = "", rwkv_model: str = '', rwkv_backend: str = '',
                 plugin_dir: str = '', dsh_version: str = '0.2.1-rc.5', arch: str = '',
                 max_steps: int | str | None = None, adapter: str | None = None, **kwargs):
        super().__init__(logs_dir, **kwargs)
        if not rwkv_url:
            raise ValueError('DshRwkv needs --ak rwkv_url=...')
        # The endpoint is the source of truth for model id and backend kind;
        # --ak rwkv_model / rwkv_backend are only checked against it.
        self.served = _served_models(rwkv_url)
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
        self.plugin_dir = Path(plugin_dir or EVAL_ROOT.parent / 'dsh-rwkv-plugin').resolve()
        self.dsh_version, self.arch = dsh_version, arch
        self.max_steps, self.adapter = max_steps, adapter
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
                f'harbor {_harbor_version()}')

    def _write_provenance(self) -> None:
        record = {
            'model': self.rwkv_model, 'backend': self.rwkv_backend, 'adapter': self.adapter,
            'endpoint': self.rwkv_url, 'served_models': self.served,
            'max_steps': self.max_steps, 'dsh_version': self.dsh_version,
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
        self.toolchain_sha256 = hashlib.sha256(tgz.read_bytes()).hexdigest()
        await self._upload_tar(environment, tgz, '/opt')

    async def setup(self, environment: BaseEnvironment) -> None:
        # Harbor 0.25.0 documents configure() but never calls it; run it here
        # (once, in case a later release starts calling it after install()).
        await super().setup(environment)
        await self.configure(environment)

    async def configure(self, environment: BaseEnvironment) -> None:
        if getattr(self, '_configured', False):
            return
        self._configured = True
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
        await self.exec_as_root(environment, command=f'mkdir -p {HOME}{owner}')
        await self.exec_as_agent(environment, env=ENV, command=(
            f'dsh plugin --profile headless add {PLUGIN} > /logs/agent/plugin-add.txt 2>&1 '
            '|| { cat /logs/agent/plugin-add.txt; exit 1; }'))
        self._write_provenance()

    @with_prompt_template
    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        flags = ['--installed', f'--home {HOME}', '--dsh dsh',
                 f'--backend {shlex.quote(self.rwkv_backend)}', f'--base-url {shlex.quote(self.rwkv_url)}',
                 f'--model {shlex.quote(self.rwkv_model)}']
        if self.max_steps:
            flags.append(f'--max-steps {int(self.max_steps)}')
        if self.adapter:
            flags.append(f'--adapter {shlex.quote(self.adapter)}')
        final_js = ("const fs=require('fs');const l=fs.readFileSync('/logs/agent/events.jsonl','utf8').split('\\n');"
                    "let t='';for(const x of l){try{const e=JSON.parse(x);if(e.type==='final')t=e.text||''}catch{}}"
                    "fs.writeFileSync('/logs/agent/final.txt',t)")
        await self.exec_as_agent(environment, env=ENV, command=(
            f'printf %s {shlex.quote(instruction)} | node {PLUGIN}/scripts/headless.ts {" ".join(flags)} - '
            '> /logs/agent/events.jsonl 2> /logs/agent/stderr.txt; status=$?; '
            f'node -e {shlex.quote(final_js)}; '
            f'cp -r {HOME}/profiles/headless/cordis.patch.yml /logs/agent/dsh-patch.yml 2>/dev/null; '
            'exit $status'))

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
