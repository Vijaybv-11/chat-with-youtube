import streamlit as st
from system.transcript import extract_video_id,list_language
from system.transcripterror_handler import TranscriptError
from system.indexing import build_index
from system.answering import answer_question
from system.generation import GenerationError


st.set_page_config(page_title="YouTube RAG", page_icon=":material/smart_display:")

st.header("YouTube Video Summarizer")
st.subheader("A chatbot for summarizing youtube videos with the help of RAG")
st.divider()


@st.cache_data(ttl=3600,show_spinner="Loading caption languages...")
def cached_languages(video_id):
      return list_language(video_id)

@st.cache_resource(max_entries=5,show_spinner=False)
def cached_index(video_id,language):
     return build_index(video_id,language)


url=st.text_input("Enter a YouTube url or video ID",key="video_url")

def reset_session():
      keys = [
          "video_url",
          "loaded",
          "vector_store",
          "messages",
          "chat_video",
      ]

      for key in list(st.session_state):
          if key in keys or key.startswith("language_"):
              del st.session_state[key]

st.button("Start fresh", on_click=reset_session)
if url.strip():
    try:
        video_id = extract_video_id(url)
        languages = cached_languages(video_id)
    except TranscriptError as error:
        st.error(str(error))
        st.stop()

    if not languages:
        st.warning("No caption languages are available for this video.")
        st.stop()

    selected_language = st.selectbox(
        "Caption language",
        options=languages,
        # YouTube already adds "(auto-generated)" to the name of generated captions
        format_func=lambda item: item["language"],
        key=f"language_{video_id}",
    )

    language_code = selected_language["language_code"]

    if st.button("Load video"):
        try:
            with st.spinner("indexing Video ..."):
                vector_store=cached_index(video_id,language_code)
        except TranscriptError as error:
            st.error(str(error))
            st.stop()
        st.session_state.vector_store=vector_store
        st.session_state.loaded=(video_id,language_code)

    if (
          st.session_state.get("loaded") == (video_id, language_code)
          and "vector_store" in st.session_state
      ):
          store = st.session_state.vector_store
          st.success(
              f"Video ready! Indexed {store.index.ntotal} text chunks."
          )

    if (
        st.session_state.get("loaded") != (video_id, language_code)
        or "vector_store" not in st.session_state
    ):
        st.info("Click Load video before asking questions.")
        st.stop()

    if (
        "messages" not in st.session_state
        or st.session_state.get("chat_video") != st.session_state.loaded
    ):
        st.session_state.messages = []
        st.session_state.chat_video = st.session_state.loaded

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask about this video")
    if question and question.strip():
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Finding an answer..."):
                    answer = answer_question(
                        st.session_state.vector_store,
                        question,
                    )
            except GenerationError as error:
                # not saved to history, so the user can just ask again
                st.error(str(error))
                st.stop()
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

