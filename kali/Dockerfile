FROM kalilinux/kali-rolling

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY chisel /usr/local/bin/chisel
RUN chmod +x /usr/local/bin/chisel

RUN apt update && \
    apt install -y \
        openssh-server \
        nmap \
        curl \
        telnet \
        proxychains4 \
        ffuf \
        ftp \
        nano \
        vim \
        iproute2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "root:root" | chpasswd && \
    mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
