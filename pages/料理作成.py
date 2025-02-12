# pages/料理作成.py
import streamlit as st
import sqlite3
import pandas as pd

st.title('作るメニューと個数を入力するページ')
st.caption('消費する材料の個数を計算してデータベースを編集する')

# データベースファイルのパス（発注管理.db を共通利用）
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"

def create_ryouri_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ryouri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

# セッション変数の初期化
if "ryouri_kinds" not in st.session_state:
    st.session_state["ryouri_kinds"] = 1
if "ryouri_inputs" not in st.session_state:
    st.session_state["ryouri_inputs"] = {}

# ── 料理数の入力（on_change を利用して動的入力欄を更新） ──
def update_ryouri_kinds():
    st.session_state["ryouri_kinds"] = st.session_state["ryouri_kinds_input"]
    # 各料理入力欄に対して初期値を設定
    for i in range(int(st.session_state["ryouri_kinds"])):
        st.session_state["ryouri_inputs"].setdefault(f"ryouri_name_{i}", "")
        st.session_state["ryouri_inputs"].setdefault(f"ryouri_quantity_{i}", 1)

st.number_input(
    '料理数',
    min_value=1,
    step=1,
    key="ryouri_kinds_input",
    value=st.session_state["ryouri_kinds"],
    on_change=update_ryouri_kinds
)

# ── 動的入力欄の表示 ──
for i in range(int(st.session_state["ryouri_kinds"])):
    name_key = f"ryouri_name_{i}"
    qty_key = f"ryouri_quantity_{i}"
    st.session_state["ryouri_inputs"][name_key] = st.text_input(
        f'料理名 {i+1}', 
        value=st.session_state["ryouri_inputs"].get(name_key, ""), 
        key=name_key
    )
    st.session_state["ryouri_inputs"][qty_key] = st.number_input(
        f'個数 {i+1}', 
        min_value=1, 
        step=1, 
        value=st.session_state["ryouri_inputs"].get(qty_key, 1), 
        key=qty_key
    )

# ── 料理登録と在庫更新処理 ──
if st.button('料理の登録'):
    ryouri_info_list = []
    for i in range(int(st.session_state["ryouri_kinds"])):
        name = st.session_state.get(f"ryouri_name_{i}")
        qty = st.session_state.get(f"ryouri_quantity_{i}")
        if name and qty:
            ryouri_info_list.append({"name": name, "quantity": qty})
    if not ryouri_info_list:
        st.error("料理情報が入力されていません。")
    else:
        # ここで、各料理に対してレシピ（menu テーブル）から必要な材料を取得し、
        # 在庫（inventory テーブル）から賞味期限の近いものから減算する処理を実施できます。
        #
        # 例：
        #   for dish in ryouri_info_list:
        #       cursor.execute("SELECT ingredient, quantity FROM menu WHERE name = ?", (dish["name"],))
        #       recipe = cursor.fetchall()
        #       for ingredient, recipe_qty in recipe:
        #           必要数 = recipe_qty * dish["quantity"]
        #           在庫から該当材料を賞味期限順に取得し、必要数分を減算
        #
        # 今回はデータ登録処理のみ実装し、在庫更新ロジックは既存の実装例に合わせて追加してください。

        create_ryouri_table()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for entry in ryouri_info_list:
            cursor.execute(
                """
                INSERT INTO ryouri (name, quantity)
                VALUES (?, ?)
                """,
                (entry["name"], entry["quantity"])
            )
        conn.commit()
        conn.close()
        st.success("料理データがデータベースに保存されました！")
        st.session_state["ryouri_inputs"] = {}

# ── 登録済み料理データの表示 ──
if st.button('登録された料理データを表示'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ryouri")
    ryouri_data = cursor.fetchall()
    if ryouri_data:
        st.write("登録された料理データ:")
        ryouri_df = pd.DataFrame(ryouri_data, columns=["ID", "料理名", "個数"])
        st.write(ryouri_df)
    else:
        st.write("登録された料理データはありません。")
    conn.close()
