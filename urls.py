# coding:utf-8

import os
from tornado.web import StaticFileHandler
#from handlers.BaseHandler import StaticFileBaseHandler as StaticFileHandler
from handlers import Passport, VerifyCode#Profile, House, Orders

urls = [
    # (r"/log", Passport.LogHandler),
    (r"/api/register", Passport.RegisterHandler),
    (r"/api/login", Passport.LoginHandler),
    (r"/api/logout", Passport.LogoutHandler),
    (r"/api/check_login", Passport.CheckLoginHandler), # 判断用户是否登录
    (r"/", Passport.IndexHandler),
    (r"/api/piccode", VerifyCode.PicCodeHandler),
    (r"/api/smscode", VerifyCode.SMSCodeHandler),
    (r"/(.*)", StaticFileHandler,dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]

