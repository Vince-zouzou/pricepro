import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
import streamlit as st
from resources.UIs.ChatboxUI import message_func,StreamlitUICallbackHandler  # 保留用于消息展示的函数
import time 
from backend.Model import Talker
import base64
from streamlit_shadcn_ui import button 
#from agent import create_agent
warnings.filterwarnings("ignore")

def get_image_path():


    return "./pages/AI Brain.png"

def get_image_base64():
    with open(get_image_path(), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def chatbox():
    cue = """
    You are a professional data analyst and I am a Relationship manager in a private bank, you are here to assist me with analysising my clients in my book to help me to make know my clients better and develop potential opportunity.
    The first thing you need to do is : Understand my query and analysis my intention to see if I really need you to help me with my book or just chatting. If I am just want a small chat, you can answer to my questions or just chat with my or tell me a small joke.
    If my query is about knowing my book or knowing clients, you need to strictedly follow the belowing instruction:{1. find the relavent information in my book;2. Give me a summary about the book;3.Answer my question;4.think about if there is anything else you can help me to achieve better revenue and RoA, and give me detailed instructions}
    Your response should consider the information of the whole book as well, use the performance of the whole book as default benchmark and compare with the bechmark unless user suggests new benchmark.
    Your response should fully consider the chat history information to make the response more accurate and relevant to users idea.
    """
    talker = Talker()


    initial  = "Hi, Mr.Timothy, How you want to know your book today?"
    gradient_text_html = f"""
    <div style="display: flex; align-items: center; justify-content: left; font-size: 30 px;">
                                <!-- 👑正常显示 -->
                                <span style="font-size: 10px;"><img src="data:image/png;base64,{get_image_base64()}" 
                                            style="width: 35px; height: 35px; object-fit: contain;"></span>
                                <!-- 渐变字体 Pro -->
                                <span style="font-weight: bold; 
                                            background: -webkit-linear-gradient(left, red, orange);
                                            background: linear-gradient(to right, red, orange);
                                            -webkit-background-clip: text;
                                            -webkit-text-fill-color: transparent;
                                            margin-left: 0px;">
                                    SKAI - SKAI is the limit
                                </span>
                            </div>
    """
    col0 = st.columns([10])[0]
    col0.markdown(gradient_text_html, unsafe_allow_html=True)
    #st.header("Talk your way through data")


    INITIAL_MESSAGE = [
        {
            "role": "assistant",
            "content": f"{initial}"    },
    ]
    with open("resources\\UIs\\styles.md", "r") as styles_file:
        styles_content = styles_file.read()


    if st.button("Reset Message",width='stretch',type="primary"):

        st.session_state["data_messages"] = INITIAL_MESSAGE
        st.session_state["data_history"] = []
    

    
    st.write(styles_content, unsafe_allow_html=True)

    if "data_messages" not in st.session_state.keys():
        st.session_state["data_messages"] = INITIAL_MESSAGE

    if "data_history" not in st.session_state:
        st.session_state["data_history"] = []




    messages_to_display = st.session_state["data_messages"].copy()
    
    box = st.container(key="Chatbox",border=False)    
    conversation = box.container(key= "Chat",border=True,height = 700)
    inputbox = box.container(key= "Input",border=False)
    
    with inputbox:
        if prompt := st.chat_input():
            if len(prompt) > 500:
                st.error("Input is too long! Please limit your message to 500 characters.")
            else:
                st.session_state["data_messages"].append({"role": "user", "content": prompt})
                st.session_state["assistant_response_processed"] = False
            
            messages_to_display = st.session_state["data_messages"].copy()
            
            
    with conversation:
        for message in messages_to_display:
            message_func(
                message["content"],
                is_user=(message["role"] == "user"),
                is_df=(message["role"] == "data"),
            )


    

    def append_message(content, role="assistant"):
        """Appends a message to the session state messages."""
        if content.strip():
            st.session_state["data_messages"].append({"role": role, "content": content})
            
    with conversation:
        callback_handler = StreamlitUICallbackHandler("")
        if (
            "data_messages" in st.session_state
            and st.session_state["data_messages"][-1]["role"] == "user"
            and not st.session_state["assistant_response_processed"]
        ):
            user_input_content = st.session_state["data_messages"][-1]["content"]

            if isinstance(user_input_content, str):
                # Start loading animation
                callback_handler.start_loading_message()
                final_input = user_input_content + "The following is all clients' information in my book : ({})".format(st.session_state.data['show_data']['text'])
                cue += "The following is all clients' information in my book : ({})".format(st.session_state.data['show_data']['text'])
                
                ## to add historical information
                history_string = "Chat History:"
                if len(st.session_state["data_messages"]) > 6:
                    for item in st.session_state["data_messages"][-1:-7]:
                        history_string = history_string + "(" + item['role']+":"+item["content"] + ");"
                    cue = history_string + cue
                else:                    
                    for item in st.session_state["data_messages"]:
                        history_string = history_string + "(" + item['role']+":"+item["content"] + ");"
                    cue = history_string + cue
                    
                #t.write(st.session_state["data_messages"])
                response = talker.get_response(final_input, cue)
                words = [str(i) for i in response ]
                
                
                for w in words:
                    callback_handler.on_llm_new_token(w, run_id="fixed_run_id")
                    #time.sleep(0.001)  # 可选：模拟思考延迟
                # 输出完成后调用on_llm_end
                callback_handler.on_llm_end(response={"final": "done"}, run_id="fixed_run_id")
                # 此时 callback_handler.final_message 就是固定输出的完整文本
                assistant_message = callback_handler.final_message
                append_message(assistant_message)
                #append_message(response)
                st.session_state["assistant_response_processed"] = True











