# pages/発注管理.py
import os
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.title('材料の入荷を操作するページ')

# データベースファイルのパスを指定
db_directory = "C:/zaiko/inventory_manegement/test_app"
db_path = os.path.join(db_directory, "発注管理.db")

# ディレクトリが存在しない場合は作成
if not os.path.exists(db_directory):
    os.makedirs(db_directory)

# テーブル作成関数（inventoryテーブル）
def create_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            品目 TEXT,
            賞味期限 TEXT,
            入荷日 TEXT,
            個数 INTEGER
        )
    """)
    conn.commit()
    conn.close()

# 発注データ登録用関数
def insert_hacchuu_data(data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for entry in data:
        cursor.execute("""
            INSERT INTO inventory (品目, 賞味期限, 入荷日, 個数)
            VALUES (?, ?, ?, ?)
        """, (entry["品目"], entry["賞味期限"], str(entry["入荷日"]), entry["個数"]))
    conn.commit()
    conn.close()

# 初期化
create_tables()

# セッション変数の初期化
if "hacchuu_info" not in st.session_state:
    st.session_state["hacchuu_info"] = []
if "current_inputs" not in st.session_state:
    st.session_state["current_inputs"] = {}
if "hacchuu_kinds" not in st.session_state:
    st.session_state["hacchuu_kinds"] = 1
if "rerun" not in st.session_state:
    st.session_state["rerun"] = False

# フォーム外でフラグをチェックし、再実行（これによりフォーム内で直接st.experimental_rerun()を呼び出さない）
if st.session_state.get("rerun", False):
    st.session_state["rerun"] = False
    st.experimental_rerun()

# ── 品目数入力用フォーム ──
with st.form(key='hacchuu_form'):
    kinds = st.number_input('品目数', min_value=1, step=1,
                              value=st.session_state["hacchuu_kinds"],
                              key='hacchuu_kinds_input')
    submit_button = st.form_submit_button('品目数を登録')
    if submit_button:
        st.session_state["hacchuu_kinds"] = kinds
        # 入力欄の初期化（各品目の入力値を保持）
        for i in range(int(kinds)):
            st.session_state["current_inputs"][f"hacchuu_name_{i}"] = st.session_state.get(f"hacchuu_name_{i}", "")
            st.session_state["current_inputs"][f"hacchuu_expiration_{i}"] = st.session_state.get(f"hacchuu_expiration_{i}", date.today())
            st.session_state["current_inputs"][f"hacchuu_date_{i}"] = st.session_state.get(f"hacchuu_date_{i}", date.today())
            st.session_state["current_inputs"][f"hacchuu_quantity_{i}"] = st.session_state.get(f"hacchuu_quantity_{i}", 1)
        # フォーム外で再実行するためのフラグをセット
        st.session_state["rerun"] = True

# ── 動的入力欄の表示 ──
for i in range(int(st.session_state.get('hacchuu_kinds', 1))):
    st.text_input(f'品目 {i + 1}',
                  value=st.session_state["current_inputs"].get(f"hacchuu_name_{i}", ""),
                  key=f"hacchuu_name_{i}")
    st.date_input(f'賞味期限 {i + 1}',
                  value=st.session_state["current_inputs"].get(f"hacchuu_expiration_{i}", date.today()),
                  key=f"hacchuu_expiration_{i}")
    st.date_input(f'入荷日 {i + 1}',
                  value=st.session_state["current_inputs"].get(f"hacchuu_date_{i}", date.today()),
                  key=f"hacchuu_date_{i}")
    st.number_input(f'個数 {i + 1}',
                    value=st.session_state["current_inputs"].get(f"hacchuu_quantity_{i}", 1),
                    min_value=1,
                    step=1,
                    key=f"hacchuu_quantity_{i}")

# ── データベースへの登録ボタン ──
if st.button("データベースに登録"):
    for i in range(int(st.session_state.get('hacchuu_kinds', 1))):
        name = st.session_state.get(f"hacchuu_name_{i}")
        expiration_date = st.session_state.get(f"hacchuu_expiration_{i}")
        arrival_date = st.session_state.get(f"hacchuu_date_{i}")
        quantity = st.session_state.get(f"hacchuu_quantity_{i}")
        st.session_state["hacchuu_info"].append({
            "品目": name,
            "賞味期限": expiration_date,
            "入荷日": arrival_date,
            "個数": quantity
        })

    if st.session_state["hacchuu_info"]:
        insert_hacchuu_data(st.session_state["hacchuu_info"])
        st.success("発注品が登録されました！")
        st.session_state["hacchuu_info"] = []       # 登録後にリセット
        st.session_state["current_inputs"] = {}      # フォームのリセット

# ── 登録済み発注データ表示ボタン ──
if st.button('新規発注データを表示'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    hacchuu_data = cursor.fetchall()
    if hacchuu_data:
        st.write("在庫データ:")
        hacchuu_df = pd.DataFrame(hacchuu_data, columns=["ID", "品目", "賞味期限", "入荷日", "個数"])
        st.write(hacchuu_df)
    else:
        st.write("在庫データはありません。")
    conn.close()
