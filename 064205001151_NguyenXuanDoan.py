# tcp_opt_example.py
# Demonstrates: TCP_NODELAY, set buffer sizes, non-blocking, and (Linux) TCP_CONGESTION if available.
# Run: python3 tcp_opt_example.py

import socket
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Disable Nagle
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Increase buffers
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)

# Non-blocking
s.setblocking(False)

# Try to set congestion control on Linux (may raise AttributeError or OSError)
try:
    TCP_CONGESTION = getattr(socket, 'TCP_CONGESTION', None)
    if TCP_CONGESTION is not None:
        s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, b'cubic')
except Exception as e:
    print("Setting TCP_CONGESTION failed or not supported:", e)

print("Socket configured (non-blocking, TCP_NODELAY, large buffers).")
s.close()
