import streamlit as st
from langchain_openai import ChatOpenAI

# --- CONFIGURACIÓN DE SEGURIDAD DEL SISTEMA ---
# Esta clave es solo para entrar a tu app de Streamlit
LLAVE_ACCESO_KIKIN = "KIKIN2026"

# --- INICIALIZACIÓN DE ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🔒 Acceso Kikin 1.1")
    clave = st.text_input("Ingresa el PIN de acceso:", type="password")
    if st.button("Entrar"):
        if clave == LLAVE_ACCESO_KIKIN:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("PIN incorrecto")
    st.stop()

# --- CONFIGURACIÓN DEL CHATBOT ---
st.title("🤖 ChatBot Inteligente Kikin")
st.image("/workspaces/kikin/Cecytobb1.jpg", width=550)

# SEGURIDAD: Intentamos leer la API Key desde los Secrets de Streamlit
# Si no existe, usamos un valor vacío para que no truene el código
try:
    api_openai = st.secrets["OPENAI_API_KEY"]
except:
    api_openai = ""

if api_openai:
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0.7,
        api_key=api_openai  # <--- YA NO HAY TEXTO sk-proj AQUÍ
    )

    # Personalidad de Kikin
    system_prompt = ("system", "Eres un chatbot AI útil, te llamas Kikin. Hablas como humano y eres experto en programación.")

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de usuario
    if prompt := st.chat_input("Escribe tu mensaje..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        contexto = [system_prompt]
        for m in st.session_state.messages[-5:]:
            contexto.append((m["role"], m["content"]))

        with st.spinner("Kikin pensando..."):
            response = llm.invoke(contexto).content
            
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("⚠️ Falta configurar la 'OPENAI_API_KEY' en los Secrets de Streamlit.")