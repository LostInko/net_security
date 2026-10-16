import socket

def send_msg(host="0.0.0.0", port= 9001):

    # Create socket and connect as client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host,port))

        # Send mess
        client.sendall(b"PING ECHO\n")

        response = client.recv(1024)
        print(f"Response from server: {response.decode('utf-8').strip()}")

if __name__ == "__main__":
    send_msg()

    