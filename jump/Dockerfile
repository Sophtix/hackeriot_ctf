FROM debian:bookworm-slim

ARG JUMP_ROOT_PASSWORD
ARG SECURE_ROOT_PASSWORD

RUN echo "root:${JUMP_ROOT_PASSWORD}" | chpasswd

COPY chisel /usr/local/bin/chisel
RUN chmod +x /usr/local/bin/chisel

RUN apt-get update && \
    apt-get install -y openbsd-inetd supervisor telnetd login bash iproute2 python3 vsftpd && \
    mkdir -p /var/run/vsftpd/empty && \
    rm -rf /var/lib/apt/lists/*
    
COPY vsftpd.conf /etc/vsftpd.conf
RUN mkdir -p /shared && \
    chmod -R 755 /shared && \
    echo "username,password,host" > /shared/passwords.csv && \
    echo "root,$JUMP_ROOT_PASSWORD,jump.local" >> /shared/passwords.csv

COPY server.py /app/server.py

RUN printf "telnet stream tcp nowait root /usr/sbin/telnetd telnetd\n" >> /etc/inetd.conf

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN sed -i 's/{{SECURE_ROOT_PASSWORD}}/"'"$SECURE_ROOT_PASSWORD"'"/' /etc/supervisor/conf.d/supervisord.conf

EXPOSE 23
EXPOSE 21
EXPOSE 30000-30009

CMD ["/usr/bin/supervisord", "-n"]
