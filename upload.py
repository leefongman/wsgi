#!/usr/bin/env python3


import os
from wsgiref.simple_server import make_server
from cgi import FieldStorage

html = """
<html>
<body>
  <form method="post" action="" enctype="multipart/form-data">
    User name: <input name="user"> <br />
    <input type="file" name="file1"> <br />
    <input type="file" name="file2"> <br />
    <p>
      result: %(message)s<br>
    </p>
    <p>
      <input type="submit" value="Submit">
    </p>
  </form>
</body>
</html>
"""


# 处理大文件上传的生成器
def buffer(f, chunk_size=10240):
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def application(env, start_response):
    formdata = FieldStorage(environ=env, fp=env['wsgi.input'])
    response_texts = []
    for key in formdata.keys():
        data = formdata[key]
        # if data.type == 'application/octet-stream':
        if data._binary_file and data.filename:
            filename = data.filename
            filesize = 0
            opath = os.path.join('uploads', filename)
            with open(opath, 'wb', 10240) as ofile:
                for chunk in buffer(data.file):
                    filesize += len(chunk)
                    ofile.write(chunk)
            response_texts.append('%s <%s bytes>' % (filename, filesize))
        else:
            """在这里处理非文件的表单数据"""

    response_body = html % {'message': ', '.join(response_texts)}
    response_body = response_body.encode()

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


if __name__ == '__main__':
    host = 'localhost'
    port = 8000
    print('<pid: %s> serving on %s:%s' % (os.getpid(), host, port))
    httpd = make_server(host, port, application)
    httpd.serve_forever()
