1. Gets IP address of DMZ
2. Scan DMZ for open ports and sees ssh
3. Connect to DMZ via SSH with root:toor
4. Check network adapters of DMZ and see the internal dmz_jump_segment
5. Scan internal segment using nmap and identify port 8080 in DMZ and 23 in jump
6. Attempt to connect to jump via telnet unsuccessfully
7. Local port forward form DMZ 8080 to localhost 80 using ssh -L 8080:localhost:8080 root@localhost -p 2200
8. Access the web application on DMZ via localhost:80 and identify the password for telnet
9. Use the identified password to connect to the jump server via telnet
