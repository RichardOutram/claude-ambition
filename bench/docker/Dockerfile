# The machine each bench run works in: a normal dev box Claude can use freely,
# with a browser it can drive, but nothing of yours on it. Both arms use it.
FROM mcr.microsoft.com/playwright:v1.52.0-noble
ARG CLAUDE_VERSION=2.1.322
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv git ripgrep \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g @anthropic-ai/claude-code@${CLAUDE_VERSION} \
 && mkdir -p /work /cfg /plugin && chown pwuser /work /cfg
USER pwuser
ENV HOME=/home/pwuser CLAUDE_CONFIG_DIR=/cfg
WORKDIR /work
