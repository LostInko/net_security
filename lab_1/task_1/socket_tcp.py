import socket
import threading

store = {}

def handle_client(conn, address):
    print(f"Connection from {address}")
    with conn:
        buffer = b""                                    
    
        while True:
            # Receive up to 1024
            data = conn.recv(1024)
    
            if not data:
                break
    
            buffer += data                              
    
            while b"\n" in buffer:                     
                raw, buffer = buffer.split(b"\n", 1)    
    
                # Decode message 
                msg = raw.decode('utf-8', errors='ignore') 
                print(f"Received from {address}: {msg!r}")
    
                # Divide first command from rest
                parts = msg.split(" ", 1)
                cmd = parts[0]                          
                rest = parts[1] if len(parts) > 1 else ""
                print(f"Translated from {address}: {cmd!r}")
    
                if cmd == "PING":
                    response = "PONG\n"
                elif cmd == "ECHO":
                    response = rest + "\n"   
                elif cmd == "SET":
                    key, _, value = rest.partition(" ")
                    if not key or not value:
                        response = "ERR\n"
                    else:
                        store[key] = value
                        response = "OK\n"    
                elif cmd == "GET":
                    if not rest:
                        response = "ERR\n"    
                    else: 
                        response = store.get(rest, "NOT_FOUND") + "\n"
                else:
                    response = "ERR\n"   
    
                conn.sendall(response.encode("utf-8"))
                print(f"Response: {response!r}")
    

def runserver(host="0.0.0.0", port=9001):
    # socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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