import socket

# Settings
DEFAULT_NETWORK_ADDRESS = "127.0.0.1" 
BROADCAST_PORT = 7500                  
RECEIVE_PORT = 7501                   
BUFFER_SIZE = 4096



def is_valid_address(address):
    parts = address.split(".")  # will split the address into 4 parts
    if len(parts) != 4:     # will make sure the address only has 4 parts 
        return False
    for part in parts:
        if not part.isdigit() or int(part) > 255:
            return False
    return True

network_address = DEFAULT_NETWORK_ADDRESS


# Sending socket
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow broadcasting 
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def set_network_address(new_address):
    # Switch to a different network address
    global network_address

    new_address = new_address.strip()
    if not is_valid_address(new_address):
        print(f"Invalid network address: {new_address}")
        return False

    network_address = new_address
    print(f"Network address changed to {network_address}")
    return True


def broadcast(code):
    # Send one integer through port 7500
    try:
        message = str(int(code))    #turning the number 12 into text 
    except ValueError:
        print(f"Not sending '{code}': transmissions must be a single integer")
        return False

    try:
        send_sock.sendto(message.encode(), (network_address, BROADCAST_PORT))   #.encode() is changing texts into bytes
        print(f"Sent: {message} to {network_address}:{BROADCAST_PORT}")
        return True
    except OSError as error:
        print(f"Could not send {message}: {error}")
        return False