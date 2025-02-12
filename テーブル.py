import streamlit as st
import sqlite3
import pandas as pd

st.title('データベースを表示するページ')
st.caption('在庫、メニューの一覧が見れる、操作できる')

# データベースファイルのパス（発注管理.pyで使用しているデータベースと同じパス）
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"

# データベース接続用のヘルパー関数
def fetch_data(query):
    conn = sqlite3.connect(db_path)
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

# ── 在庫データの表示 ──
try:
    # inventory テーブルを必要に応じて作成
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
    conn.close()

    # 在庫データ取得
    inventory_data = fetch_data("SELECT * FROM inventory ORDER BY 品目, id")

    if not inventory_data.empty:
        st.write("在庫データ:")

        # 重複する品目は表示上空白に置き換え
        inventory_data["品目"] = inventory_data["品目"].mask(inventory_data["品目"].duplicated(), "")

        # HTMLテーブルの作成
        html_content = ""
        for _, row in inventory_data.iterrows():
            html_content += (
                f"<tr>"
                f"<td>{row['品目']}</td>"
                f"<td>{row['賞味期限']}</td>"
                f"<td>{row['入荷日']}</td>"
                f"<td>{row['個数']}</td>"
                f"</tr>"
            )

        html_table = f"""
        <table border="1" style="width:100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr>
                    <th>品目</th>
                    <th>賞味期限</th>
                    <th>入荷日</th>
                    <th>個数</th>
                </tr>
            </thead>
            <tbody>
                {html_content}
            </tbody>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.write("在庫データはありません。")

except Exception as e:
    st.error(f"在庫データ取得時にエラーが発生しました: {e}")


# ── メニューデータの表示 ──
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredient TEXT,
            quantity INTEGER
        )
    """)
    conn.close()

    menu_data = fetch_data("SELECT * FROM menu")
    if not menu_data.empty:
        st.write("メニューデータ:")

        html_content = ""
        grouped_data = menu_data.groupby("name")  # メニュー名でグループ化

        for menu_name, group in grouped_data:
            html_content += f"<tr><td rowspan='{len(group)}'>{menu_name}</td>"
            for i, row in group.iterrows():
                if i != group.index[0]:
                    html_content += "<tr>"
                html_content += f"<td>{row['ingredient']}</td><td>{row['quantity']}</td></tr>"

        html_table = f"""
        <table border="1" style="width:100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr>
                    <th>メニュー名</th>
                    <th>材料名</th>
                    <th>必要個数</th>
                </tr>
            </thead>
            <tbody>
                {html_content}
            </tbody>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.write("メニューデータはありません。")
except Exception as e:
    st.error(f"メニューデータ取得時にエラーが発生しました: {e}")


# ── 新しいメニューの登録 ──
st.caption('新しいメニューを追加')
if "menu_info" not in st.session_state:
    st.session_state["menu_info"] = []

with st.form(key='menu_form'):
    menu_name = st.text_input('メニュー名')
    num_ingredients = st.number_input('材料の種類数', min_value=1, step=1)
    submit_menu = st.form_submit_button('材料を入力')

    if submit_menu:
        # セッション変数にメニューの材料情報を保持
        for i in range(int(num_ingredients)):
            ingredient_name = st.text_input(f'材料名 {i + 1}', key=f"ingredient_name_{i}")
            ingredient_qty = st.number_input(f'必要個数 {i + 1}', min_value=1, step=1, key=f"ingredient_qty_{i}")
            if ingredient_name and ingredient_qty:
                st.session_state["menu_info"].append({
                    "材料名": ingredient_name,
                    "必要個数": ingredient_qty
                })

        if st.session_state["menu_info"]:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # テーブルが存在しない場合は作成
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS menu (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        ingredient TEXT,
                        quantity INTEGER
                    )
                """)
                # 同じメニュー名のデータが存在するかチェック
                cursor.execute("SELECT COUNT(*) FROM menu WHERE name = ?", (menu_name,))
                existing_count = cursor.fetchone()[0]
                if existing_count > 0:
                    # 既に登録されている場合は古いデータを削除し更新する
                    cursor.execute("DELETE FROM menu WHERE name = ?", (menu_name,))
                # 新しい材料情報を挿入
                for item in st.session_state["menu_info"]:
                    cursor.execute("""
                        INSERT INTO menu (name, ingredient, quantity)
                        VALUES (?, ?, ?)
                    """, (menu_name, item["材料名"], item["必要個数"]))
                conn.commit()
                conn.close()
                st.success("メニューが登録されました！")
                st.session_state["menu_info"] = []
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
