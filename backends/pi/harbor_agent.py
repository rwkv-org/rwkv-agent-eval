"""Pi + rwkv-pi as a Harbor installed agent.

    PYTHONPATH=. harbor run -p tasks/<task> -a backends.pi.harbor_agent:PiRwkv \
        --ak rwkv_url=http://host:8000 [--ak container_url=http://172.17.0.1:8000] \
        [--ak rwkv_model=<id>] [--ak api_key_env=RWKV_API_KEY] [--ak max_steps=40] \
        [--ak adapter=<id> --ak adapter_version=<v>] [--ak tools=read,write,edit,bash]

The counterpart of backends/dsh (DshRwkv), with the same backend contract
(README "框架接口") so runner/ reads both the same way. What differs is what
Pi and DSH are:

  DSH   a host app with a plugin profile; dsh-rwkv-plugin talks to Lightning or
        irwkv; tools incl. grep/glob/web; one `headless.ts` run per user turn.
  Pi    a coding agent run from its pinned source (rwkv-pi .upstream/pi, v1.5.0)
        with rwkv-pi as an extension provider: rwkv-pi renders Pi's messages
        into an RWKV prompt itself (src/prompt.ts), posts raw continuations to
        Lightning /v1/batch/completions and parses XML tool calls client-side
        (src/xml.ts). Tools are Pi's own read/write/edit/bash (the training
        allowlist); there are no web tools, so web.json archives are not used.

No network install inside the task container:
  install()    uploads .cache/rae-pi-<label>-linux-<arch>.tar.gz (Node + Pi
               source + compiled rwkv-pi + helpers, built by
               backends/pi/build-toolchain.sh) to /opt/rae-pi, or uses a
               read-only mount from scripts/prepare-toolchain.sh pi. Then checks
               the container can reach the engine (fails fast if not).
  configure()  seeds /app on the shared prebuilt image (as DSH does), writes
               Pi's settings exactly as the rwkv-pi harness made training data
               (compaction off, retries off), writes provenance.json.
  run()        one Pi process per user turn (turns from environment/turns.json;
               turn 2+ and Harbor multi-step steps resume with --continue).
               Per turn: pi-N.txt (Pi's JSON stream), events-N.jsonl (converted
               to the DSH event schema), final-N.txt, session-N.txt, ws-N.json;
               overall events.jsonl, final.txt, turns.json; trace/ holds the exact
               request/response bytes of every engine call (backends/pi/trace.mjs).

Training parity (what the model saw when rwkv-pi made the data): the
rwkv-pi launcher's flags (--no-extensions + rwkv-pi extension, --no-skills,
--no-context-files, --no-prompt-templates, thinking high, explicit --tools
allowlist), RWKV_PI_PARITY=1, and a turn budget that does not add text to the
system prompt (backends/pi/budget.mjs; Harbor's stock Pi max_turns does).

Model id and backend kind come from the endpoint's /v1/models, as for DSH;
the engine credential is read from the host env var named by api_key_env and
passed to the container only as process env (never into job JSON).
"""
import json
import platform
import re
import shlex
import tempfile
import time
import urllib.request
from pathlib import Path

from pydantic import Field
from harbor.agents.base import BaseAgent
from harbor.agents.capabilities import AgentCapabilities
from harbor.agents.installed.base import with_prompt_template
from harbor.agents.installed.pi import Pi, PiOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from backends.dsh.harbor_agent import BASE_IMAGE, _checkout, _commit, _harbor_version, _sha256

EVAL_ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = '/opt/rae-pi'
PI_HOME = '/installed-agent/pi-home'          # PI_CODING_AGENT_DIR: settings only, no auth/models
SESSIONS = '/logs/agent/pi/sessions'           # = Pi._SESSIONS_DIRECTORY under the agent log dir
DEFAULT_TOOLS = 'read,write,edit,bash'         # rwkv-pi DEFAULT_PI_TOOLS: the training allowlist
# rwkv-pi harness.ts SettingsManager.inMemory(...): what training data was made with.
SETTINGS = {'compaction': {'enabled': False}, 'retry': {'enabled': False, 'provider': {'maxRetries': 0}}}
PI_CLI = f'{TOOLCHAIN}/pi-source/packages/coding-agent/src/cli.ts'
RESOLVER = f'{TOOLCHAIN}/pi-source/packages/coding-agent/src/experimental/source-resolver.ts'
BASE_ENV = {'PATH': f'{TOOLCHAIN}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'PI_CODING_AGENT_DIR': PI_HOME, 'PI_TELEMETRY_DISABLED': '1', 'NO_COLOR': '1'}


def _v1(url: str) -> str:
    url = url.rstrip('/')
    return url if url.endswith('/v1') else url + '/v1'


def _served_models(base_url: str, key: str = '', wait_sec: int = 900) -> dict:
    """GET <base>/v1/models with the engine credential (Lightning started with
    --password requires it). Retries for wait_sec so an engine restart pauses
    new trials instead of failing the job."""
    req = urllib.request.Request(_v1(base_url) + '/models', headers={'Authorization': f'Bearer {key}'} if key else {})
    deadline = time.monotonic() + wait_sec
    while True:
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except (OSError, ValueError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(15)


def _label(provider_dir: Path) -> str:
    """Toolchain label build-toolchain.sh gives the provider checkout as it is now."""
    from backends.dsh.harbor_agent import _git
    dirty = _git(provider_dir, 'diff', '--name-only', 'HEAD', '--', 'src', 'package.json', 'package-lock.json', 'tsconfig.json')
    return f"rwkv-pi-{_git(provider_dir, 'rev-parse', '--short', 'HEAD')}{'-dirty' if dirty else ''}"


class PiRwkvOptions(PiOptions):
    rwkv_url: str = Field(default='', description='Engine API root as reached from the Harbor host.')
    container_url: str = Field(default='', description='Engine API root as reached from inside the task container (default: rwkv_url).')
    rwkv_model: str = ''
    rwkv_backend: str = ''
    api_key_env: str = Field(default='RWKV_API_KEY', description='Host env var holding the engine credential (may be unset for an open engine).')
    provider_dir: str = Field(default='', description='rwkv-pi checkout (default ../rwkv-pi); used for the toolchain label and provenance.')
    pi_label: str = Field(default='', description='Toolchain label (default: the label of provider_dir HEAD).')
    arch: str = ''
    max_steps: int | None = Field(default=None, ge=1, description='Model turns per user turn (Pi turn_end count).')
    adapter: str | None = None
    adapter_version: str | None = None
    adapter_scale: float | None = None
    trace: bool = True
    tools: str = DEFAULT_TOOLS
    context_window: int | None = Field(default=None, ge=1024)
    max_tokens: int = Field(default=8192, ge=1)
    endpoint_wait_sec: int = 900
    provider_env: str = Field(default='', description='Experiment only: JSON file of extra RWKV_* env for rwkv-pi. Breaks training parity.')


class PiRwkv(Pi):
    options_model = PiRwkvOptions
    options: PiRwkvOptions
    capabilities = AgentCapabilities(atif=True, reasoning_effort=True, resume=True)
    MODEL_CONNECTION = None  # rwkv-pi owns the engine connection; Harbor's model routing is not used.

    @classmethod
    def resolve_model_connection_config(cls, *args, **kwargs):
        return BaseAgent.resolve_model_connection_config.__func__(cls, *args, **kwargs)

    @classmethod
    def check_model_credentials(cls, connection, *, kwargs, env, explicit_env=None):
        return None  # the engine key is optional and read in __init__ from api_key_env

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if str(self.environment_logs_dir) != '/logs/agent':
            raise ValueError(f'PiRwkv writes the backend contract under /logs/agent, not {self.environment_logs_dir}')
        o = self.options
        if not o.rwkv_url:
            raise ValueError('PiRwkv needs --ak rwkv_url=...')
        self.api_key = self._get_env(o.api_key_env) or ''
        self.served = _served_models(o.rwkv_url, self.api_key, int(o.endpoint_wait_sec))
        models = {m['id']: m for m in self.served.get('data', [])}
        model = o.rwkv_model or (self.model_name or '').split('/', 1)[-1]
        if not model:
            if len(models) != 1:
                raise ValueError(f'endpoint serves {sorted(models)}; pick one with --ak rwkv_model=...')
            model = next(iter(models))
        elif model not in models:
            raise ValueError(f'endpoint does not serve {model!r}; it serves {sorted(models)}')
        owned_by = models[model].get('owned_by', '')
        inferred = 'lightning' if ('lightning' in owned_by or 'lighting' in owned_by) else 'irwkv'
        if o.rwkv_backend and o.rwkv_backend != inferred:
            raise ValueError(f'--ak rwkv_backend={o.rwkv_backend} but the endpoint is {owned_by!r} ({inferred})')
        # rwkv-pi renders and tokenizes with the Lightning-native tokenizer only; other engines would
        # count and serve different tokens than the ones the model was trained on.
        if inferred != 'lightning':
            raise ValueError(f'PiRwkv requires an rwkv_lightning_cuda endpoint; {model!r} is owned by {owned_by!r}')
        self.rwkv_model, self.rwkv_backend = model, inferred
        self.rwkv_url = _v1(o.rwkv_url)
        self.container_url = _v1(o.container_url or o.rwkv_url)
        # The context budget rwkv-pi enforces (it never truncates input): the
        # checkpoint's trained context when its id states one (…-ctx34304).
        m = re.search(r'ctx(\d{4,6})', model)
        self.context_window = o.context_window or (int(m.group(1)) if m else 32768)
        if o.max_tokens >= self.context_window:
            raise ValueError('max_tokens must be smaller than the context window')
        if bool(o.adapter_version or o.adapter_scale is not None) and not o.adapter:
            raise ValueError('adapter_version / adapter_scale need --ak adapter=...')
        self.tools = ','.join(t.strip() for t in o.tools.split(',') if t.strip())
        self.thinking = o.reasoning_effort or 'high'
        self.provider_dir = Path(o.provider_dir or EVAL_ROOT.parent / 'rwkv-pi').resolve()
        self.pi_label = o.pi_label or _label(self.provider_dir)
        self.provider_commit = _commit(self.provider_dir)
        self.eval_commit = _commit(EVAL_ROOT)
        self.provider_env = {}
        if o.provider_env:
            p = Path(o.provider_env)
            self.provider_env = json.loads((p if p.is_absolute() else EVAL_ROOT / p).read_text())
            bad = [k for k in self.provider_env if not k.startswith('RWKV_')]
            if bad:
                raise ValueError(f'provider_env may only set RWKV_* variables, got {bad}')
        self.toolchain_sha256 = ''
        self.build = {}
        self._turn_no = 0      # user turns run so far (across Harbor multi-step steps)
        self._lines = 0        # session JSONL lines consumed so far

    @staticmethod
    def name() -> str:
        return 'pi-rwkv'

    def get_version_command(self) -> str | None:
        return f'{TOOLCHAIN}/bin/node --import {RESOLVER} {PI_CLI} --version'

    def version(self) -> str | None:
        # report.py parses these `key value` pairs; the full record is provenance.json.
        pi_ver = self.build.get('pi_version') or self._version or '-'
        return (f'pi {pi_ver}; rwkv-pi {self.provider_commit}; toolchain {self.pi_label}; eval {self.eval_commit}; '
                f'model {self.rwkv_model}; backend {self.rwkv_backend}; adapter {self.options.adapter or "-"}; '
                f'tools {self.tools}; thinking {self.thinking}; '
                f'provider_env {self.options.provider_env or "-"}; harbor {_harbor_version()}')

    # ---- environment of every Pi process -------------------------------------------------
    def _pi_env(self) -> dict[str, str]:
        o = self.options
        env = {**BASE_ENV,
               'RWKV_BACKEND': 'lightning', 'RWKV_TOOL_FORMAT': 'xml', 'RWKV_PROMPT_TEMPLATE': 'xml',
               'RWKV_BASE_URL': self.container_url, 'RWKV_MODEL': self.rwkv_model,
               'RWKV_API_KEY': self.api_key or 'rwkv-local',
               'RWKV_CONTEXT_WINDOW': str(self.context_window), 'RWKV_MAX_TOKENS': str(o.max_tokens),
               'RWKV_PI_PARITY': '1', 'RWKV_TOOLS': self.tools, 'RWKV_PLUGINS': 'none',
               'RWKV_ADAPTER_ID': o.adapter or '', 'RWKV_ADAPTER_VERSION': o.adapter_version or '',
               'RWKV_ADAPTER_SCALE': '' if o.adapter_scale is None else str(o.adapter_scale),
               'RAE_MAX_TURNS': str(o.max_steps or o.max_turns or 0)}
        if o.trace:
            env['RAE_TRACE_DIR'] = '/logs/agent/trace'
        env.update({k: str(v) for k, v in self.provider_env.items()})
        return env

    def _write_provenance(self) -> None:
        o = self.options
        record = {
            'harness': 'pi', 'model': self.rwkv_model, 'backend': self.rwkv_backend,
            'adapter': o.adapter, 'adapter_version': o.adapter_version, 'adapter_scale': o.adapter_scale,
            'endpoint': self.rwkv_url, 'container_endpoint': self.container_url, 'served_models': self.served,
            'max_steps': o.max_steps or o.max_turns, 'tools': self.tools, 'thinking': self.thinking,
            'context_window': self.context_window, 'max_tokens': o.max_tokens, 'settings': SETTINGS,
            'provider_env_path': o.provider_env, 'provider_env': self.provider_env,
            'toolchain_label': self.pi_label, 'toolchain_sha256': self.toolchain_sha256, 'toolchain_build': self.build,
            'toolchain_mounted': getattr(self, 'toolchain_mounted', False),
            'workspace_seeded': getattr(self, 'workspace_seeded', False),
            'web_archive_ignored': getattr(self, 'web_archive_ignored', False),
            'harbor_version': _harbor_version(),
            'provider': _checkout(self.provider_dir), 'eval': _checkout(EVAL_ROOT),
            'host': {'platform': platform.platform(), 'python': platform.python_version()},
        }
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.logs_dir / 'provenance.json').write_text(json.dumps(record, ensure_ascii=False, indent=1))

    # ---- install -----------------------------------------------------------------------
    async def install(self, environment: BaseEnvironment) -> None:
        arch = self.options.arch
        if not arch:
            res = await environment.exec(command='uname -m')
            arch = {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(res.stdout.strip(), res.stdout.strip())
        stem = EVAL_ROOT / '.cache' / f'rae-pi-{self.pi_label}-linux-{arch}'
        tgz, manifest = stem.with_suffix('.tar.gz'), stem.with_suffix('.json')
        if not tgz.exists():
            raise FileNotFoundError(f'{tgz} missing: run backends/pi/build-toolchain.sh (label {self.pi_label}, linux/{arch})')
        self.toolchain_sha256 = _sha256(tgz)
        self.build = json.loads(manifest.read_text()) if manifest.exists() else {}
        if self.build.get('tarball_sha256') not in (None, self.toolchain_sha256):
            raise RuntimeError(f'{manifest} does not describe {tgz.name} (sha256 differs): rebuild the toolchain')
        # glibc check first: the packed node is a glibc build (no Alpine/musl images).
        res = await self.exec_as_root(environment, command='(ldd --version 2>&1 || true) | head -1')
        if 'musl' in (res.stdout or '').lower():
            raise RuntimeError('task image is musl-based; the Pi toolchain needs glibc')
        res = await self.exec_as_root(environment, command=f'cat {TOOLCHAIN}/RAE_TOOLCHAIN 2>/dev/null || true')
        try:
            marker = json.loads(res.stdout or '')
        except json.JSONDecodeError:
            marker = {}
        want = {'label': self.pi_label, 'tarball_sha256': self.toolchain_sha256}
        self.toolchain_mounted = all(marker.get(k) == v for k, v in want.items())
        if marker and not self.toolchain_mounted:
            raise RuntimeError(f'{TOOLCHAIN} is mounted but stale ({marker} != {want}): rerun scripts/prepare-toolchain.sh pi')
        if not self.toolchain_mounted:
            remote = f'/tmp/{tgz.name}'
            await environment.upload_file(tgz, remote)
            await self.exec_as_root(environment, command=(
                f'mkdir -p /opt && tar --no-same-owner -xzf {remote} -C /opt && rm -f {remote} && chmod -R a+rX {TOOLCHAIN}'))
        # The engine must be reachable from inside the container (Pi runs there,
        # unlike Harbor's terminus-2): fail here, before any model turn.
        probe = ('const u=process.env.RWKV_BASE_URL+"/models";'
                 'fetch(u,{headers:{Authorization:"Bearer "+process.env.RWKV_API_KEY},signal:AbortSignal.timeout(15000)})'
                 '.then(r=>{console.log("rae-endpoint "+r.status);process.exit(r.ok?0:3)})'
                 '.catch(e=>{console.log("rae-endpoint "+e.message);process.exit(3)})')
        res = await environment.exec(command=f'{TOOLCHAIN}/bin/node -e {shlex.quote(probe)} || true',
                                     env={'RWKV_BASE_URL': self.container_url, 'RWKV_API_KEY': self.api_key or 'rwkv-local'})
        out = (res.stdout or '').strip()
        if 'rae-endpoint 200' not in out:
            raise RuntimeError(f'engine {self.container_url} not reachable from the task container ({out or "no output"}); '
                               'bind it to the docker bridge (e.g. --host 172.17.0.1) and pass --ak container_url=...')

    # ---- configure ---------------------------------------------------------------------
    async def setup(self, environment: BaseEnvironment) -> None:
        # Harbor 0.25.0 documents configure() but never calls it (same as backends/dsh).
        await super().setup(environment)
        await self.configure(environment)

    async def configure(self, environment: BaseEnvironment) -> None:
        if getattr(self, '_configured', False):
            return
        self._configured = True
        await self._seed_workspace(environment)
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / 'settings.json'
            settings.write_text(json.dumps(SETTINGS))
            await self.exec_as_root(environment, command=f'mkdir -p {PI_HOME}')
            await environment.upload_file(settings, f'{PI_HOME}/settings.json')
        owner = ''
        if environment.default_user is not None:
            owner = f' && chown -R {shlex.quote(str(environment.default_user))} /installed-agent'
        await self.exec_as_root(environment, command=f'chmod 644 {PI_HOME}/settings.json && mkdir -p {SESSIONS}{owner}')
        self._write_provenance()

    async def _seed_workspace(self, environment: BaseEnvironment) -> None:
        """Same as DshRwkv._seed_workspace: tasks on the shared prebuilt image start with an empty /app."""
        self.workspace_seeded = False
        workspace = Path(environment.environment_dir) / 'workspace'
        if environment.task_env_config.docker_image != BASE_IMAGE or not workspace.is_dir():
            return
        res = await self.exec_as_root(environment, command='ls -A /app 2>/dev/null | head -1 || true')
        if (res.stdout or '').strip():
            return
        await environment.upload_dir(workspace, '/app')
        self.workspace_seeded = True

    # ---- run ---------------------------------------------------------------------------
    def _pi_command(self, text: str, resume: bool) -> str:
        preload = ['--import', RESOLVER] + (['--import', f'{TOOLCHAIN}/trace.mjs'] if self.options.trace else [])
        args = [f'{TOOLCHAIN}/bin/node', *preload, PI_CLI,
                # rwkv-pi src/cli.ts: explicit extensions only, provider rwkv, thinking high, tool allowlist,
                # parity flags. Plus the eval's prompt-neutral turn budget.
                '--no-extensions', '--extension', f'{TOOLCHAIN}/dist/extension.js', '--extension', f'{TOOLCHAIN}/budget.mjs',
                '--provider', 'rwkv', '--model', self.rwkv_model, '--thinking', self.thinking,
                '--tools', self.tools, '--no-skills', '--no-context-files', '--no-prompt-templates',
                '--offline', '--print', '--mode', 'json', '--session-dir', SESSIONS]
        if resume:
            args.append('--continue')
        return shlex.join(args + [text])

    @with_prompt_template
    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        env_dir = Path(environment.environment_dir)
        shipped = {name: (env_dir / name).read_text() for name in ('turns.json', 'web.json') if (env_dir / name).is_file()}
        # Pi has no web tools in its training allowlist: an archive cannot be served. Recorded, not hidden.
        self.web_archive_ignored = bool(shipped.get('web.json', '').strip() not in ('', '{}'))
        await self.exec_as_root(environment, command='rm -rf /rae')
        try:
            turns = [str(t) for t in json.loads(shipped.get('turns.json', ''))] or [instruction]
        except (json.JSONDecodeError, TypeError):
            turns = [instruction]
        # A Harbor multi-step step (self._resume) continues the session the earlier step started.
        if self._resume:
            self._session_usage_start = await self._session_positions(environment)
        env = self._pi_env()
        statuses = []
        first = self._turn_no + 1
        for i, text in enumerate(turns):
            n = self._turn_no = self._turn_no + 1
            resume = self._resume or i > 0
            res = await self.exec_as_agent(environment, env=env, command=(
                f'{self._pi_command(text, resume)} < /dev/null 2> /logs/agent/stderr-{n}.txt '
                f'| grep -v \'"type":"message_update"\' > /logs/agent/pi-{n}.txt; status=${{PIPESTATUS[0]}}; '
                f'{TOOLCHAIN}/bin/node {TOOLCHAIN}/turn.mjs {n} {SESSIONS} {self._lines}; echo "rae-status $status"'))
            out = res.stdout or ''
            statuses.append(int(out.rsplit('rae-status ', 1)[1].split()[0]) if 'rae-status ' in out else 1)
            if 'rae-lines ' in out:
                self._lines = int(out.rsplit('rae-lines ', 1)[1].split()[0])
            session = (await self.exec_as_agent(environment, command=f'cat /logs/agent/session-{n}.txt 2>/dev/null || true')).stdout.strip()
            if not session:
                break  # nothing to continue: later turns would start from scratch
        res = await self.exec_as_root(environment, command="awk '/^oom_kill /{print $2}' /sys/fs/cgroup/memory.events 2>/dev/null || true")
        try:
            oom_kills = int((res.stdout or '').strip() or 0)
        except ValueError:
            oom_kills = 0
        last = self._turn_no
        summary = {'turns': len(turns), 'ran': len(statuses), 'first_turn': first, 'status': statuses,
                   'oom_kills': oom_kills, 'web_archive_ignored': self.web_archive_ignored}
        self._write_provenance()
        await self.exec_as_agent(environment, command=(
            f'cp /logs/agent/final-{last}.txt /logs/agent/final.txt 2>/dev/null || : > /logs/agent/final.txt; '
            f'cat $(ls /logs/agent/events-*.jsonl | sort -t- -k2 -n) > /logs/agent/events.jsonl; '
            f'cp {PI_HOME}/settings.json /logs/agent/pi-settings.json 2>/dev/null; '
            # Harbor's Pi fallback token count reads pi.txt (all turns' JSON streams).
            f'cat $(ls /logs/agent/pi-*.txt | sort -t- -k2 -n) > /logs/agent/pi.txt 2>/dev/null; '
            f'printf %s {shlex.quote(json.dumps(summary))} > /logs/agent/turns.json; '
            f'exit {next((x for x in statuses if x), 0)}'))

    def populate_context_post_run(self, context: AgentContext) -> None:
        # Pi's own converter: ATIF trajectory.json + token accounting from the session JSONL.
        super().populate_context_post_run(context)
        self._recover_contract()

    def _recover_contract(self) -> None:
        """When Harbor's agent timeout kills the run mid-turn, turn.mjs never runs:
        rebuild events.jsonl / final.txt / turns.json on the host from the session
        log Harbor already copied out, so the trial still has the contract files
        (marked recovered_after_kill) instead of looking like it never started."""
        logs = self.logs_dir
        if (logs / 'events.jsonl').exists():
            return
        sessions = sorted((logs / self._SESSIONS_DIRECTORY).glob('*.jsonl'), key=lambda p: (p.stat().st_mtime_ns, p.name))
        if not sessions:
            return
        lines = [l for l in sessions[-1].read_text(errors='replace').splitlines() if l.strip()]
        events, final = convert_session(lines, self._lines)
        n = self._turn_no or 1
        try:
            (logs / f'events-{n}.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events))
            (logs / 'events.jsonl').write_text(''.join(
                p.read_text() for p in sorted(logs.glob('events-*.jsonl'), key=lambda p: int(p.stem.split('-')[1]))))
            (logs / f'final-{n}.txt').write_text(final)
            (logs / 'final.txt').write_text(final)
            if not (logs / 'turns.json').exists():
                (logs / 'turns.json').write_text(json.dumps({'turns': None, 'ran': n, 'status': ['killed'], 'recovered_after_kill': True}))
        except OSError as exc:
            self.logger.debug(f'could not recover Pi contract files: {exc}')


# Same mapping as backends/pi/turn.mjs convert() (kept in step by backends/pi/test/test_convert.py).
_KIND = {'stop': 'completed', 'toolUse': 'completed', 'length': 'max_tokens', 'aborted': 'aborted', 'error': 'error'}


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    return ''.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text' and isinstance(b.get('text'), str))


def convert_session(lines: list[str], start: int = 0) -> tuple[list[dict], str]:
    events, session_id, cwd, last_text, last_stop, last_error = [], '', '', '', '', ''
    for index, line in enumerate(lines):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(e, dict):
            continue
        if e.get('type') == 'session':
            session_id, cwd = e.get('id') or session_id, e.get('cwd') or cwd
            continue
        m = e.get('message')
        if index < start or e.get('type') != 'message' or not isinstance(m, dict):
            continue
        if m.get('role') == 'assistant':
            for b in m.get('content') if isinstance(m.get('content'), list) else []:
                if b.get('type') == 'thinking' and b.get('thinking'):
                    events.append({'type': 'reasoning', 'text': b['thinking']})
                elif b.get('type') == 'text' and b.get('text'):
                    events.append({'type': 'text', 'text': b['text']})
                elif b.get('type') == 'toolCall':
                    events.append({'type': 'tool_call', 'callId': b.get('id'), 'tool': b.get('name'), 'input': b.get('arguments') or {}})
            u = m.get('usage') or {}
            inp = (u.get('input') or 0) + (u.get('cacheRead') or 0) + (u.get('cacheWrite') or 0)
            events.append({'type': 'status', 'phase': 'step_end', 'stopReason': m.get('stopReason'),
                           'usage': {'inputTokens': inp, 'outputTokens': u.get('output') or 0,
                                     'totalTokens': u.get('totalTokens') or inp + (u.get('output') or 0)}})
            t = _text(m.get('content')).strip()
            last_text = t or last_text
            last_stop = m.get('stopReason') or last_stop
            last_error = m.get('errorMessage') or last_error
        elif m.get('role') == 'toolResult':
            events.append({'type': 'tool_result', 'callId': m.get('toolCallId'), 'tool': m.get('toolName'),
                           'status': 'error' if m.get('isError') else 'completed', 'result': _text(m.get('content'))})
        elif m.get('role') == 'user':
            events.append({'type': 'user', 'text': _text(m.get('content'))})
    reason = {'kind': _KIND.get(last_stop) or last_stop or 'no_reply'}
    if last_error:
        reason['error'] = last_error
    return ([{'type': 'session', 'sessionId': session_id, 'cwd': cwd}, *events,
             {'type': 'final', 'sessionId': session_id, 'reason': reason, 'text': last_text}], last_text)
