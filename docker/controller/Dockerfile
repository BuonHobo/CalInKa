FROM kathara/base

# This installs nodejs,
# clones the caldera repo,
# installs the python requirements,
# and builds the magma plugin which is needed for the web UI to work
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - \
    && apt install nodejs nmap -y \
    && apt clean \
    && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp \
    && git clone https://github.com/mitre/caldera.git --recursive \
    && cd caldera \
    && pip3 install --break-system-packages -r requirements.txt \
    && cd ./plugins \
    && git clone https://github.com/center-for-threat-informed-defense/caldera_pathfinder.git pathfinder --recursive \
    && cd ./pathfinder \
    && pip3 install --break-system-packages -r requirements.txt \
    && cd /caldera/plugins/magma \
    && npm install \
    && npm run build
