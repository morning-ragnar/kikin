import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora Pro", page_icon="🧮")

# Estilo CSS para imitar tu diseño de Kivy (bordes redondeados y colores)
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 24px;
        border-radius: 12px;
        border: none;
        transition: 0.3s;
    }
    /* Botones de números */
    .stButton > button:first-child {
        background-color: #ececec;
        color: #333;
    }
    /* Estilo para el display */
    .stTextInput input {
        font-size: 40px !important;
        text-align: right;
        background-color: #262626 !important;
        color: white !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicializar el estado de la calculadora
if 'display' not in st.session_state:
    st.session_state.display = ""

def click_button(label):
    if label == "C":
        st.session_state.display = ""
    elif label == "=":
        try:
            # Evaluar la expresión
            result = eval(st.session_state.display)
            # Formatear el resultado
            if isinstance(result, float):
                st.session_state.display = f"{result:.2f}".rstrip('0').rstrip('.')
            else:
                st.session_state.display = str(result)
        except:
            st.session_state.display = "Error"
    else:
        st.session_state.display += str(label)

# Título e Interfaz
st.title("🧮 Calculadora")

# Pantalla (Display)
st.text_input(label="Resultado", value=st.session_state.display, key="input", disabled=True, label_visibility="collapsed")

# Distribución de botones (Grid de 4 columnas)
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    'C', '0', '=', '+'
]

cols = st.columns(4)
for i, button in enumerate(buttons):
    with cols[i % 4]:
        # Diferenciar colores para operadores (como en tu CustomButton)
        is_operator = button in ['+', '-', '*', '/', 'C', '=']
        if st.button(button, key=f"btn_{button}_{i}"):
            click_button(button)