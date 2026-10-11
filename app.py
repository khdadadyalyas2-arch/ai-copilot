import os
import json
import streamlit as st
from openai import OpenAI
from tools import TOOLS_SCHEMA, TOOL_MAP

st.set_page_config(page_title="دستیار هوشمند همه‌کاره", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    div[data-testid="stChatMessage"] { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 دستیار هوش مصنوعی همه‌کاره")
st.caption("آماده برای انجام امور تحلیلی، محاسباتی و پاسخ به پرسش‌ها")

with st.sidebar:
    st.header("⚙️ تنظیمات API")
    api_key = st.text_input("OpenAI / GitHub API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    base_url = st.text_input("Base URL (اختیاری)", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

if not api_key:
    st.info("رفیق، لطفاً کلید API را در منوی کناری وارد کن.")
    st.stop()

client = OpenAI(api_key=api_key, base_url=base_url)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "تو یک دستیار هوش مصنوعی بسیار باهوش و همه‌کاره هستی که به زبان فارسی صمیمی و دقیق پاسخ می‌دهی. در صورت نیاز از ابزارها استفاده کن."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_prompt = st.chat_input("از من هر کاری یا سوالی داری بپرس...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                if func_name in TOOL_MAP:
                    tool_result = TOOL_MAP[func_name](func_args)
                    st.session_state.messages.append({
                        "role": "function",
                        "name": func_name,
                        "content": str(tool_result)
                    })
            second_res = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages
            )
            final_reply = second_res.choices[0].message.content
        else:
            final_reply = msg.content

        st.session_state.messages.append({"role": "assistant", "content": final_reply})
        with st.chat_message("assistant"):
            st.write(final_reply)

    except Exception as e:
        st.error(f"خطایی رخ داد: {e}")
