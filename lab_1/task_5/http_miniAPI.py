from http.server import *
from urllib.parse import urlparse, parse_qs
import json

notes = {}
counter = 1
claim_token = ""

# creating a class for handling 
class NT_SERVER(BaseHTTPRequestHandler):

    # helper for the response
    def send_response_json(self, stat, data):
        msg = json.dumps(data).encode("utf-8")
        self.send_response(stat)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

    # creating a function for Get Request
    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        if clean_path == '/':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

        elif clean_path == '/claim':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
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
        
        if clean_path == '/claim':
            content_lengt = int(self.headers.get("content-length", 0))
            claim_token = self.rfile.read(content_lengt).decode('utf-8')
            self.send_response(200)
            self.end_headers()
        

    def do_PUT(self):
            parsed_url = urlparse(self.path)
            clean_path = parsed_url.path

            if clean_path == '/notes' or clean_path.startswith('/notes'):
                self.send_response(405)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        if clean_path.startswith('/notes'):
            path_partition = clean_path.strip('/').split('/')
                        
            if len(path_partition) == 2 and path_partition[1].isdigit():
                note_id = int(path_partition[1])

                if note_id in notes:
                    del notes[note_id]
                    self.send_response(204)
                    self.end_headers()
                    return
            
            self.send_response(404)
            self.end_headers()


# this is the object which take port 
# number and the server-name
# for running the server
port = HTTPServer(('', 8090), NT_SERVER)

# this is used for running our 
# server as long as we wish
# i.e. forever
port.serve_forever()