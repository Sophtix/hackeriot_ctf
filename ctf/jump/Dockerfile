FROM debian:bookworm-slim

ARG JUMP_ROOT_PASSWORD

COPY chisel /usr/local/bin/chisel
RUN chmod +x /usr/local/bin/chisel

RUN apt-get update && \
    apt-get install -y openssh-server && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

RUN echo "root:${JUMP_ROOT_PASSWORD}" | chpasswd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
