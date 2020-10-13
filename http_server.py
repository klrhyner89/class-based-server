import socket
import sys
import traceback
import os
import pathlib
import mimetypes

class HttpServer():

    @staticmethod
    def make_response(
        code,
        reason,
        body=b"",
        mimetype=b"text/plain"
    ):
        """
        returns a basic HTTP response
        Ex:
            make_response(
                b"200",
                b"OK",
                b"<html><h1>Welcome:</h1></html>",
                b"text/html"
            ) ->

            b'''
            HTTP/1.1 200 OK\r\n
            Content-Type: text/html\r\n
            \r\n
            <html><h1>Welcome:</h1></html>\r\n
            '''
        """

        return b"\r\n".join([
            b"HTTP/1.1 " + code + b" " + reason,
            b"Content-Type: " + mimetype,
            b"",
            body
        ])

    @staticmethod
    def get_path(request):
        """
        Given the content of an HTTP request, return the _path_
        of that request.

        For example, if request were:

        '''
        GET /images/sample_1.png HTTP/1.1
        Host: localhost:1000

        '''

        Then you would return "/images/sample_1.png"
        """
        # IN: GET /images/sample_1.png HTTP/1.1 OUT: /images/sample_1.png
        return request.split(' ')[1]


    @staticmethod
    def get_mimetype(path):
        """
        This method should return a suitable mimetype for the given `path`.

        A mimetype is a short bytestring that tells a browser how to
        interpret the response body. For example, if the response body
        contains a web page then the mimetype should be b"text/html". If
        the response body contains a JPG image, then the mimetype would
        be b"image/jpeg".

        Here are a few concrete examples:

            get_mimetype('/a_web_page.html') -> b"text/html"

            get_mimetype('/images/sample_1.png') -> b"image/png"

            get_mimetype('/') -> b"text/plain"
            # A directory listing should have either a plain text mimetype
            # or a b"text/html" mimetype if you turn your directory listings
            # into web pages.

            get_mimetype('/a_page_that_doesnt_exist.html') -> b"text/html"
            # This function should return an appropriate mimetype event
            # for files that don't exist.
        """

        if path.endswith('/'):
            return b"text/plain"
        else:
            # b"TODO: FINISH THE REST OF THESE CASES"  # TODO
            # mimetypes.guess_type(path) -> tuple of (#$ , #$)
            return bytes(str(mimetypes.guess_type(path)[0]), 'utf-8') # b'image/png'

    @staticmethod
    def get_content(path):
        """
        This method should return the content of the file/directory
        indicated by `path`. For example, if path is `/a_web_page.html`
        then this function would return the contents of the file
        `webroot/a_web_page.html` as a byte string.

          * If the requested path is a directory, then the content should
          be a plain-text listing of the contents of that directory.

          * If the path is a file, it should return the contents of that
            file.

          * If the indicated path doesn't exist inside of `webroot`, then
            raise a FileNotFoundError.

        Here are some concrete examples:

        Ex:
            get_content('/a_web_page.html') -> b"<html><h1>North Carolina..."
            # Returns the contents of `webroot/a_web_page.html`

            get_content('/images/sample_1.png') -> b"A12BCF..."
            # Returns the contents of `webroot/images/sample_1.png`

            get_content('/') -> images/, a_web_page.html, make_type.py,..."
            # Returns a directory listing of `webroot/`

            get_content('/a_page_that_doesnt_exist.html') 
            # The file `webroot/a_page_that_doesnt_exist.html`) doesn't exist,
            # so this should raise a FileNotFoundError.
        """
        if os.path.exists(pathlib.Path.cwd() / 'webroot' / path[1:]):
            if HttpServer.get_mimetype(path) == b'None' or path == '/':
        # below is broken
                # items = []
                # for item in os.listdir(pathlib.Path.cwd() / 'webroot' / path[1:]):
        # if the mimetype of the item is None, its another directory (not jpg, html, etc.), add that to the href path
                #     items.append('\n<li><a href=\"http://localhost:10000/{0}\"><b>{0}</b></a></li>'.format(item))
                # return ('<!DOCTYPE html> \n<html> \n<body> \n<h1>File Contents</h1> \
                #         \n<p>So many things!</p> \n</ul>{}\n<ul> \n</body> \n</html>'.format(''.join(items)), True)
                return bytes(str(os.listdir(pathlib.Path.cwd() / 'webroot' / path[1:])), 'utf-8')
            else:
                with open(pathlib.Path.cwd() / 'webroot' / path[1:], 'rb') as f:
                    bytified = f.read()     
                return bytified
        raise FileNotFoundError  # TODO: Complete this function.

    def __init__(self, port):
        self.port = port

    def serve(self):
        address = ('0.0.0.0', port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("making a server on {0}:{1}".format(*address))
        print("Visit http://localhost:{}".format(port))

        sock.bind(address)
        sock.listen(10)

        try:
            while True:
                print('waiting for a connection')
                conn, addr = sock.accept()  # blocks until a connection arrives
                try:
                    print('connection - {0}:{1}'.format(*addr))

                    request = ''
                    while True:
                        data = conn.recv(1024)
                        request += data.decode('utf8')

                        if '\r\n\r\n' in request:
                            break
                    
                    print("Request received:\n{}\n\n".format(request))

                    path = self.get_path(request) #e.g. /images/sample_1.png
                    
                    try:
                        # get_content needs to be able to raise a filenotfound error    DONE
                        body = self.get_content(path) #returns contents of a file or dir list
                        # if body[1]:
                        #     mimetype = b'text/html'
                        #     body = bytes(str(body[0]), 'utf-8')
                        # else:
                        mimetype = self.get_mimetype(path) #short str that tells browser what it is e.g image, webpage
                        # http response to req
                        response = self.make_response(
                            b"200", b"OK", body, mimetype
                        )

                    except FileNotFoundError:
                        body = b"Couldn't find the file you requested."
                        mimetype = b"text/plain"

                        response = self.make_response(
                            b"404", b"NOT FOUND", body, mimetype
                        )

                    conn.sendall(response)
                except:
                    traceback.print_exc()
                finally:
                    conn.close() 

        except KeyboardInterrupt:
            sock.close()
            return
        except:
            traceback.print_exc()


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 10000 

    server = HttpServer(port)
    server.serve()

