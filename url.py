#!/usr/bin/env python3


from wsgiref.simple_server import make_server


class Url:
    urls = {}

    def __init__(self, path_info):
        self.path_info = path_info if path_info[-1] != '/' else path_info[:-1]

    def __call__(self, func):
        Url.urls[self.path_info] = func
        Url.urls[self.path_info + '/'] = func



@Url('/morning')
def morning(env):
    return "Good morning"


@Url('/afternoon')
def afternoon(env):
    return "Good afternoon"


@Url('/evening')
def evening(env):
    return "Good evening"


def happy(env):
    return "Happy day"


def application(env, start_response):
    path_info = env['PATH_INFO']
    msg = Url.urls.get(path_info, happy)(env)

    body = "<h1>%s</h1>" % msg
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
