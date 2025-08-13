import html
import re
import os 
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

import base64

def get_image_path():


    return "./pages/AI Brain.png"

def get_image_base64():
    with open(get_image_path(), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def format_message(text):
    """
    This function is used to format the messages in the chatbot UI.

    Parameters:
    text (str): The text to be formatted.
    """
    text_blocks = re.split(r"```[\s\S]*?```", text)
    code_blocks = re.findall(r"```([\s\S]*?)```", text)

    text_blocks = [html.escape(block) for block in text_blocks]

    formatted_text = ""
    for i in range(len(text_blocks)):
        formatted_text += text_blocks[i].replace("\n", "<br>")
        if i < len(code_blocks):
            formatted_text += f'<pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{html.escape(code_blocks[i])}</code></pre>'

    return formatted_text


def message_func(text, is_user=False, is_df=False, model="gpt"):
    """
    This function displays messages in the chatbot UI, ensuring proper alignment and avatar positioning.

    Args:
    text (str): The text to be displayed.
    is_user (bool, optional): Whether the message is from the user or not. Defaults to False.
    is_df (bool, optional): Whether the message is a dataframe or not. Defaults to False.
    model (str, optional): The model used to generate the message. Defaults to "gpt".

    Returns:
    None

    """
    """
    This function displays messages in the chatbot UI, ensuring proper alignment and avatar positioning.

    Parameters:
    text (str): The text to be displayed.
    is_user (bool): Whether the message is from the user or not.
    is_df (bool): Whether the message is a dataframe or not.
    """
    message_bg_color = (
        "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)" if is_user else "#71797E"
    )
    avatar_class = "user-avatar" if is_user else "bot-avatar"
    alignment = "flex-end" if is_user else "flex-start"
    margin_side = "margin-left" if is_user else "margin-right"
    message_text = html.escape(text.strip()).replace('\n', '<br>')

    if message_text:  # Check if message_text is not empty
        if is_user:
            # 用户消息（右侧）使用猫咪emoji做为头像示例
            container_html = f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin:0; padding:0; margin-bottom:10px;">
                <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-right:5px; max-width:75%; font-size:18px; margin:0; line-height:1.2; word-wrap:break-word;">
                    {message_text}
                </div>
                <div style="width:40px; height:40px; margin:0; font-size:30px; line-height:40px; text-align:center;">🤔</div>
            </div>
            """
        else:
            # 助手消息（左侧）使用机器人emoji做为头像示例
            container_html = f"""
        <div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0; padding:0; margin-bottom:10px;">
            <div style="width:30px; height:30px; margin:0; margin-right:5px; margin-top:5px;">
                <img src="data:image/png;base64,{get_image_base64()}">
            </div>
            <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-left:5px; max-width:75%; font-size:18px; margin:0; line-height:1.2; word-wrap:break-word;">
                {message_text}
            </div>
        </div>
        """
        st.write(container_html, unsafe_allow_html=True)



class StreamlitUICallbackHandler(BaseCallbackHandler):
    def __init__(self,model):
        """
        类的初始化方法。

        Args:
        model (object): 使用的模型对象。

        Attributes:
        token_buffer (list): 用于存储标记的缓冲区。
        placeholder (st.empty): 一个空的Streamlit占位符，用于动态显示内容。
        has_streaming_ended (bool): 一个布尔值，表示流是否已经结束。
        has_streaming_started (bool): 一个布尔值，表示流是否已经开始。
        final_message (str): 流结束时的最终消息。
        model (object): 传入的模型对象。
        """
        self.token_buffer = []
        self.placeholder = st.empty()
        self.has_streaming_ended = False
        self.has_streaming_started = False
        self.final_message = ""
        self.model = model
    def start_loading_message(self):
        loading_message_content = self._get_bot_message_container("Thinking...")
        self.placeholder.markdown(loading_message_content, unsafe_allow_html=True)

    def on_llm_new_token(self, token, run_id, parent_run_id=None, **kwargs):
        if not self.has_streaming_started:
            self.has_streaming_started = True

        self.token_buffer.append(str(token))
        complete_message = "".join(self.token_buffer)
        container_content = self._get_bot_message_container(complete_message)
        self.placeholder.markdown(container_content, unsafe_allow_html=True)
        self.final_message = "".join(self.token_buffer)

    def on_llm_end(self, response, run_id, parent_run_id=None, **kwargs):
        self.token_buffer = []
        self.has_streaming_ended = True
        self.has_streaming_started = False

    def _get_bot_message_container(self, text):
        """Generate the bot's message container style for the given text."""
        formatted_text = format_message(text.strip())
        if not formatted_text:
            formatted_text = "Thinking..."
        container_content = f"""
    <div style="display:flex; flex-direction:flex-start; align-items:float; justify-content:flex-start; margin:0; padding:0;">
        <div style="width:30px; height:30px; margin:0; margin-right:5px; margin-top:5px;">
           <img src="data:image/png;base64,{get_image_base64()}">
        </div>
        <div style="background:#71797E; color:white; border-radius:20px; padding:10px; margin-top:5px; max-width:75%; font-size:18px; line-height:1.2; word-wrap:break-word;">
            {formatted_text}
        </div>
    </div>
    """
        return container_content


    def display_dataframe(self, df):
        """
        Display the dataframe in Streamlit UI within the chat container.
        """
        message_alignment = "flex-start"
        avatar_class = "bot-avatar"

        st.write(
            f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px; justify-content: {message_alignment};">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(df)


    def __call__(self, *args, **kwargs):
        pass

