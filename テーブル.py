import streamlit as st
import sqlite3
import pandas as pd

st.title('データベースを表示するページ')
st.caption('在庫、メニューの一覧が見れる、操作できる')

# データベースファイルのパス
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"  # 発注管理.pyで使用しているデータベースと同じパス

# データベース接続
def fetch_data(query):
    conn = sqlite3.connect(db_path)
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data


# データ表示処理
try:
    # テーブル作成（必要な場合）
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

    # データ取得
    inventory_data = fetch_data("SELECT * FROM inventory ORDER BY 品目, id")  # 品目ごとにソート

    if not inventory_data.empty:
        st.write("在庫データ:")

        # 重複する品目を空白に置き換える
        inventory_data["品目"] = inventory_data["品目"].mask(inventory_data["品目"].duplicated(), "")

        # HTMLテーブル作成
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

        # HTMLテーブル全体
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
        # HTMLを表示
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.write("在庫データはありません。")

except Exception as e:
    st.error(f"在庫データ取得時にエラーが発生しました: {e}")



    
    
    
    
    
# メニューデータを取得
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

        # データを「結合して表示する」形式に加工
        html_content = ""
        grouped_data = menu_data.groupby("name")  # メニュー名でグループ化

        for menu_name, group in grouped_data:
            # グループごとのHTMLを生成
            html_content += f"<tr><td rowspan='{len(group)}'>{menu_name}</td>"
            for i, row in group.iterrows():
                if i != group.index[0]:
                    html_content += "<tr>"
                html_content += f"<td>{row['ingredient']}</td><td>{row['quantity']}</td></tr>"

        # HTMLテーブルの全体構造
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# 新しいメニューを登録
st.caption('新しいメニューを追加')
if "menu_info" not in st.session_state:
    st.session_state["menu_info"] = []

with st.form(key='menu_form'):
    menu_name = st.text_input('メニュー名')
    num_ingredients = st.number_input('材料の種類数', min_value=1, step=1)
    submit_menu = st.form_submit_button('材料を入力')

    if submit_menu:
        for i in range(int(num_ingredients)):
            ingredient_name = st.text_input(f'材料名 {i + 1}', key=f"ingredient_name_{i}")
            ingredient_qty = st.number_input(f'必要個数 {i + 1}', min_value=1, step=1, key=f"ingredient_qty_{i}")
            if ingredient_name and ingredient_qty:
                st.session_state["menu_info"].append({
                    "材料名": ingredient_name,
                    "必要個数": ingredient_qty
                })

        if st.session_state["menu_info"]:
            # メニュー情報をデータベースに保存（仮に「menu」というテーブルを使用）
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
                for item in st.session_state["menu_info"]:
                    cursor.execute("""
                        INSERT INTO menu (name, ingredient, quantity)
                        VALUES (?, ?, ?)
                    """, (menu_name, item["材料名"], item["必要個数"]))
                conn.commit()
                conn.close()
                st.success("メニューが登録されました！")
                st.session_state["menu_info"] = []  # 登録後にセッションをリセット
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
