"""DSH + dsh-rwkv-plugin as a Harbor installed agent (`environment = "docker"` tasks).

    PYTHONPATH=. harbor run -p tasks/<task> -a backends.dsh.harbor_agent:DshRwkv \
        --ak rwkv_url=http://host:8000 --ak rwkv_model=rwkv7-g1l-7.2b \
        [--ak plugin_dir=../dsh-rwkv-plugin] [--ak dsh_version=0.2.1-rc.5] [--ak max_steps=12]

No network install inside the task container:
  install()    uploads .cache/rae-node-<dsh>-linux-<arch>.tar.gz (Node + DSH +
               pnpm, built by backends/dsh/build-toolchain.sh) to /opt/rae-node.
  configure()  uploads the local plugin checkout (every trial, so the run
               records exactly that commit) and adds it to the headless profile
               with `dsh plugin add`, the same path a user install takes.
  run()        the plugin's scripts/headless.ts --installed, the entry the
               workspace runner uses too. Events go to /logs/agent/events.jsonl,
               the final message to /logs/agent/final.txt (graded by answer tasks).

The task image needs glibc (Debian/Ubuntu based) and must reach the endpoint.
"""
import io
import json
import shlex
import subprocess
import tarfile
import tempfile
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


class DshRwkv(BaseInstalledAgent):
    def __init__(self, logs_dir: Path, rwkv_url: str = "", rwkv_model: str = '', rwkv_backend: str = 'irwkv',
                 plugin_dir: str = '', dsh_version: str = '0.2.1-rc.5', arch: str = '',
                 max_steps: int | str | None = None, adapter: str | None = None, **kwargs):
        super().__init__(logs_dir, **kwargs)
        if not rwkv_url or not rwkv_model:
            raise ValueError('DshRwkv needs --ak rwkv_url=... and --ak rwkv_model=...')
        self.rwkv_url, self.rwkv_model, self.rwkv_backend = rwkv_url, rwkv_model, rwkv_backend
        self.plugin_dir = Path(plugin_dir or EVAL_ROOT.parent / 'dsh-rwkv-plugin').resolve()
        self.dsh_version, self.arch = dsh_version, arch
        self.max_steps, self.adapter = max_steps, adapter
        self.plugin_commit = _git(self.plugin_dir, 'rev-parse', '--short', 'HEAD') + (
            '*' if _git(self.plugin_dir, 'status', '--porcelain') else '')

    @staticmethod
    def name() -> str:
        return 'dsh-rwkv'

    def version(self) -> str | None:
        # Shown in Harbor's result.json; the model endpoint is in model_name/kwargs.
        return f'dsh {self.dsh_version}; plugin {self.plugin_commit}'

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
