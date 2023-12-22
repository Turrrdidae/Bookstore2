from be.model import error
from be.model import db_conn
import json
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            response = self.mongo['book'].find_one({'id':book_id})
            book_info_json = json.loads(book_json_str)
            price = book_info_json.get("price")
            book_info_json.pop("price")

            title = ''
            title = book_info_json.get("title")
            tags = ''
            tags = book_info_json.get("tags")
            content = ''
            content = book_info_json.get("content")
            book_intro = ''
            book_intro = book_info_json.get("book_intro")

            self.conn.execute(
                "INSERT INTO book_store(store_id, book_id, title, tags, content, book_intro) "
                "VALUES (:sid, :bid, :til, :tgs, :cnt, :intro)",
                {'sid': store_id, 'bid': book_id, 'til': title, 'tgs': tags, 'cnt': content, 'intro': book_intro}
            )
            self.conn.execute(
                "INSERT into store(store_id, book_id, stock_level, price) VALUES (:sid, :bid, :skl, :prc)",
                {'sid': store_id, 'bid': book_id, 'skl': stock_level, 'prc': price})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except PyMongoError as e:
            return 529, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("UPDATE store SET stock_level = stock_level + :asl  WHERE store_id = :sid AND book_id = :bid",
                              {'asl':add_stock_level, 'sid':store_id, 'bid':book_id})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.conn.execute("INSERT into user_store(store_id, user_id) VALUES (:sid, :uid)", {'sid':store_id, 'uid':user_id})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 发货
    def send_books(self,store_id,order_id):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.order_id_exist(order_id):   #增加order_id不存在的错误处理
                return error.error_invalid_order_id(order_id)
            cursor = self.conn.execute(
                "SELECT status FROM new_order where order_id = '%s' ;" % (order_id))
            row = cursor.fetchone()
            status = row[0]
            if status != 2:
                return error.error_invalid_order_status(order_id)

            self.conn.execute(
                "UPDATE new_order set status=3 where order_id = '%s' ;" % (order_id))
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"