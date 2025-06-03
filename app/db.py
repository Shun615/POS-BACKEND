import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # .env から DB名が正しく読み込まれているか確認するためのデバッグ出力
    print("✅ DB名：", os.getenv("MYSQL_DB"))  # ← これが追加された行

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        ssl_ca=os.getenv("MYSQL_SSL_CA")
    )
