import uuid
import logging
from be.model import db_conn
from be.model import error
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from be.model.times import add_unpaid_order, delete_unpaid_order, check_order_time, get_time_stamp
from be.model.order import Order


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):#判断user存在否
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):#判断store存在否
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0
            for book_id, count in id_and_count:
                #更新库存
                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - :count "
                    "WHERE store_id = :store_id and book_id = :book_id and stock_level >= :count "
                    "RETURNING price",
                    {"count":count, "store_id":store_id, "book_id":book_id, "count":count})
                if cursor.rowcount == 0:
                    self.conn.rollback()
                    return error.error_stock_level_low(book_id) + (order_id, )
                row = cursor.fetchone()
                price = row[0]

                #创建新订单信息
                self.conn.execute(
                        "INSERT INTO new_order_detail(order_id, book_id, count) "
                        "VALUES(:uid, :book_id, :count)",
                        {"uid":uid, "book_id":book_id, "count":count})

                # 计算总价
                total_price += count * price

            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id, total_price, order_time) "
                "VALUES(:uid, :store_id, :user_id, :total_price, :order_time)",
                {"uid":uid, "store_id":store_id, "user_id":user_id, "total_price":total_price, "order_time": get_time_stamp()})#增加总价和订单状态
            self.conn.commit()
            order_id = uid

            # 增加订单到数组
            add_unpaid_order(order_id)
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id



    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.execute("SELECT * FROM new_order WHERE order_id = :order_id",
                                  {"order_id": order_id, })
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            total_price = row[4]# 总价
            order_time = row[5]
            status = row[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if status != 1:
                return error.error_invalid_order_status()
            if check_order_time(order_time) == False:
                self.conn.commit()
                delete_unpaid_order(order_id)
                o = Order()
                o.cancel_order(order_id)
                return error.error_invalid_order_id()

            cursor = conn.execute("SELECT balance, password FROM users WHERE user_id = :buyer_id;",
                                  {"buyer_id": buyer_id, })
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 下单扣买家的钱
            cursor = conn.execute("UPDATE users set balance = balance - :total_price1 "
                                  "WHERE user_id = :buyer_id AND balance >= :total_price2",
                                  {"total_price1": total_price, "buyer_id": buyer_id, "total_price2": total_price})
            if cursor.rowcount == 0:
                return error.error_unknown("update_user_error")

            self.conn.execute(
                "UPDATE new_order set status=2 where order_id = '%s' ;" % (order_id))
            self.conn.commit()

            #从数组中删除
            delete_unpaid_order(order_id)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):#买家充值
        try:
            cursor = self.conn.execute("SELECT password from users where user_id=:user_id", {"user_id":user_id,})
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE users SET balance = balance + :add_value WHERE user_id = :user_id",
                {"add_value":add_value, "user_id":user_id})
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"


    def search_history_order(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return 513, "non exist user_id", []  # error.error_non_exist_user_id(user_id)

            cursor = self.conn.execute(
                "SELECT order_id, store_id, status, total_price, order_time FROM new_order "
                "WHERE user_id = :user_id",
                {"user_id": user_id}
            )
            result = []
            for row in cursor.fetchall():
                order_data = {
                    "order_id": row[0],
                    "store_id": row[1],
                    "status": row[2],
                    "total_price": row[3],
                    "order_time": row[4]
                }
                result.append(order_data)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []

        return 200, "ok", result


    def cancel(self, buyer_id, order_id) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT status FROM new_order WHERE order_id = :order_id;",
                                       {"order_id": order_id, })
            row = cursor.fetchone()
            if row[0] != 1:
                return error.error_invalid_order_status(order_id)

            if not self.user_id_exist(buyer_id):
                return error.error_non_exist_user_id(buyer_id)
            if not self.order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)

            # 从数组中删除
            delete_unpaid_order(order_id)
            o = Order()
            o.cancel_order(order_id)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 收货
    def receive_books(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):  #增加order_id不存在的错误处理
                return error.error_invalid_order_id(order_id)

            cursor = self.conn.execute("SELECT order_id, user_id, store_id, total_price, status FROM new_order WHERE order_id = :order_id",
                                  {"order_id": order_id, })
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            total_price = row[3]  # 总价
            status = row[4]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if status != 3:
                return error.error_invalid_order_status(order_id)

            cursor = self.conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id = :store_id;",
                                  {"store_id": store_id, })
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = self.conn.execute("UPDATE users set balance = balance + :total_price "
                                  "WHERE user_id = :seller_id",
                                  {"total_price": total_price, "seller_id": seller_id})
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            self.conn.commit()
            o = Order()
            o.cancel_order(order_id, end_status=4)
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
