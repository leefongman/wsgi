#!/usr/bin/env python3


from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from html import escape


html = """
<html>
<body>
  <form method="get" action="">
    <p>Age: <input type="text" name="age" value="%(age)s"></p>
    <p>Hobbies:
      <input name="hobbies" type="checkbox" value="software"
        %(checked-software)s> Software
      <input name="hobbies" type="checkbox" value="tunning"
        %(checked-tunning)s> Auto Tunning
    </p>
    <p>
      <input type="submit" value="Submit">
    </p>
  </form>
  <p>
    Age: %(age)s<br>
    Hobbies: %(hobbies)s
  </p>
</body>
</html>
"""


def application(env, start_response):
    d = parse_qs(env['QUERY_STRING'])

    age = d.get('age', [''])[0]
    hobbies = d.get('hobbies', [])

    age = escape(age)
    hobbies = [escape(hobby) for hobby in hobbies]
    body = html % {
            'checked-software': ('', 'checked')['software' in hobbies],
            'checked-tunning': ('', 'checked')['tunning' in hobbies],
            'age': age or 'Empty',
            'hobbies': ', '.join(hobbies or ['No Hobbies?'])
            }
    body = body.encode()
    status = "200 OK"
    headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(body))),
            ]
    start_response(status, headers)
    return [body]


if __name__ == '__main__':
    host = 'localhost'
    port = 8000
    print('serving on %s:%s' % (host, port))
    httpd = make_server(host, port, application)
    httpd.serve_forever()
