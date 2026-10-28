# TO RUN
# sudo systemctl start tor   
# sudo cat /var/lib/tor/my_website/hostname   

from http.server import *
from urllib.parse import urlparse
import json

claim_token = ""

# Creates a class for handling 
class NT_SERVER(BaseHTTPRequestHandler):

    # Helper for the response
    def send_response_json(self, stat, data):
        msg = json.dumps(data).encode("utf-8")
        self.send_response(stat)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        if clean_path == '/':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

        # Gets the last token received as plain text (doesnt get it through tor)
        elif clean_path == '/claim':
            self.send_response(200)
            self.send_header('content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(claim_token.encode('utf-8'))

        else:
            self.send_response(404)
            self.send_header('content-type', 'text/html')
            self.end_headers()

    def do_POST(self):
        global claim_token
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        # Post the token as plain text in the body
        if clean_path == '/claim':
            
            # Analyzing the size
            content_lengt = int(self.headers.get("content-length", 0))
            
            # Readinf how many bytes and then decode them to a string
            claim_token = self.rfile.read(content_lengt).decode('utf-8')
            self.send_response(200)
            self.end_headers()


port = HTTPServer(('', 8090), NT_SERVER)
# Runs forever
port.serve_forever()