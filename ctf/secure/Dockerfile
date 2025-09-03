FROM debian:bookworm-slim

ARG SECURE_FLAG
ARG SECURE_ROOT_PASSWORD


COPY chisel /usr/local/bin/chisel
RUN chmod +x /usr/local/bin/chisel

RUN apt-get update && \
    apt-get install -y \
    iproute2 \
    openssh-server \
    python3 && \
    apt-get clean && \
    echo "root:$SECURE_ROOT_PASSWORD" | chpasswd && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

COPY server.py /app/server.py

WORKDIR /app



EXPOSE 22

ENTRYPOINT ["sh", "-c", "/usr/sbin/sshd && python3 server.py $SECURE_FLAG"]
