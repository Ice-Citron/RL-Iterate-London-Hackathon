
import socket

target = "31.97.117.123"
# Extended port list
ports = list(range(1, 1001)) + [3000, 5000, 8000, 8080, 8888, 9000, 9090, 27017, 5432, 3306]

open_ports = []
for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    except:
        pass

print("[*] Open Ports Found:")
for port in sorted(open_ports):
    print(f"    Port {port}")

