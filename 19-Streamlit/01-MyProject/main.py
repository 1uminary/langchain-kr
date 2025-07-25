import streamlit as st
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_teddynote.prompts import load_prompt
import glob

load_dotenv()

st.title("나만의 챗GPT 만들기")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    clear_btn = st.button("대화 초기화")

    prompt_files = glob.glob("prompts/*.yaml")
    selected_prompt = st.selectbox(
        "프롬프트를 선택해 주세요", prompt_files, index=0
    )
    task_input = st.text_input("TASK 입력", "")

def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)

def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))

def create_chain(prompt_filepath, task=""):
    prompt = load_prompt(prompt_filepath, encoding="utf-8")
    if task:
        prompt = prompt.partial(task=task)

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    return chain

print_messages()

user_input = st.chat_input("궁금한 내용을 물어보세요!")

if user_input:
    st.chat_message("user").write(user_input)
    chain = create_chain(selected_prompt, task=task_input)

    # 선택된 프롬프트 타입에 따라 입력 변수 키를 동적으로 설정
    input_key = "question"
    if selected_prompt == "요약":
        input_key = "ARTICLE"

    response = chain.stream({input_key: user_input})
    with st.chat_message("assistant"):
        container = st.empty()
        
        ai_answer = ""
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)
    
    add_message("user", user_input) # 사용자 메시지 저장
    add_message("assistant", ai_answer) # 챗봇의 실제 응답 저장
