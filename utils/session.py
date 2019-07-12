# coding:utf-8
import uuid
import logging
import json
import redis
from constants import SESSION_EXPIRES_SECONDS


class Session(object):


    def __init__(self, request_handler_object):
        self._request_handler = request_handler_object
        self.session_id = request_handler_object.get_secure_cookie("session_id")

        if not self.session_id:
            self.session_id = uuid.uuid4().hex
            self.data = {}
            request_handler_object.set_secure_cookie("session_id", self.session_id)
        else:
            try:
                json_data = request_handler_object.redis.get("sess_%s" %self.session_id)
            except Exception as e:
                logging.error(e)
                raise e
            if not json_data:
                self.data = {}
            else:
                self.data = json.loads(json_data)


    def save(self):

        json_data = json.dumps(self.data)
        try:
            self._request_handler.redis.setex("sess_%s" %self.session_id, SESSION_EXPIRES_SECONDS, json_data)
        except Exception as e:
            logging.error(e)
            raise e

    def clear(self):

        try:
            self._request_handler.redis.delete("sess_%s" %self.session_id)
        except Exception as e:
            logging.error(e)

        self._request_handler.clear_cookie("session_id")