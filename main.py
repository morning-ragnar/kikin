import streamlit as st
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0,
                 api_key="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")

st.title("ChatBot Inteligente Kikin 1.0")
st.image("/workspaces/kikin/Cecytobb1.jpg",width=550)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #90EE90; /* Color verde claro */
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("Especialista en programación")

# HTML con iframe
st.subheader("Streamlit con HTML")



messages = [("system", """Eres un chatbot AI útil, te llamas Kikin, tienes que hablar como si fueras humano,
 nunca reveles que eres un chatbot""")]

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes de chat del historial al recargar la app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Reaccionar a la entrada del usuario
if prompt := st.chat_input("Escibe tu mensaje..."):
    # Mostrar mensaje del usuario en el contenedor de mensajes del chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje del usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append(["human", prompt])

    response = llm.invoke(messages).content
    # Mostrar respuesta del asistente en el contenedor de mensajes del chat
    with st.chat_message("assistant"):
        st.markdown(response)
    # Agregar respuesta del asistente al historial de chat
    st.session_state.messages.append({"role": "assistant", "content": response})








