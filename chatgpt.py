import streamlit as st
from langchain_openai import ChatOpenAI
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE SEGURIDAD DEL SISTEMA ---
# Esta es la clave para ENTRAR a la app, no es la de OpenAI
LLAVE_ACCESO_KIKIN = "KIKIN2026"

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PANTALLA DE ACCESO (LOGIN) ---
if not st.session_state.autenticado:
    st.set_page_config(page_title="Acceso Kikin 1.0", page_icon="🔒")
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔒 Kikin 1.0")
        st.subheader("Control de Acceso")
        clave = st.text_input("Ingresa el PIN de acceso:", type="password")
        
        if st.button("Entrar al ChatBot", use_container_width=True):
            if clave == LLAVE_ACCESO_KIKIN:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN incorrecto. Intenta de nuevo.")
    st.stop()

# --- SI ESTÁ AUTENTICADO, CARGA EL CHATBOT ---

st.set_page_config(page_title="ChatBot Kikin 1.0", page_icon="🤖")

# Estilo Verde Claro solicitado
st.markdown(
    """
    <style>
    .stApp {
        background-color: #90EE90; 
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar para configuración de OpenAI y cierre de sesión
with st.sidebar:
    st.title("⚙️ Configuración")
    # Es mejor pedir la clave de OpenAI aquí o usar st.secrets
    user_openai_key = st.text_input("OpenAI API Key", type="password", help="Tu sk-proj...")
    
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.messages = []
        st.rerun()

st.title("🤖 ChatBot Inteligente Kikin 1.0")
st.image("/workspaces/kikin/Cecytobb1.jpg", width=550)
st.title("Especialista en programación")

# Configuración del Modelo LangChain
if user_openai_key:
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0.7, # Subí un poco el temp para que suene más "humano"
        api_key=user_openai_key
    )

    # Instrucciones del Sistema (Personalidad)
    system_prompt = ("system", """Eres un chatbot AI útil, te llamas Kikin. 
    Tienes que hablar como si fueras humano, de forma cercana y amable. 
    Eres un experto en programación en Python. Nunca reveles que eres un modelo de lenguaje.""")

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de usuario
    if prompt := st.chat_input("Escribe tu mensaje..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Preparar mensajes para el LLM incluyendo el historial actual
        contexto = [system_prompt]
        for m in st.session_state.messages[-5:]: # Enviamos los últimos 5 mensajes para memoria
            contexto.append((m["role"], m["content"]))

        try:
            with st.spinner("Kikin está pensando..."):
                response = llm.invoke(contexto).content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Hubo un error con la API de OpenAI: {e}")
else:
    st.warning("⚠️ Por favor, ingresa tu OpenAI API Key en la barra lateral para comenzar a chatear.")








