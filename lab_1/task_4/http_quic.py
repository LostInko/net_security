import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
import hashlib

# Call this once for every incoming request: 
# scope = dict that contains (type, method type, path, HTTP version, etc)
async def app(scope, receive, send):
    
    # Eusure only http
    if scope['type'] != 'http':
        return

    # Reads the request from scope
    method = scope.get('method')
    path = scope.get('path')
    http_version = scope.get('http_version')  

    if method == "GET" and path == '/':
        status_code = 200
        response_body = b"OK"
        
    # Return plain text with the protocol 2
    elif method == "GET" and path == '/proto':
        status_code = 200
        match http_version:
            case '1.1': response_body = b'HTTP/1.1'
            case '2': response_body = b'HTTP/2'
            case '3': response_body = b'HTTP/3'

    # Return the hash of the full body
    elif method == 'POST' and path == '/hash':
        
        # The body arrives in separated chunk so we keep them all in a list
        body_chunk = []
        while True:
            message = await receive() 
            
            # If the message type match we save the chunk of text into the list
            if message['type'] == 'http.request':    
                body_chunk.append(message.get('body','b'))

            # If there are no other chunks coming we stop the loop
            if not message.get('more_body', False):
                break
        
        # Joins all the chunks into a single object
        full_body = b''.join(body_chunk)
        status_code = 200
        
        # Computes the hash and encode it into bytes
        hashcode = hashlib.sha256(full_body).hexdigest()
        response_body = hashcode.encode('utf-8')
    else:
        status_code = 404
        response_body = b"crazy"

    # Headers
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', b'text/plain'),
                    # Length in bytes
                    (b'content-length', str(len(response_body)).encode('utf-8')),
                    # Alt-svc advertise that HTTP/3 is available so tcp can connect into QUIC
                    (b'alt-svc', b'h3="4433"')],

    })
    
    # Body
    await send({
        'type': 'http.response.body',
        'body': response_body,
    })


async def main():
    config = Config()

    # TLS Certificates 
    config.certfile = "cert.pem"
    config.keyfile = "key.pem"

    # TCP Binding 
    config.bind = ["0.0.0.0:4433"]

    # UDP Binding
    config.quic_bind = ["0.0.0.0:4433"]

    # Launch Hypercorn server
    await serve(app, config)


if __name__ == "__main__":
    asyncio.run(main())