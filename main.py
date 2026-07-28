import streamlit as st

from backend import (
    responder_pregunta,
    cargar_base_predeterminada,
)

st.set_page_config(
    page_title="Asistente de Terminos y Condiciones",
    page_icon="📄",
    layout="wide",
)

# ======================================================
# CARGA AUTOMATICA DEL PDF
# ======================================================

cargar_base_predeterminada()

if "nombre_evento" not in st.session_state:
    st.session_state.nombre_evento = "Términos y Condiciones"

# ======================================================
# HISTORIAL DEL CHAT
# ======================================================

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content":
                "Hola! Soy tu asistente virtual. "
                "Puedo responder preguntas sobre los terminos y condiciones "
                "del servicio de masajes. ¿En que puedo ayudarte?"
        }
    ]

if "prompt_sugerido" not in st.session_state:
    st.session_state.prompt_sugerido = None


# ======================================================
# BARRA LATERAL
# ======================================================

with st.sidebar:

    st.header("📄 Documento cargado")

    st.success(st.session_state.nombre_evento)

    st.markdown("---")

    st.info(
        "La base de conocimiento se carga automaticamente desde "
        "**terminosycondiciones.pdf**."
    )


# ======================================================
# INTERFAZ PRINCIPAL
# ======================================================

URL_ROBOT = "https://em-content.zobj.net/thumbs/240/microsoft/319/robot_1f916.png"

st.markdown(
    f"""
    <h1 style="display:flex;align-items:center;gap:12px;">
        <img src="{URL_ROBOT}" width="50">
        Asistente de Terminos y Condiciones
    </h1>
    """,
    unsafe_allow_html=True
)

st.subheader(
    "Haz cualquier pregunta relacionada con los términos y condiciones del servicio."
)

# ======================================================
# HISTORIAL
# ======================================================

for mensaje in st.session_state.mensajes:

    avatar = URL_ROBOT if mensaje["role"] == "assistant" else "👤"

    with st.chat_message(mensaje["role"], avatar=avatar):
        st.write(mensaje["content"])


# ======================================================
# PREGUNTAS SUGERIDAS
# ======================================================

PREGUNTAS_SUGERIDAS = [
    "¿Como puedo cancelar una cita?",
    "¿Cual es la politica de reembolso?",
    "¿Que metodos de pago aceptan?",
    "¿Como se protegen mis datos personales?"
]


def seleccionar_pregunta(pregunta):
    st.session_state.prompt_sugerido = pregunta


st.write("### 💡 Preguntas sugeridas")

columnas = st.columns(len(PREGUNTAS_SUGERIDAS))

for i, pregunta in enumerate(PREGUNTAS_SUGERIDAS):

    with columnas[i]:

        st.button(
            pregunta,
            key=f"pregunta_{i}",
            on_click=seleccionar_pregunta,
            args=(pregunta,),
            use_container_width=True,
        )


# ======================================================
# ENTRADA DEL USUARIO
# ======================================================

user_input = st.chat_input("Escribe tu pregunta...")

if st.session_state.prompt_sugerido:

    prompt_final = st.session_state.prompt_sugerido
    st.session_state.prompt_sugerido = None

else:

    prompt_final = user_input


# ======================================================
# RESPUESTA DEL ASISTENTE
# ======================================================

if prompt_final:

    st.session_state.mensajes.append(
        {
            "role": "user",
            "content": prompt_final
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.write(prompt_final)

    with st.chat_message("assistant", avatar=URL_ROBOT):

        with st.spinner("Analizando documento..."):

            try:

                respuesta = responder_pregunta(prompt_final)

                st.write(respuesta)

            except Exception as e:

                respuesta = f"Ocurrió un error: {e}"

                st.error(respuesta)

    st.session_state.mensajes.append(
        {
            "role": "assistant",
            "content": respuesta
        }
    )

    st.rerun()