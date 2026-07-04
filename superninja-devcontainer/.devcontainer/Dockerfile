# =============================================================================
# SuperNinja Sandbox - Full Development Environment
# Replicates the NinjaTech AI agent sandbox for use in VS Code
# Base: Debian 12 (bookworm) + Python 3.11 + Node.js 20.x
# =============================================================================

FROM python:3.11-slim-bookworm

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color

# ---- System packages & core tools ----
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    ca-certificates \
    curl \
    wget \
    git \
    sudo \
    gnupg \
    # Text processing
    grep \
    gawk \
    sed \
    # File analysis & data processing
    file \
    jq \
    csvkit \
    xmlstarlet \
    # PDF processing
    poppler-utils \
    wkhtmltopdf \
    # Document processing
    antiword \
    unrtf \
    catdoc \
    # Utilities
    tmux \
    vim \
    tree \
    rsync \
    zip \
    unzip \
    # SSH & networking
    openssh-client \
    netcat-openbsd \
    # Process management
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# ---- Node.js 20.x ----
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@latest

# ---- Python packages (matching SuperNinja sandbox) ----
RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir \
    # Web & API
    fastapi \
    httpx \
    httpx-sse \
    # Data & validation
    pydantic \
    annotated-types \
    # MCP (Model Context Protocol)
    mcp \
    # Markdown
    markdown-it-py \
    # Crypto
    cryptography \
    # General utilities
    click \
    rich \
    # JSON Schema
    jsonschema \
    # File handling
    python-multipart \
    aiofiles \
    # Async
    anyio \
    greenlet \
    # Processing
    attrs \
    packaging \
    pexpect \
    # HTTP
    certifi \
    charset-normalizer \
    idna \
    h11 \
    httpcore

# ---- Additional useful Python tools ----
RUN pip3 install --no-cache-dir \
    # Data science
    pandas \
    numpy \
    matplotlib \
    # PDF generation
    weasyprint \
    # YAML/TOML
    pyyaml \
    toml \
    # Requests (classic)
    requests \
    # BeautifulSoup for scraping
    beautifulsoup4 \
    lxml

# ---- Global Node.js tools ----
RUN npm install -g \
    typescript \
    ts-node \
    pm2 \
    serve \
    nodemon

# ---- Create non-root user (like SuperNinja sandbox) ----
ARG USERNAME=superninja
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} -s /bin/bash \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# ---- Set up workspace ----
RUN mkdir -p /workspace && chown -R ${USERNAME}:${USERNAME} /workspace

# ---- Shell enhancements ----
RUN echo 'export PS1="\[\033[01;32m\]🥷 superninja\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/${USERNAME}/.bashrc \
    && echo 'export PATH="/usr/local/bin:$PATH"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias la="ls -A"' >> /home/${USERNAME}/.bashrc

# ---- Health check ----
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD echo "SuperNinja sandbox alive" || exit 1

# Switch to non-root user
USER ${USERNAME}
WORKDIR /workspace

CMD ["/bin/bash"]
