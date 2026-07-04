# =============================================================================
# SuperNinja Sandbox - COMPLETE Replica Development Environment
# Exact replica of the NinjaTech AI agent sandbox for use in VS Code
# Base: Debian 12 (bookworm) + Python 3.11 + Node.js 20.x
# =============================================================================

FROM python:3.11-slim-bookworm

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color
ENV DISPLAY=:99
ENV CHROME_DEBUGGING_PORT=9222
ENV CHROME_DEBUGGING_HOST=localhost
ENV CHROME_PERSISTENT_SESSION=true

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
    # Web server
    nginx \
    # OCR (like real sandbox)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    # Graphics & fonts (matching real sandbox)
    fontconfig \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-freefont-ttf \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-wqy-zenhei \
    fonts-ipafont-gothic \
    # X11 / Virtual display (like real sandbox for browser automation)
    xvfb \
    x11vnc \
    tigervnc-tools \
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
    python3-openpyxl \
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
    && npm install -g npm@latest corepack

# =============================================================================
# PHASE 3: code-server (VS Code in browser - like real sandbox)
# =============================================================================
RUN curl -fsSL https://code-server.dev/install.sh | sh

# =============================================================================
# PHASE 4: ttyd (web terminal - like real sandbox)
# =============================================================================
RUN curl -fsSL https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64 -o /usr/local/bin/ttyd \
    && chmod +x /usr/local/bin/ttyd

# =============================================================================
# PHASE 5: noVNC (browser VNC access - like real sandbox)
# =============================================================================
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone --depth 1 https://github.com/novnc/websockify.git /opt/novnc/utils/websockify \
    && rm -rf /opt/novnc/.git /opt/novnc/utils/websockify/.git

# =============================================================================
# PHASE 6: Python packages - EXACT match with real SuperNinja sandbox
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
    # === Extra data science (bonus!) ===
    pandas \
    numpy \
    matplotlib \
    beautifulsoup4 \
    lxml \
    pyyaml \
    toml \
    # === Misc ===
    attrs \
    jaraco.context \
    backports.tarfile \
    annotated-doc \
    pipx \
    aiofiles

# Install Playwright browsers (like real sandbox)
RUN playwright install chromium && playwright install-deps chromium

# =============================================================================
# PHASE 7: Global Node.js tools (bonus - more than real sandbox)
# =============================================================================
RUN npm install -g \
    typescript \
    ts-node \
    pm2 \
    serve \
    nodemon

# =============================================================================
# PHASE 8: GitHub CLI (like real sandbox)
# =============================================================================
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# PHASE 9: Create user & workspace (matching real sandbox)
# =============================================================================
ARG USERNAME=superninja
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} -s /bin/bash \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

RUN mkdir -p /workspace /app /var/log/supervisor && chown -R ${USERNAME}:${USERNAME} /workspace

# =============================================================================
# PHASE 10: Supervisor config - FULL (matching real sandbox)
# =============================================================================
RUN mkdir -p /var/log/supervisor /root/.vnc && \
    echo '[unix_http_server]\nfile=/var/run/supervisor.sock\nchmod=0700\n\n[rpcinterface:supervisor]\nsupervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\n[supervisorctl]\nserverurl=unix:///var/run/supervisor.sock\n\n[supervisord]\nuser=root\nnodaemon=false\nlogfile=/var/log/supervisor/supervisord.log\nchildlogdir=/var/log/supervisor\npidfile=/var/run/supervisord.pid\nloglevel=debug\nenvironment=DISPLAY=":99",CHROME_DEBUGGING_PORT="9222",CHROME_DEBUGGING_HOST="localhost",CHROME_PERSISTENT_SESSION="true"\n\n[program:xvfb]\ncommand=Xvfb :99 -screen 0 1600x900x24 -ac +extension GLX +render -noreset\nautorestart=true\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\npriority=100\nstartsecs=3\nstopsignal=TERM\nstopwaitsecs=10\n\n[program:vnc_setup]\ncommand=bash -c "VNC_UUID=$(cat /proc/sys/kernel/random/uuid) && mkdir -p ~/.vnc && echo $VNC_UUID | vncpasswd -f > ~/.vnc/passwd && chmod 600 ~/.vnc/passwd && echo $VNC_UUID > ~/.vnc/password.txt"\nautorestart=false\nstartsecs=0\npriority=150\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\n\n[program:x11vnc]\ncommand=bash -c "sleep 3 && DISPLAY=:99 x11vnc -display :99 -forever -shared -rfbport 5901 -o /var/log/x11vnc.log"\nautorestart=true\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\npriority=200\nstartretries=10\nstartsecs=10\nstopsignal=TERM\nstopwaitsecs=10\ndepends_on=vnc_setup,xvfb\n\n[program:novnc]\ncommand=bash -c "sleep 5 && cd /opt/novnc && ./utils/novnc_proxy --vnc localhost:5901 --listen 0.0.0.0:6080 --web /opt/novnc"\nautorestart=true\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\npriority=300\nstartretries=5\nstartsecs=3\ndepends_on=x11vnc\n\n[program:nginx]\ncommand=/usr/sbin/nginx -g daemon off;\nautostart=true\nautorestart=false\nstartsecs=0\npriority=350\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\n\n[program:ttyd]\ncommand=/usr/local/bin/ttyd -p 2222 /bin/bash\nautorestart=true\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\npriority=450\nstartsecs=5\n\n[program:code_server]\ncommand=/usr/bin/code-server --bind-addr 0.0.0.0:4000 --auth none --user-data-dir /opt/code-server --extensions-dir /opt/code-server/extensions\nautorestart=true\nstdout_logfile=/dev/null\nstderr_logfile=/dev/null\npriority=500\nstartsecs=5' > /etc/supervisor/supervisord.conf

# =============================================================================
# PHASE 11: Shell & environment setup
# =============================================================================
RUN echo 'export PS1="\[\033[01;32m\]🥷 superninja\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/${USERNAME}/.bashrc \
    && echo 'export PATH="/usr/local/bin:$PATH"' >> /home/${USERNAME}/.bashrc \
    && echo 'export DISPLAY=:99' >> /home/${USERNAME}/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias la="ls -A"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias gs="git status"' >> /home/${USERNAME}/.bashrc \
    && echo 'alias gp="git push"' >> /home/${USERNAME}/.bashrc

# =============================================================================
# PHASE 12: Nginx config for proxy (like real sandbox)
# =============================================================================
RUN echo 'server {\n    listen 8080;\n    server_name localhost;\n\n    location /vnc/ {\n        proxy_pass http://localhost:6080/;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection "upgrade";\n        proxy_set_header Host $host;\n    }\n\n    location /terminal/ {\n        proxy_pass http://localhost:2222/;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection "upgrade";\n        proxy_set_header Host $host;\n    }\n\n    location /code/ {\n        proxy_pass http://localhost:4000/;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection "upgrade";\n        proxy_set_header Host $host;\n        proxy_set_header Accept-Encoding "";\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Host $host;\n    }\n}' > /etc/nginx/sites-available/superninja \
    && ln -sf /etc/nginx/sites-available/superninja /etc/nginx/sites-enabled/superninja \
    && rm -f /etc/nginx/sites-enabled/default

# =============================================================================
# Health check
# =============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Expose all service ports
EXPOSE 2222 3000 4000 5000 5901 6080 8000 8080 8888 11434

# Switch to non-root user
USER ${USERNAME}
WORKDIR /workspace

CMD ["sudo", "supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
