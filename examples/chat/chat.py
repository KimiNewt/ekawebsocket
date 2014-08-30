import os
import tornado
import tornado.web

from ekawebsocket.websocket import EkaWebsocket


class SingleStaticFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(SingleStaticFileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        # Ignore 'path'.
        super(SingleStaticFileHandler, self).get(self.filename, include_body)


class ChatWebsocketHandler(EkaWebsocket):

    def handle_message(self, message_type, message):
        self.broadcast_to_client_rooms(message)


def main(debug=True):
    application = tornado.web.Application([
         (r'/', SingleStaticFileHandler, {'path': 'static/index.html'}),
         (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
         (r'/chat', ChatWebsocketHandler)
    ], debug=debug)
    application.listen(8888)
    print 'Running Tornado webserver on port 8888'
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()