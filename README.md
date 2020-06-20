# ServerLight
**This module defines classes for implementing HTTP/WSGI servers (Web servers).**
> Warning : This is not recommended for production. It only implements
> basic security checks.

One class, Server or WSGI Server creates and listens at the HTTP 
socket, dispatching the requests to a handler. Code to create and run the server looks like this:\

```python
def run(server_class=Server, handler_class=BaseHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
run()
```

 - fast ( It's very fast )
 - simple ( around 150 lines )
 - lightweight (simple and lightweight )
 -  [WSGI](http://www.wsgi.org/) ( supports web server gateway interface )
 -  micro web-server ( can use as a traditional server )
 - with web frameworks (any  [WSGI](http://www.wsgi.org/)  framework supported)
 
> Flask, Django, Pyramid, Bottle supported
 ### Example: "Hello World"
 
```python
def app(environ, start_response):
    ""A barebones WSGI application.
    This is a starting point for your own Web framework :)
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Hello world from a simple WSGI application!\n']
```

save above code as app.py
now run sl (ServeLight)

```bash
python -m sl --app=app:app
```

view [examples](https://github.com/Ksengine/ServeLight/blob/master/examples) for more...
**View Documentaion***
### License
Code and documentation are available according to the MIT License (see  [LICENSE](https://github.com/Ksengine/ServeLight/blob/master/LICENSE)).
