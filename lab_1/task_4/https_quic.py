import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
import hashlib

async def app(scope, receive, send):
    
    # Eusure only http
    if scope['type'] != 'http':
        return

    # This reads
    method = scope.get('method')
    path = scope.get('path')
    http_version = scope.get('http_version')  

    if method == "GET" and path == '/':
        status_code = 200
        response_body = b"OK"
    elif method == "GET" and path == '/proto':
        status_code = 200
        match http_version:
            case '1.1': response_body = b'HTTP/1.1'
            case '2': response_body = b'HTTP/2'
            case '3': response_body = b'HTTP/3'

    elif method == 'POST' and path == '/hash':
        body_chunk = []
        while True:
            message = await receive()
            if message['type'] == 'http.request':    
                body_chunk.append(message.get('body','b'))

            if not message.get('more_body', False):
                break
        full_body = b''.join(body_chunk)
        status_code = 200
        hashcode = hashlib.sha256(full_body).hexdigest()
        response_body = hashcode.encode('utf-8')
    else:
        status_code = 404
        response_body = b"crazy"

    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', b'text/plain'),
                    (b'content-length', str(len(response_body)).encode('utf-8')),
                    (b'alt-svc', b'h3 = "4433"')],

    })
    
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