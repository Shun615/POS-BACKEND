from fastapi import FastAPI
from app.db import get_connection
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "POS-API is running!"}

@app.get("/product/{code}")
def get_product_by_code(code: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM `商品マスタ` WHERE CODE = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result
    else:
        return {"message": "商品が見つかりません"}


# ======================
# /purchase POST API 追加部分
# ======================

class PurchaseItem(BaseModel):
    code: str
    name: str
    price: int

class PurchaseRequest(BaseModel):
    emp_cd: str
    store_cd: str
    pos_no: str
    items: List[PurchaseItem]

@app.post("/purchase")
def make_purchase(purchase: PurchaseRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 取引テーブルに追加（合計金額は0で初期登録）
    cursor.execute(
        "INSERT INTO 取引 (EMP_CD, STORE_CD, POS_NO, TOTAL_AMT) VALUES (%s, %s, %s, %s)",
        (purchase.emp_cd, purchase.store_cd, purchase.pos_no, 0)
    )
    trd_id = cursor.lastrowid

    # 2. 明細テーブルに1商品ずつ登録
    total_amt = 0
    for i, item in enumerate(purchase.items):
        cursor.execute(
            "INSERT INTO 取引明細 (TRD_ID, DTL_ID, PRD_ID, PRD_CODE, PRD_NAME, PRD_PRICE) "
            "VALUES (%s, %s, NULL, %s, %s, %s)",
            (trd_id, i + 1, item.code, item.name, item.price)
        )
        total_amt += item.price

    # 3. 合計金額を取引テーブルに反映
    cursor.execute(
        "UPDATE 取引 SET TOTAL_AMT = %s WHERE TRD_ID = %s",
        (total_amt, trd_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "total": total_amt}
