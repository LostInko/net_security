import socket
import threading

# Shared dictionary for the SET
store = {}

def handle_client(conn, address):
    print(f"Connection from {address}")
    with conn:
        # Buffer to aggregate all of incoming bytes until a \n arrives
        buffer = b""                                    
    
        while True:
            # Receive up to 1024
            data = conn.recv(1024)

            # Close the conn if recv is empty
            if not data:
                break
    
            buffer += data                              

            # Process the complete line separated by \n
            while b"\n" in buffer:    

                # Put the complete line in raw and in buffer saves the rest                 
                raw, buffer = buffer.split(b"\n", 1)    
    
                # Decode message bytes into text
                msg = raw.decode('utf-8', errors='ignore') 
                print(f"Received from {address}: {msg!r}")
    
                # Divide first command from arguments
                parts = msg.split(" ", 1)
                cmd = parts[0]                          
                rest = parts[1] if len(parts) > 1 else ""
                print(f"Translated from {address}: {cmd!r}")

                # Commands protocols
                if cmd == "PING":
                    response = "PONG\n"

                elif cmd == "ECHO":
                    response = rest + "\n"   

                elif cmd == "SET":

                    # Separate key from value
                    key, _, value = rest.partition(" ")
                    
                    # Require that both contain smth
                    if not key or not value:
                        response = "ERR\n"
                    else:
                        store[key] = value
                        response = "OK\n"    

                elif cmd == "GET":
                    # Check if there is the key and if it contains spaces
                    if not rest:
                        response = "ERR\n"    
                    else: 
                        response = store.get(rest, "NOT_FOUND") + "\n"
                else:
                    response = "ERR\n"   

                # Send a single line response coded in utf-8
                conn.sendall(response.encode("utf-8"))
                print(f"Response: {response!r}")
    

def runserver(host="0.0.0.0", port=9001):
    # Initialize ipv4 socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allows quick reuse after closing
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  

    # Bind the socket to the host and port
    server.bind((host, port))

    # Start listening for incoming connections
    server.listen()

    print(f"Server listening on port {port}")

    # Keep the server running
    while True:
        # Accept an incoming client connection
        conn, address = server.accept()
        threading.Thread(target=handle_client, args=(conn, address), daemon= True).start()
        
if __name__ == "__main__":
    runserver()