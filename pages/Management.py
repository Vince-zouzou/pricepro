import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st  
import streamlit_shadcn_ui as ui
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_echarts import st_echarts as echart
import pandas as pd
from pages.Chatbox import chatbox

# sample RM: RMname126

@st.cache_data
def load(RMname):
    df = st.session_state['data']['client'].loc[st.session_state['data']['client']['RM Name'] == RMname]
    transdf = st.session_state['data']['transactions'].loc[st.session_state['data']['transactions']['ClientGroup'].isin(df.ClientGroup)]
    return df,transdf 

df,transdf = load('RMname126')
show_cols = {"Client": "ClientGroup",
            "Location":"Location",
            "Cash":"ASSETS_CASH",
            "Mandates":"ASSETS_MANDATES",
            "Loans":"ASSETS_LOANS",
            "Security":"ASSETS_SECURITIES",
            "AuM":"Average Relationship AuM",
            "Revenue":"Total Relationship Revenue",
            "RoA":"RoA",
            "Guidance":"Guidance",
            "Churning" :"Churning"
            }

show_df = df[list(show_cols.values())].rename(columns={v: k for k, v in show_cols.items()}).reset_index(drop = True)

for col in show_df.columns:
    if col not in  ["RoA",'Client','Location',"Churning","Guidance"]:
        show_df[col] = show_df[col].astype(int)

st.session_state.data['show_data'] = {'df':show_df,'text':str(show_df.to_dict(orient = 'records'))}


### ————————————————————————————————————————————Chatbox——————————————————————————————————————————————————

# 修改侧边栏布局
with st.sidebar:
    # 创建一个容器来包装聊天界面
    chat_container = st.container(border=True)
    
    # 添加一些顶部空间
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
    
    # 在容器中显示聊天界面
    with chat_container:
        chatbox()

### ————————————————————————————————————————————Start————————————————————————————————————————————————————

st.title("Welcome ! Mr.Timothy")

# ———————————————————————————————————————————————Cards———————————————————————————————————————————————————
cards = st.container(border=False,)
cols = cards.columns(3)
with cols[0]:
    ui.metric_card(
        title="Total Revenue",
        content="${:,}".format(int(df[show_cols['Revenue']].sum())),
        description="+12.0% from last month",
        key="card1"
    )
with cols[1]:
    ui.metric_card(
        title="Total AuM",
        content="${:,}".format(int(df[show_cols['AuM']].sum())),
        description="+10.1% from last month",
        key="card2"
    )
with cols[2]:
    ui.metric_card(title="Overall RoA", content="{:.2%}".format(df[show_cols['Revenue']].sum()/df[show_cols['AuM']].sum()), description="+1.1% from last month", key="card3")



# ————————————————————————————————————————————————Table————————————————————————————————————————————————
def to_client():
    # 跳转界面 + session_state改变
    if table.selection['rows']:
        row = table.selection['rows'][0]
        clientname = show_df.loc[row, "Client"]
        st.session_state['Client'] = clientname
        #st.switch_page(st.Page("Profile.py"))


datatable = st.container(border=False)
# 删除原有的格式化代码，替换为以下内容：

def style_dataframe(df):
    """
    统一设置 DataFrame 的显示样式
    除了 Client 和 Location 列外，每列根据值的排序（排名）应用红到绿的渐变背景
    """
    # 设置数值格式化字典
    format_dict = {}
    
    # 设置百分比格式
    for col in ["RoA", "Guidance", "Churning"]:
        format_dict[col] = "{:.2%}"
    
    # 设置千位分隔符格式
    for col in df.columns:
        if col not in ["RoA", "Guidance", "Churning", "Client", "Location"]:
            format_dict[col] = "{:,}"
    
    # 应用基本样式
    styled_df = df.style\
        .format(format_dict, na_rep="")\
        .set_properties(**{
            'text-align': 'right',
            'font-size': '14px',
            'padding': '5px 15px'
        })\
        .set_table_styles([
            {'selector': 'th',
             'props': [('font-size', '14px'),
                      ('text-align', 'center'),
                      ('background-color', '#f0f2f6'),
                      ('color', 'black'),
                      ('font-weight', 'bold'),
                      ('padding', '5px 15px')]
            }
        ])
    
    # 对除了 Client 和 Location 外的每列应用基于排名的渐变
    for col in df.columns:
        if col not in ["Client", "Location"]:
            # 计算排名（ascending=True 使最小值排名最低）
            ranks = df[col].rank(ascending=True, method='min', na_option='keep')
            # 归一化排名到 [0, 1] 区间
            if ranks.notna().any():
                vmin = ranks.min()
                vmax = ranks.max()
                if vmin != vmax:  # 避免所有值相同导致除零
                    normalized_ranks = (ranks - vmin) / (vmax - vmin)
                    # 应用渐变，使用归一化的排名
                    styled_df = styled_df.background_gradient(
                        cmap='RdYlGn',
                        subset=[col],
                        vmin=0,
                        vmax=1,
                        gmap=normalized_ranks
                    )
                else:
                    # 如果所有值相同，应用单一颜色（可选：跳过或设置默认颜色）
                    styled_df = styled_df.background_gradient(
                        cmap='RdYlGn',
                        subset=[col],
                        vmin=0,
                        vmax=1,
                        gmap=ranks * 0 + 0.5  # 中间颜色（黄色）
                    )
    
    return styled_df
# 应用样式到数据框
styled_show_df = style_dataframe(show_df)

# 在 datatable 容器中显示样式化的数据框
with datatable:
    table = st.dataframe(
        styled_show_df,
        use_container_width=True,
        key='client_table',
        selection_mode='single-row',
        on_select=to_client,
        hide_index=True,
        row_height=35,
        height=35*(len(show_df)+1)
    )
