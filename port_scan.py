
import socket
import sys

target = "31.97.117.123"
ports = [80, 443, 8080, 8443, 3000, 5000, 5432, 3306, 22, 21, 25, 110, 143, 3306, 5900, 27017]

for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"[+] Port {port} is OPEN")
        sock.close()
    except Exception as e:
        pass

