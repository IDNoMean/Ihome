import json
from utils.session import Session

from tornado.web import RequestHandler, StaticFileHandler

class BaseHandlers(RequestHandler):


    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = {}

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data