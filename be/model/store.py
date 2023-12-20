import logging
import os
import sqlite3 as sqlite
import mysql.connector
import threading


class Store:
    database: str

    def __init__(self, db_config):
        # self.database = os.path.join(db_path, "be.db")
        self.database = mysql.connector.connect(**db_config)
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cursor = conn.cursor()

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            # )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id VARCHAR(255) PRIMARY KEY, password VARCHAR(255) NOT NULL, "
                "balance INT NOT NULL, token VARCHAR(255), terminal VARCHAR(255));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id VARCHAR(255), store_id VARCHAR(255), PRIMARY KEY(user_id, store_id));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id VARCHAR(255), book_id VARCHAR(255), book_info TEXT, stock_level INT,"
                " PRIMARY KEY(store_id, book_id))"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id VARCHAR(255) PRIMARY KEY, user_id VARCHAR(255), store_id VARCHAR(255))"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id VARCHAR(255), book_id VARCHAR(255), count INT, price INT,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.commit()
        
        # except sqlite.Error as e:
        except mysql.connector.Error as e:
            logging.error(e)
            conn.rollback()

    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)
    def get_db_conn(self):
        return self.database


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_config):
    global database_instance
    database_instance = Store(db_config)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
