# coding:utf-8
from .BaseHandler import BaseHandlers
from utils.commons import required_login
from utils.response_code import RET
import logging
import datetime
import constants

class OrderHandler(BaseHandlers):

    @required_login
    def post(self):
        user_id = self.session.data["user_id"]
        house_id = self.json_args("house_id")
        start_date = self.json_args("start_date")
        end_date = self.json_args("end_date")

        if not all((house_id, start_date, end_date)):
            return self.write({"errcode": RET.PARAMERR, "errmsg": "params error"})

        try:
            house = self.db.get("select hi_price,hi_user_id from ih_house_info where hi_house_id=%s", house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "get house error"})

        if not house:
            return self.write({"errcode":RET.NODATA, "errmsg":"no data"})

        if user_id == house["hi_user_id"]:
            return self.write({"errcode": RET.ROLEERR, "errmsg": "user is forbidden"})

        days = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(start_date, "%Y-%m-%d")).days + 1

        if days <= 0:
            return self.write({"errcode": RET.PARAMERR, "errmsg": "date params error"})

        try:
            ret = self.db.get("select count(*) counts from ih_order_info where oi_house_id=%(house_id)s "
                              "and oi_begin_date<%(end_date)s and oi_end_date>%(start_date)s",
                              house_id=house_id, end_date=end_date, start_date=start_date)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode":RET.DBERR, "errmsg":"get date error"})

        if ret["counts"] > 0:
            return self.write({"errcode":RET.DATAERR, "errmsg":"serve date error"})

        amount = days * house["hi_price"]

        try:
            self.db.execute(
                "insert into ih_order_info(oi_user_id,oi_house_id,oi_begin_date,oi_end_date,oi_days,oi_house_price,oi_amount)"
                " values(%(user_id)s,%(house_id)s,%(begin_date)s,%(end_date)s,%(days)s,%(price)s,%(amount)s);"
                "update ih_house_info set hi_order_count=hi_order_count+1 where hi_house_id=%(house_id)s;",
                user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date, days=days,
                price=house["hi_price"], amount=amount)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "save data error"})

        self.write({"errcode": RET.OK, "errmsg": "OK"})

class MyOrderHandler(BaseHandlers):

    @required_login
    def get(self):
        user_id = self.session.data["user_id"]
        role = self.json_args["role", ""]
        try:
            if "landlord" == role:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,"
                                    "oi_days,oi_amount,oi_status,oi_comment from ih_order_info inner join ih_house_info "
                                    "on oi_house_id=hi_house_id where hi_user_id=%s order by oi_ctime desc", user_id)
            else:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,"
                                    "oi_days,oi_amount,oi_status,oi_comment from ih_order_info inner join ih_house_info "
                                    "on oi_house_id=hi_house_id where oi_user_id=%s order by oi_ctime desc", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "get data error"})

        orders = []
        if ret:
            for l in ret:
                order = {
                    "order_id": l["oi_order_id"],
                    "title": l["hi_title"],
                    "img_url": constants.QINIU_URL_PREFIX + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                    "start_date": l["oi_begin_date"].strftime("%Y-%m-%d"),
                    "end_date": l["oi_end_date"].strftime("%Y-%m-%d"),
                    "ctime": l["oi_ctime"].strftime("%Y-%m-%d"),
                    "days": l["oi_days"],
                    "amount": l["oi_amount"],
                    "status": l["oi_status"],
                    "comment": l["oi_comment"] if l["oi_comment"] else ""
                }

                orders.append(order)

        self.write({"errcode": RET.OK, "errmsg": "OK", "orders": orders})


class AcceptOrderHandler(BaseHandlers):

    @required_login
    def post(self):
        user_id = self.session.data["user_id"]
        order_id = self.json_args["order_id"]
        if not order_id:
            return self.write({"errcode": RET.PARAMERR, "errmsg": "params error"})

        try:
            self.db.execute("update ih_order_info set oi_status=3 where oi_order_id=%(order_id)s and oi_house_id in "
                            "(select hi_house_id from ih_house_info where hi_user_id=%(user_id)s) and oi_status=0",
                            # update ih_order_info inner join ih_house_info on oi_house_id=hi_house_id set oi_status=3 where
                            # oi_order_id=%(order_id)s and hi_user_id=%(user_id)s
                            order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "DB error"})

        self.write({"errcode": RET.OK, "errmsg": "OK"})


class RejectOrderHandler(BaseHandlers):

    @required_login
    def post(self):
        user_id = self.session.data["user_id"]
        order_id = self.json_args["order_id"]
        reject_reason = self.json_args["reject_reason"]

        if not all((order_id, reject_reason)):
            return self.write({"errcode": RET.PARAMERR, "errmsg": "params error"})
        try:
            self.db.execute("update ih_order_info set oi_status=6,oi_comment=%(reject_reason)s "
                            "where oi_order_id=%(order_id)s and oi_house_id in (select hi_house_id from ih_house_info "
                            "where hi_user_id=%(user_id)s) and oi_status=0",
                            reject_reason=reject_reason, order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "DB error"})
        self.write({"errcode": RET.OK, "errmsg": "OK"})

class OrderCommentHandler(BaseHandlers):

    @required_login
    def post(self):
        user_id = self.session.data["user_id"]
        order_id = self.json_args.get("order_id")
        comment = self.json_args.get("comment")
        if not all((order_id, comment)):
            return self.write({"errcode": RET.PARAMERR, "errmsg": "params error"})
        try:
            # 需要确保只能评论自己下的订单
            self.db.execute("update ih_order_info set oi_status=4,oi_comment=%(comment)s where oi_order_id=%(order_id)s "
                            "and oi_status=3 and oi_user_id=%(user_id)s", comment=comment, order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode":RET.DBERR, "errmsg":"DB error"})

        # 同步更新redis缓存中关于该房屋的评论信息，此处的策略是直接删除redis缓存中的该房屋数据
        try:
            ret = self.db.get("select oi_house_id from ih_order_info where oi_order_id=%s", order_id)
            if ret:
                self.redis.delete("house_info_%s" % ret["oi_house_id"])
        except Exception as e:
            logging.error(e)
        self.write({"errcode":RET.OK, "errmsg":"OK"})
