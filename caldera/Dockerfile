FROM kathara/base

RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - \
    && apt install nodejs -y \
    && apt clean \
    && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp \
    && git clone https://github.com/mitre/caldera.git --recursive \
    && cd caldera \
    && pip3 install --break-system-packages -r requirements.txt \
    && cd ./plugins/magma \
    && npm install \
    && npm run build
