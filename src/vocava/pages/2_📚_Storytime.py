import streamlit as st
import os
from dotenv import load_dotenv

from vocava import entity, service, storage

# ANTHROPIC_API_KEY = str(st.secrets["anthropic_api_key"])
# COHERE_API_KEY = str(st.secrets["cohere_api_key"])

load_dotenv()  # Load biến môi trường từ file .env

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")


def main():
    if "data" not in st.session_state:
        st.session_state["data"] = None

    st.title("Storytime")

    tutor = entity.get_tutor("Claude", key=ANTHROPIC_API_KEY)

    languages = list(entity.LANGUAGES)
    default_native_lang = st.session_state.get("user.native_lang", languages[0])
    default_target_lang = st.session_state.get("user.target_lang", languages[4])
    default_fluency = st.session_state.get("user.fluency", 3)
    native_language = st.sidebar.selectbox(
        "Native Language", options=entity.LANGUAGES,
        index=languages.index(default_native_lang),
    )
    target_language = st.sidebar.selectbox(
        "Choose Language", options=entity.LANGUAGES,
        index=languages.index(default_target_lang),
    )

    fluency = st.sidebar.slider("Fluency", min_value=1, max_value=10, step=1,
                                value=default_fluency)
    store = storage.VectorStore(COHERE_API_KEY)
    user = entity.User(
        native_language=native_language,
        target_language=target_language,
        fluency=fluency,
        db=store,
    )
    st.session_state["user.native_lang"] = native_language
    st.session_state["user.target_lang"] = target_language
    st.session_state["user.fluency"] = fluency
    view_native = st.sidebar.checkbox("Native View")

    concept = st.text_input("What kind of story would you like?")
    storytime = service.Service(
        "storytime",
        user=user,
        native_mode=view_native,
        tutor=tutor,
        max_tokens=1_000,
    )
    if st.button("Generate Story"):
        with st.spinner():
            data = storytime.run(fluency=fluency, concept=concept)
        st.session_state["data"] = data

    language = storytime.current_language()
    data = st.session_state["data"]
    if not data or language not in data["story"]:
        return

    generated_story = st.session_state["data"]["story"][language]
    comprehension_questions = st.session_state["data"]["questions"]
    st.markdown(generated_story)
    for i, item in enumerate(comprehension_questions):
        cols = st.columns(2)
        with cols[0]:
            st.write(item[f"question_{language}"])
        with cols[1]:
            show_answer = st.checkbox("Show Answer", key=f"q{i}")
        if show_answer:
            st.success(item[f"answer_{language}"])





if __name__ == "__main__":
    main()
