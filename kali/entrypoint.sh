#!/bin/bash
set -e

# Start SSH server
exec /usr/sbin/sshd -D
