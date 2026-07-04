# =============================================================================
# SuperNinja Sandbox - FULL Replica Development Environment
# Exact replica of the NinjaTech AI agent sandbox for use in VS Code
# Base: Debian 12 (bookworm) + Python 3.11 + Node.js 20.x
# =============================================================================

FROM python:3.11-slim-bookworm

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color
ENV DISPLAY=:0

# =============================================================================
# PHASE 1: Core system packages (matching real sandbox)
# =============================================================================
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
    mawk \
    diffutils \
    patch \
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
    # Archive tools
    zip \
    unzip \
    bzip2 \
    gzip \
    xz-utils \
    tar \
    rsync \
    # Terminal & editor
    tmux \
    vim \
    tree \
    less \
    # Process & system management
    procps \
    htop \
    lsof \
    psmisc \
    supervisor \
    # Networking
    openssh-client \
    openssh-server \
    netcat-traditional \
    net-tools \
    dnsutils \
    iputils-ping \
    curl \
    # Web server
    nginx \
    # OCR (like real sandbox)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    # Graphics & fonts (matching real sandbox)
    fontconfig \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-wqy-zenhei \
    # X11 / Virtual display (like real sandbox for browser automation)
    xvfb \
    x11vnc \
    xauth \
    x11-utils \
    x11-xkb-utils \
    xdg-utils \
    # Python system packages (matching real sandbox)
    python3-agate \
    python3-bs4 \
    python3-lxml \
    python3-numpy \
    python3-pil \
    python3-pygments \
    python3-pytest \
    python3-sqlalchemy \
    python3-tz \
    python3-requests \
    # Misc
    trash-cli \
    xxd \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# PHASE 2: Node.js 20.x (matching real sandbox)
# =============================================================================
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@latest

# =============================================================================
# PHASE 3: Python packages - EXACT match with real SuperNinja sandbox
# =============================================================================
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && pip3 install --no-cache-dir \
    # === Web & API frameworks ===
    fastapi \
    starlette \
    uvicorn \
    httpx \
    httpx-sse \
    sse-starlette \
    python-multipart \
    # === Data validation & settings ===
    pydantic \
    pydantic_core \
    pydantic-settings \
    annotated-types \
    # === MCP (Model Context Protocol) ===
    mcp \
    # === Markdown processing ===
    markdown-it-py \
    mdurl \
    # === Cryptography & auth ===
    cryptography \
    cffi \
    pycparser \
    PyJWT \
    # === HTTP & networking ===
    certifi \
    charset-normalizer \
    idna \
    h11 \
    httpcore \
    requests \
    urllib3 \
    # === Async & concurrency ===
    anyio \
    greenlet \
    tenacity \
    # === Data formats & schemas ===
    jsonschema \
    jsonschema-specifications \
    referencing \
    rpds-py \
    # === CLI & terminal ===
    click \
    rich \
    argcomplete \
    # === Process & system ===
    pexpect \
    ptyprocess \
    # === File & path ===
    platformdirs \
    userpath \
    packaging \
    # === Typing ===
    typing_extensions \
    typing-inspection \
    # === Configuration ===
    python-dotenv \
    # === Image processing ===
    pillow \
    pytesseract \
    # === Browser automation (like real sandbox) ===
    playwright \
    pyee \
    # === GUI automation (like real sandbox) ===
    PyAutoGUI \
    MouseInfo \
    PyGetWindow \
    PyMsgBox \
    PyRect \
    PyScreeze \
    pytweening \
    pyperclip \
    python3-xlib \
    # === Code analysis ===
    Pygments \
    bashlex \
    # === SWE / Agent tools (like real sandbox) ===
    swe-rex \
    # === Misc ===
    attrs \
    jaraco.context \
    backports.tarfile \
    annotated-doc \
    pipx

# Install Playwright browsers (like real sandbox)
RUN playwright install chromium && playwright install-deps chromium

# =============================================================================
# PHASE 4: Global Node.js tools
# =============================================================================
RUN npm install -g \
    typescript \
    ts-node \
    pm2 \
    serve \
    nodemon \
    corepack

# =============================================================================
# PHASE 5: GitHub CLI (like real sandbox)
# =============================================================================
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# PHASE 6: Create user & workspace (matching real sandbox)
# =============================================================================
ARG USERNAME=superninja
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} -s /bin/bash \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

RUN mkdir -p /workspace && chown -R ${USERNAME}:${USERNAME} /workspace

# =============================================================================
# PHASE 7: Shell & environment setup
# =============================================================================
RUN echo 'export PS1="\[\033[01;32m\]🥷 superninja\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/${USERNAME}/.bashrc \
    && echo 'export PATH="/usr/local/bin:$PATH"' >> /home/${USERNAME}/.bashrc \
    && echo 'export DISPLAY=:0' >> /home/${USERNAME}/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias la="ls -A"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias gs="git status"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias gp="git push"' >> /home/${USERNAME}/.bashrc

# =============================================================================
# PHASE 8: Supervisor config for Xvfb + VNC (like real sandbox)
# =============================================================================
RUN mkdir -p /var/log/supervisor && \
    echo '[supervisord]\nnodaemon=false\nlogfile=/var/log/supervisor/supervisord.log\npidfile=/var/run/supervisord.pid\n\n[program:xvfb]\ncommand=Xvfb :0 -screen 0 1280x720x24\nautorestart=true\npriority=10\n\n[program:x11vnc]\ncommand=x11vnc -display :0 -forever -nopw -shared\nautorestart=true\npriority=20' > /etc/supervisor/conf.d/superninja.conf

# =============================================================================
# Health check
# =============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD echo "SuperNinja sandbox alive" || exit 1

# Switch to non-root user
USER ${USERNAME}
WORKDIR /workspace

CMD ["/bin/bash"]
