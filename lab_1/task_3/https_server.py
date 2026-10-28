import http.server
import ssl
import threading
from urllib.parse import urlparse
import uuid
from http.cookies import SimpleCookie
import json

sessions = {}

# Handler for Port 8443 (TLS and Session authentication)
class StandardHTTPSHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        if clean_path == '/':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

        # Session verification with username
        elif clean_path == '/me':
            raw_cookies = self.headers.get('Cookie')
            username = None

            # Parse incoming COokie header to retrieve session_id
            if raw_cookies:
                cookie = SimpleCookie()
                cookie.load(raw_cookies)
                if 'session_id' in cookie:
                    session_token = cookie["session_id"].value
                    username = sessions.get(session_token)

            # Return user details if the session is valid
            if username:
                msg = json.dumps({"user": username}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
            else:
                self.send_response(401)
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header('content-type', 'text/html')
            self.end_headers()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        # Validate Content-Type header costraint
        content_type = self.headers.get('content-type', '')
        if content_type != "application/json":
            self.send_response(415)
            self.end_headers()
            return

        # Validate credentials (login) and issue session cookie
        if clean_path.startswith('/login'):
            content_lengt = int(self.headers.get("content-length", 0))
            msg_bytes = self.rfile.read(content_lengt)

            # Parse json body
            try:
                data = json.loads(msg_bytes.decode('utf-8'))
            
            except(json.JSONDecodeError, UnicodeDecodeError):    
                self.send_response(400)
                self.end_headers()
                return
            
            if not isinstance(data, dict):
                self.send_response(400)
                self.end_headers()
                return

            username = data.get("user")
            password = data.get("password")

            # Authenticate by using netsec ad password and check not empty username
            if password == "netsec" and isinstance(username, str) and username:
                session_token = str(uuid.uuid4())
                sessions[session_token] = username

                self.send_response(200)
                self.send_header('Set-Cookie', f'session_id={session_token}; Secure; HttpOnly; Path=/')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
            else:
                self.send_response(401)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()




# Handler for Port 8444 (mTLS authentication)
class MTLSServerHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        # Identity extraction route
        if clean_path == '/whoami':
            
            # Retrieve validated client certificate from socket
            peercert = self.connection.getpeercert()
            common_name = None

            # Extract commonName attribute from certificate
            if peercert and 'subject' in peercert:
                for rdn in peercert['subject']:
                    for key, val in rdn:
                        if key == 'commonName':
                            common_name = val
                            break

            # If extracted retrieve CommonName
            if common_name:
                body = common_name.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                
            else:
                self.send_response(401)
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header('content-type', 'text/html')
            self.end_headers()

        


def run_port_8443():
    server = http.server.HTTPServer(("0.0.0.0", 8443), StandardHTTPSHandler)
    
    # Configure TLS context for port 8443
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print("Port 8443 (Standard TLS) listening...")
    server.serve_forever()


def run_port_8444():
    server = http.server.HTTPServer(("0.0.0.0", 8444), MTLSServerHandler)
    
    # Configure mTLS context for port 8444
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    
    # Enforce client certificate verification against CA
    context.load_verify_locations(cafile="ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED

    server.socket = context.wrap_socket(server.socket, server_side=True)
    print("Port 8444 (mTLS) listening...")
    server.serve_forever()


if __name__ == "__main__":

    # Launch both HTTPS servers concurrently using separate daemon threads
    t1 = threading.Thread(target=run_port_8443, daemon=True)
    t2 = threading.Thread(target=run_port_8444, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()