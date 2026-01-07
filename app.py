import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 구글 무료 키(AIza...)를 따옴표 안에 넣어주세요!
# "GOOGLE_API_KEY"라는 이름표를 가진 비밀번호를 가져와! 라고 해야 합니다.
api_key = st.secrets["GOOGLE_API_KEY"]
# ==========================================

# 페이지 설정
st.set_page_config(page_title="보육일지 도우미", page_icon="📝")
st.title("📝 엄마를 위한 보육일지 (Google)")

# --- [핵심] 사용 가능한 모델 자동 찾기 로직 ---
try:
    genai.configure(api_key=api_key)
    
    # 내 키로 쓸 수 있는 모델 목록을 가져옵니다
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    # 가장 성능 좋고 빠른 모델을 우선 선택합니다
    if "models/gemini-1.5-flash" in available_models:
        selected_model = "gemini-1.5-flash"
    elif "models/gemini-pro" in available_models:
        selected_model = "gemini-pro"
    elif len(available_models) > 0:
        selected_model = available_models[0] # 아무거나 되는 거 선택
    else:
        st.error("사용 가능한 AI 모델이 없습니다. API 키를 확인해주세요.")
        selected_model = None

    if selected_model:
        model = genai.GenerativeModel(selected_model)
        # st.success(f"연결 성공! 현재 모델: {selected_model}") # (테스트용 문구)

except Exception as e:
    st.error(f"키 설정 중 오류가 났습니다: {e}")
    selected_model = None
# ---------------------------------------------

# 입력 폼
with st.form("journal_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("아동 이름", placeholder="예: 김00")
    with col2:
        mood = st.selectbox("오늘 아이 기분", ["즐거움/활발함", "차분함/보통", "짜증/화냄", "기운없음/아픔"])
    
    keywords = st.text_area("활동 내용 & 특이사항", 
                            placeholder="예: 생일잔치 준비, 풍선 불기, 친구 도와줌, 간식 잘 먹음",
                            height=100)
    
    submit_button = st.form_submit_button(label='일지 생성하기 ✨')

# AI 생성 로직
if submit_button and keywords:
    if not selected_model:
        st.error("AI 모델 연결에 실패하여 글을 쓸 수 없습니다.")
    else:
        with st.spinner('구글 AI가 선생님 말투로 작성 중입니다...'):
            try:
                prompt = f"""
                당신은 보육원 사회복지사입니다. 아래 정보를 바탕으로 보육일지를 작성하세요.
                
                [작성 규칙]
                1. 문체: '~함', '~보임', '~하였음' (관찰일지용 개조식)
                2. 길이: 2~3문장으로 자연스럽게 연결
                3. 내용: 아동의 행동과 반응을 구체적으로 묘사
                
                [입력 정보]
                - 이름: {name}
                - 기분: {mood}
                - 활동: {keywords}
                
                위 내용을 바탕으로 자연스러운 일지 1개를 작성해줘.
                """
                
                response = model.generate_content(prompt)
                
                st.success("작성 완료!")
                st.text_area("결과 (복사해서 쓰세요)", value=response.text, height=150)
                
            except Exception as e:
                st.error(f"작성 중 오류가 났습니다: {e}")