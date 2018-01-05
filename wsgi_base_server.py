#!/usr/bin/env python3


from wsgiref.simple_server import make_server


def application(env, start_response):
    body = "<h1>hello wsgi world</h1>"
    body = body.encode()
    status = "200 OK"
    headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(body))),
            ]
    start_response(status, headers)
    return [body]


if __name__ == "__main__":
    host = "localhost"
    port = 8000
    httpd = make_server(host, port, application)
    httpd.serve_forever()
