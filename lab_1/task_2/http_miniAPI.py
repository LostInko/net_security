from http.server import *
from urllib.parse import urlparse, parse_qs
import json

# Shared in memory data store
notes = {}
counter = 1

class NT_SERVER(BaseHTTPRequestHandler):

    # Helper to send formatted JSON responses
    def send_response_json(self, stat, data):
        msg = json.dumps(data).encode("utf-8")
        self.send_response(stat)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

    # Handles GET requests
    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        if clean_path == '/':
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>(Netsec)</h1>'.encode())

        # Query parameter echo check
        elif clean_path == '/echo':
            query_param = parse_qs(parsed_url.query)

            # Extracts msg value
            msg_val = query_param.get('msg', [''])[0]
            self.send_response_json(200,{"msg": msg_val})

        # Retrieve not by ID
        elif clean_path.startswith('/notes'):
            path_partition = clean_path.strip('/').split('/')

            # Checks if patch matches
            if len(path_partition) == 2 and path_partition[1].isdigit():
                note_id = int(path_partition[1])

                if note_id in notes:
                    msg = notes[note_id]
                    self.send_response_json(200, {"id":note_id, "text": msg})
                    self.end_headers()
                    return

            # Non numeric id or missing
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 not found</h1>'.encode())

    # Handles POST requests
    def do_POST(self):
        global counter
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        # Enforce content-type header costraint
        content_type = self.headers.get('content-type', '')
        if content_type != "application/json":
            self.send_response(415)
            self.end_headers()

        if clean_path.startswith('/notes'):
            content_lengt = int(self.headers.get("content-length", 0))
            msg_bytes = self.rfile.read(content_lengt)

            # Parse json body
            try:
                data = json.loads(msg_bytes.decode('utf-8'))
            
            except(json.JSONDecodeError, UnicodeDecodeError):    
                self.send_response(400)
                self.end_headers()
                return

            # Validate json, the payload must be a dictionary containinga string key
            if not isinstance(data, dict) or 'text' not in data or not isinstance(data['text'], str):
                self.send_response(400)
                self.end_headers()
                return
            
            # Saving the note
            notes_text = data['text']        
            new_id = counter    
            notes[new_id] = notes_text
            counter += 1
            self.send_response_json(201, {'id': new_id})

    # Handles unsupported modes
    def do_PUT(self):
            parsed_url = urlparse(self.path)
            clean_path = parsed_url.path

            if clean_path == '/notes' or clean_path.startswith('/notes'):
                self.send_response(405)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    # Handles DELETE requests
    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        if clean_path.startswith('/notes'):
            path_partition = clean_path.strip('/').split('/')

            # Ensure path matches the id        
            if len(path_partition) == 2 and path_partition[1].isdigit():
                note_id = int(path_partition[1])

                # If found delete note
                if note_id in notes:
                    del notes[note_id]
                    self.send_response(204)
                    self.end_headers()
                    return
            
            self.send_response(404)
            self.end_headers()


# Server initialization on port 8080
if __name__ == '__main__':
    server = HTTPServer(('', 8080), NT_SERVER)
    print("Server running on port 8080...")
    server.serve_forever()