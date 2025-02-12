# pages/料理作成.py
import streamlit as st
import sqlite3
import pandas as pd

st.title('作るメニューと作る個数を入力するページ')
st.caption('登録された料理のレシピに基づき、在庫から必要な材料を減算します')

# データベースファイルのパス（発注管理.db を共通利用）
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"

# 料理登録用テーブル（ryouri）がなければ作成
def create_ryouri_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ryouri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER
        )
    """)
    conn.commit()
    conn.close()

# 料理作成時に在庫（inventory）から材料を減算する処理
def update_inventory_for_dish(dish_name, dish_qty):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # メニュー（レシピ）から該当料理の材料と必要数を取得
    cursor.execute("SELECT ingredient, quantity FROM menu WHERE name = ?", (dish_name,))
    recipe = cursor.fetchall()
    if not recipe:
        st.warning(f"レシピが見つかりません: {dish_name}")
        conn.close()
        return

    st.write(f"【{dish_name}】 の在庫更新:")
    # 各材料について必要な数量（＝レシピ数量 × 作る個数）を計算し、在庫から減算
    for ingredient, recipe_qty in recipe:
        required = recipe_qty * dish_qty
        st.write(f"- 材料「{ingredient}」 必要数: {required}")

        # 在庫テーブルから該当材料を、賞味期限の近い順に取得
        cursor.execute("""
            SELECT id, 個数, 賞味期限 
            FROM inventory 
            WHERE 品目 = ? AND 個数 > 0 
            ORDER BY 賞味期限 ASC
        """, (ingredient,))
        inv_rows = cursor.fetchall()
        remaining = required
        for inv_id, available, expiration in inv_rows:
            if available >= remaining:
                new_val = available - remaining
                cursor.execute("UPDATE inventory SET 個数 = ? WHERE id = ?", (new_val, inv_id))
                st.write(f"  → 在庫ID {inv_id}: {available} から {new_val} に更新")
                remaining = 0
                break
            else:
                # 在庫が不足している場合はそのレコードを使い切る
                cursor.execute("UPDATE inventory SET 個数 = 0 WHERE id = ?", (inv_id,))
                st.write(f"  → 在庫ID {inv_id}: {available} を全て使用")
                remaining -= available

        if remaining > 0:
            st.warning(f"  ※ 材料「{ingredient}」は在庫不足です。必要 {required} のうち {required - remaining} 減算しましたが、{remaining} 足りません。")
        else:
            st.success(f"  → 材料「{ingredient}」の在庫を必要数分減算しました。")
    conn.commit()
    conn.close()

# --- セッション変数の初期化 ---
# 「調理する料理の種類数」：複数種類の料理を同時に登録するための個数
if "ryouri_kinds" not in st.session_state:
    st.session_state["ryouri_kinds"] = 1
if "ryouri_inputs" not in st.session_state:
    st.session_state["ryouri_inputs"] = {}

# --- 料理の種類数入力（動的入力欄の数を決める） ---
def update_ryouri_kinds():
    st.session_state["ryouri_kinds"] = st.session_state["ryouri_kinds_input"]
    # 各料理入力欄に対して初期値を設定（既存の値は保持）
    for i in range(int(st.session_state["ryouri_kinds"])):
        st.session_state["ryouri_inputs"].setdefault(f"ryouri_name_{i}", "")
        st.session_state["ryouri_inputs"].setdefault(f"ryouri_quantity_{i}", 1)

st.number_input(
    '調理する料理の種類数',  # 種類数（例：和食・洋食など複数の料理を同時に調理する場合）
    min_value=1,
    step=1,
    key="ryouri_kinds_input",
    value=st.session_state["ryouri_kinds"],
    on_change=update_ryouri_kinds
)

# --- 動的入力欄の表示 ---
# 各料理ごとに「料理名」と「作る個数」を入力
for i in range(int(st.session_state["ryouri_kinds"])):
    name_key = f"ryouri_name_{i}"
    qty_key = f"ryouri_quantity_{i}"
    st.session_state["ryouri_inputs"][name_key] = st.text_input(
        f'料理名 {i+1}',
        value=st.session_state["ryouri_inputs"].get(name_key, ""),
        key=name_key
    )
    st.session_state["ryouri_inputs"][qty_key] = st.number_input(
        f'作る個数 {i+1}',
        min_value=1,
        step=1,
        value=st.session_state["ryouri_inputs"].get(qty_key, 1),
        key=qty_key
    )

# --- 料理登録ボタン（在庫更新処理＋料理記録） ---
if st.button('料理の登録'):
    # 収集した料理情報（各料理の名称と作る個数）
    ryouri_info_list = []
    for i in range(int(st.session_state["ryouri_kinds"])):
        dish_name = st.session_state.get(f"ryouri_name_{i}")
        dish_qty = st.session_state.get(f"ryouri_quantity_{i}")
        if dish_name and dish_qty:
            ryouri_info_list.append({"name": dish_name, "quantity": dish_qty})

    if not ryouri_info_list:
        st.error("料理情報が入力されていません。")
    else:
        # 在庫更新と料理の記録を行う
        create_ryouri_table()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for dish in ryouri_info_list:
            dish_name = dish["name"]
            dish_qty = dish["quantity"]

            # 在庫から材料を減算（レシピに基づく）
            update_inventory_for_dish(dish_name, dish_qty)

            # 料理の登録（記録用：後日参照可能）
            cursor.execute("""
                INSERT INTO ryouri (name, quantity)
                VALUES (?, ?)
            """, (dish_name, dish_qty))
        conn.commit()
        conn.close()
        st.success("料理登録と在庫更新が完了しました！")
        st.session_state["ryouri_inputs"] = {}

# --- 登録済み料理データの表示 ---
if st.button('登録された料理データを表示'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ryouri")
    ryouri_data = cursor.fetchall()
    if ryouri_data:
        st.write("登録された料理データ:")
        ryouri_df = pd.DataFrame(ryouri_data, columns=["ID", "料理名", "作る個数"])
        st.write(ryouri_df)
    else:
        st.write("登録された料理データはありません。")
    conn.close()
