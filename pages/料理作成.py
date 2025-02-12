# pages/料理作成.py
import streamlit as st
import sqlite3
import pandas as pd

st.title('作るメニューと個数を入力するページ')
st.caption('登録された料理のレシピに基づき、在庫データから賞味期限の近いものから材料を減らします')

# 共通のデータベースファイル（発注管理.db）を利用
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"

def create_ryouri_table():
    """料理登録用テーブル（ryouri）がなければ作成"""
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

# セッション変数の初期化（料理数および各入力項目を保持）
if "ryouri_kinds" not in st.session_state:
    st.session_state["ryouri_kinds"] = 1
if "ryouri_inputs" not in st.session_state:
    st.session_state["ryouri_inputs"] = {}

# ── 料理数入力フォーム ──
with st.form(key='ryouri_kinds_form'):
    kinds = st.number_input('料理数', min_value=1, step=1, value=st.session_state["ryouri_kinds"], key="ryouri_kinds_input")
    submit_kinds = st.form_submit_button('料理数を登録')
    if submit_kinds:
        st.session_state["ryouri_kinds"] = int(kinds)
        st.experimental_rerun()

# ── 各料理の入力欄（料理名・個数） ──
for i in range(st.session_state["ryouri_kinds"]):
    name_key = f"ryouri_name_{i}"
    qty_key = f"ryouri_quantity_{i}"
    # 初回は初期値を設定
    if name_key not in st.session_state["ryouri_inputs"]:
        st.session_state["ryouri_inputs"][name_key] = ""
    if qty_key not in st.session_state["ryouri_inputs"]:
        st.session_state["ryouri_inputs"][qty_key] = 1
    st.session_state["ryouri_inputs"][name_key] = st.text_input(f'料理名 {i+1}', value=st.session_state["ryouri_inputs"][name_key], key=name_key)
    st.session_state["ryouri_inputs"][qty_key] = st.number_input(f'個数 {i+1}', min_value=1, step=1, value=st.session_state["ryouri_inputs"][qty_key], key=qty_key)

# ── 料理登録ボタン ──
if st.button('料理の登録'):
    ryouri_info_list = []
    for i in range(st.session_state["ryouri_kinds"]):
        name = st.session_state.get(f"ryouri_name_{i}")
        qty = st.session_state.get(f"ryouri_quantity_{i}")
        if name and qty:
            ryouri_info_list.append({"name": name, "quantity": qty})
    if not ryouri_info_list:
        st.error("料理情報が入力されていません。")
    else:
        # データベース接続開始
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 各料理について、レシピ（menuテーブル）を参照して必要な材料を在庫から減らす
        for dish in ryouri_info_list:
            dish_name = dish["name"]
            dish_qty = dish["quantity"]

            # menuテーブルから該当料理のレシピを取得
            cursor.execute("SELECT ingredient, quantity FROM menu WHERE name = ?", (dish_name,))
            recipe_rows = cursor.fetchall()
            if not recipe_rows:
                st.warning(f"レシピが見つかりませんでした: {dish_name}")
                continue  # 該当レシピがなければ次の料理へ

            st.write(f"【{dish_name}】 {dish_qty}品作成のための材料消費")
            # 各材料について処理
            for ingredient, recipe_qty in recipe_rows:
                total_required = recipe_qty * dish_qty
                st.write(f"- 材料：{ingredient} 必要数：{total_required}")

                # 在庫テーブルから、該当材料のレコードを賞味期限の近い順に取得
                cursor.execute("""
                    SELECT id, 個数, 賞味期限 
                    FROM inventory 
                    WHERE 品目 = ? AND 個数 > 0 
                    ORDER BY 賞味期限 ASC
                """, (ingredient,))
                inventory_rows = cursor.fetchall()
                remaining = total_required

                for inv_id, available, expiration in inventory_rows:
                    if available >= remaining:
                        new_value = available - remaining
                        cursor.execute("UPDATE inventory SET 個数 = ? WHERE id = ?", (new_value, inv_id))
                        st.write(f"  -> 在庫ID {inv_id} の在庫を {available} から {new_value} に更新")
                        remaining = 0
                        break
                    else:
                        # 在庫が足りない場合は、在庫をゼロにして次のレコードへ
                        cursor.execute("UPDATE inventory SET 個数 = 0 WHERE id = ?", (inv_id,))
                        st.write(f"  -> 在庫ID {inv_id} の在庫 {available} を全て使用")
                        remaining -= available

                if remaining > 0:
                    st.warning(f"  ※ 材料 {ingredient} の在庫が不足しています。必要数 {total_required} のうち {total_required - remaining} しか減算できませんでした。")
                else:
                    st.success(f"  → 材料 {ingredient} の在庫を必要数分減算しました。")

            # 料理自体の登録（ryouriテーブルに記録）
            cursor.execute("""
                INSERT INTO ryouri (name, quantity)
                VALUES (?, ?)
            """, (dish_name, dish_qty))
        
        conn.commit()
        conn.close()
        st.success("料理登録と在庫の更新が完了しました。")
        st.session_state["ryouri_inputs"] = {}  # 入力欄のリセット（必要に応じて）
        create_ryouri_table()  # 料理登録テーブルの初期化（存在しない場合のみ作成）
