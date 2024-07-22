FROM kathara/base

RUN pip3 install --break-system-packages marshmallow \
    && mkdir /agent \
    && mkfifo /agent{in,out}
