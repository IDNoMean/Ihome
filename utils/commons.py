# coding:utf-8

def required_login(func):
    def wrapper(request_handler_obj, *args, **kargs):
        if not request_handler_obj.get_current_user():
            request_handler_obj.write(dict(errcode=RET.SESSIONERR, errmsg="用户未登录"))
        else:
            func(request_handler_obj, *args, **kargs)

    return wrapper

# @dec
# def add_two(num1, num2):
#     return num1+num2
#
# add_two = dec(add_two)    .__name__ = "add_two"
#
# @dec
# def add_three(num1, num2, num3):
#     return num1+num2+num3
#
# def dec(f):
#     @functools.wraps(f)
#     def wrapper(*args, **kwargs):
#         print("hello")
#         f(*args, **kwargs)
#     return wrapper
#
#
#
# def main(fun):
#     a, b, c = 1, 2, 3
#     if fun.__name__ == "add_two":
#         fun(a, b)
#     elif fun.__name__ == "add_three":
#         fun(a, b, c)























