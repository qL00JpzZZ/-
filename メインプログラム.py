import streamlit as st
from PIL import Image

# ポップボタンを表示する関数
def pop_btn(label="pop", key=None, layer=0, onclick=lambda: None, done=None, description=None):
    placeholder = st.empty()  # プレースホルダーを作成
    with placeholder.container():  # プレースホルダー内でボタンを配置
        if description:  # ボタンの説明があれば表示
            st.write(description)
        # ボタンのクリック時に処理を実行
        res = st.button(label, key=key, on_click=lambda: [placeholder.empty(), layer_session(layer), onclick()])
    if res and done:
        with placeholder:  # ボタンがクリックされたらdone処理を実行
            done()
            placeholder.empty()

# レイヤーの管理
def layer_session(layer=0):
    st.session_state.layer = layer

# done処理のサンプル
def sample_done():
    st.write("ボタンが押されました！")

# 画像を表示する
image = Image.open('./pic/databaseImage.jpg')
st.image(image, width=200)





# ポップボタンを表示する
pop_btn(
    label="ポップボタンをクリック！",  # ボタンのラベル
    layer=1,  # レイヤーの状態
    onclick=lambda: st.write("ボタンがクリックされました！"),  # ボタンがクリックされた時に実行される処理
    done=sample_done,  # ボタンがクリックされた後に実行される処理
    description="このボタンをクリックして、メッセージを表示します。"  # ボタンの説明
)
