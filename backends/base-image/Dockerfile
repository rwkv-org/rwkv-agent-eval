# Shared image for bank tasks (bank/prebuilt.py): what every per-task image
# was before the workspace COPY. Tasks name it in task.toml [environment]
# docker_image, Harbor starts it without a build, and the agent copies the
# task's environment/workspace into /app (backends/dsh/harbor_agent.py).
FROM python:3.12-slim
WORKDIR /app
