from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from be.model import db_conn

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store(self, choose: int, store_id: str, keyword: str, page: int, limit: int):
        order_id = ""
        try:
            # 初始化连接
            conn = self.conn

            # 构建 SQL 查询条件
            choose = int(choose)
            page = int(page)
            limit = int(limit)
            skip_count = (page - 1) * limit

            if choose == 0:
                sql_query = text(
                    "SELECT * FROM book_store WHERE store_id = :store_id AND "
                    "title LIKE :keyword OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, store_id=store_id, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 1:
                sql_query = text(
                    "SELECT * FROM book_store WHERE store_id = :store_id AND "
                    "tags LIKE :keyword OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, store_id=store_id, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 2:
                sql_query = text(
                    "SELECT * FROM book_store WHERE store_id = :store_id AND "
                    "content LIKE :keyword OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, store_id=store_id, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 3:
                sql_query = text(
                    "SELECT * FROM book_store WHERE store_id = :store_id AND "
                    "book_intro LIKE :keyword OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, store_id=store_id, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]

            return 200, "ok", result
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []

    def search_all(self, choose: int, keyword: str, page: int, limit: int):
        order_id = ""
        try:
            conn = self.conn
            choose = int(choose)
            page = int(page)
            limit = int(limit)
            skip_count = (page - 1) * limit

            if choose == 0:
                sql_query = text(
                    "SELECT * FROM book_store WHERE title LIKE :keyword "
                    "OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 1:
                sql_query = text(
                    "SELECT * FROM book_store WHERE tags LIKE :keyword "
                    "OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 2:
                sql_query = text(
                    "SELECT * FROM book_store WHERE content LIKE :keyword "
                    "OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]
            elif choose == 3:
                sql_query = text(
                    "SELECT * FROM book_store WHERE book_intro LIKE :keyword "
                    "OFFSET :skip_count LIMIT :limit"
                )
                result = conn.execute(sql_query, keyword=f'%{keyword}%', skip_count=skip_count, limit=limit)
                result = [dict(row) for row in result]

            return 200, "ok", result
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []

