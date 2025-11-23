import os
import streamlit as st
from backend import classify_message

st.set_page_config(page_title="스미싱 가디언", page_icon="📭", layout="centered")

# UI 스타일 지정 (모바일 비율 및 디자인 적용 + 사용자/AI 정렬 구분)
st.markdown("""
    <style>
    .main {
        background-color: white !important;
        max-width: 480px;
        margin: auto;
        padding: 1.5rem;
        font-family: 'Apple SD Gothic Neo', sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .stChatMessage.user {
        display: flex;
        justify-content: flex-end;
        text-align: right;
    }
    .stChatMessage.user .element-container {
        background-color: #f0f4ff;
        color: black;
        padding: 1rem;
        border-radius: 10px;
        max-width: 80%;
    }
    .stChatMessage.assistant {
        display: flex;
        justify-content: flex-start;
        text-align: left;
    }
    .stChatMessage.assistant .element-container {
        background-color: #fef9c3;
        color: black;
        padding: 1rem;
        border-radius: 10px;
        max-width: 80%;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤔 의심스러운 문자를 받으셨나요?")
st.caption("AI가 실제 사례 기반으로 스미싱 가능성을 분석해드립니다.")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "retry_trigger" not in st.session_state:
    st.session_state["retry_trigger"] = None

# 사용자 입력 받기 또는 다시 검사 트리거
user_input = st.chat_input("✉️ 여기에 의심 문자를 붙여넣어 주세요")
if user_input or st.session_state["retry_trigger"] is not None:
    target_input = user_input if user_input else st.session_state["retry_trigger"]

    # 사용자 메시지를 출력
    user_msg = {"role": "user", "content": target_input}
    st.session_state["messages"].append(user_msg)

    with st.spinner("AI가 메시지를 분석 중입니다..."):
        result = classify_message(target_input)

    confidence = float(result['confidence']) if isinstance(result['confidence'], float) else float(str(result['confidence']).replace('%', '').strip())
    ai_msg = {
        "role": "assistant",
        "content": f"""
        ### ✅ 판단 결과
        **최종 판단:** `{result['label']}`  
        **위험도:** `{confidence}%`  
        **판단 근거:**  
        {result['reason']}
        """
    }

    st.session_state["messages"].append(ai_msg)
    st.session_state["retry_trigger"] = None

# 메시지 출력 및 메시지별 검사 버튼 렌더링
for idx in range(len(st.session_state["messages"])):
    msg = st.session_state["messages"][idx]
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    # 사용자 메시지 아래에만 다시 검사 버튼 추가
    if msg["role"] == "user":
        if st.button("🔁 다시 검사하기", key=f"retry_{idx}"):
            st.session_state["retry_trigger"] = msg["content"]
            st.rerun()

    # 각 assistant 메시지에 따라 가이드 출력
    if msg["role"] == "assistant" and "판단 결과" in msg["content"]:
        with st.expander("📢 대응 가이드 보기"):
            st.markdown("""
            - **문자에 포함된 링크를 클릭하지 마세요.**
            - **의심스러운 번호로 전화하지 마세요.**
            - 이미 클릭했다면 **금융 앱, 공인인증서 등을 삭제**하고,
              가까운 경찰서 또는 금융감독원에 신고하세요.
            """)
            st.button("📨 보호자에게 알리기", disabled=True, key=f"guardian_alert_{idx}")

        with st.expander("🔍 피해 여부 확인하기"):
            st.markdown("""
            이미 클릭했거나, 앱 설치 등이 의심된다면 아래를 확인해보세요.
            - 휴대폰에 알 수 없는 앱이 설치되어 있지 않나요?
            - 통신사, 은행으로부터 비정상적인 알림을 받지 않았나요?
            - 의심 문자 수신 후 **정보 유출 알림**을 받은 적 있나요?
            """)
            st.button("피해 점검 도구 연결 (준비 중)", disabled=True, key=f"check_tool_{idx}")

        with st.expander("🔎 링크 클릭 여부 확인"):
            clicked = st.radio(
                label="이 문자에 포함된 링크를 클릭하셨나요?",
                options=["아니요", "예, 클릭했습니다"],
                key=f"clicked_radio_{idx}"
            )

        with st.expander("📌 클릭 여부에 따른 대응 가이드"):
            if clicked == "아니요":
                st.markdown("""
                - 문자에 포함된 링크를 클릭하지 않은 경우에도 주의가 필요합니다.
                - 의심 번호로 전화하거나 회신하지 마세요.
                """)
            else:
                st.markdown("""
                - **즉시 비행기 모드 전환**
                - **모든 금융 앱 및 공인인증서 삭제**
                - **백신 앱 전체 검사 후 재부팅**
                - **은행 및 인증서 비밀번호 변경**
                - **가까운 경찰서 또는 금융감독원에 문의**
                """)
