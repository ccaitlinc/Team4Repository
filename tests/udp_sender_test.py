import socket

SOURCE_IP = "127.0.0.1"       #  local interface
PORT = 7500
TARGET_IP = "127.0.0.1"  

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow broadcasting
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print(f"Broadcasting from {SOURCE_IP} to {TARGET_IP}:{PORT}")
print("Type an equipment ID and press Enter (Ctrl+C to quit)")

while True:
    try:
        message = input("Equipment ID: ")
        sock.sendto(message.encode(), (TARGET_IP, PORT))
        print("Sent:", message)
    except KeyboardInterrupt:
        print("\nShutting down.")
        break

sock.close()