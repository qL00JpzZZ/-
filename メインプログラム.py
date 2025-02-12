import streamlit as st
from PIL import Image

# ポップボタンを表示する関数
def pop_btn(label="pop", key=None, layer=0, onclick=lambda: None, done=None, description=None):
    placeholder = st.empty()  # プレースホルダーを作成
    with placeholder.container():
        if description:
            st.write(description)
        # ボタンのクリック時に処理を実行
        res = st.button(label, key=key, on_click=lambda: [placeholder.empty(), layer_session(layer), onclick()])
    if res and done:
        with placeholder:
            done()
            placeholder.empty()

# レイヤーの管理関数
def layer_session(layer=0):
    st.session_state.layer = layer

# done 処理のサンプル
def sample_done():
    st.write("ボタンが押されました！")

# 画像を表示
image = Image.open('./pic/databaseImage.jpg')
st.image(image, width=200)

# ポップボタンの表示
pop_btn(
    label="ポップボタンをクリック！",
    layer=1,
    onclick=lambda: st.write("ボタンがクリックされました！"),
    done=sample_done,
    description="このボタンをクリックして、メッセージを表示します。"
)
