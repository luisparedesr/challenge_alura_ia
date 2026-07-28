import os
import cohere
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader


def obtener_cliente_cohere():
    """Inicializa de forma segura el cliente de Cohere usando st.secrets y lo guarda en la sesión."""
    if "co_client" not in st.session_state:
        try:
            api_key = st.secrets["COHERE_API_KEY"]
            st.session_state.co_client = cohere.Client(api_key)
        except KeyError:
            st.error(" No se encontró la clave 'COHERE_API_KEY' en los secretos de Streamlit.")
            return None
        except Exception as e:
            st.error(f" Error al conectar con Cohere: {e}")
            return None

    return st.session_state.co_client


def cargar_base_predeterminada():
    """Carga automáticamente el PDF 'terminosycondiciones.pdf'."""

    if "bloques_evento" in st.session_state and st.session_state.bloques_evento:
        return

    # Obtiene la ruta de la carpeta raíz del proyecto
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_raiz = os.path.dirname(ruta_actual)

    # Ruta del PDF
    ruta_pdf = os.path.join(ruta_raiz, "documento", "terminosycondiciones.pdf")

    if os.path.exists(ruta_pdf):
        try:
            # Procesamos el documento automáticamente
            bloques = procesar_documento(ruta_pdf)
            embeddings = generar_embeddings_contexto(bloques)

            st.session_state.bloques_evento = bloques
            st.session_state.embeddings_evento = embeddings
            st.session_state.nombre_evento = "Terminos y Condiciones"

        except Exception as e:
            st.session_state.nombre_evento = "Error al cargar documento"
            st.error(f" Error al procesar el PDF: {e}")
    else:
        st.session_state.nombre_evento = "Documento no encontrado"


def procesar_documento(ruta_archivo):
    """Procesa únicamente documentos PDF."""

    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension != ".pdf":
        raise ValueError("Solo se permiten archivos PDF.")

    loader = PyPDFLoader(ruta_archivo)
    paginas = loader.load()

    bloques_texto = []

    for pagina in paginas:
        texto = pagina.page_content.strip()

        if texto:
            bloques_texto.append(texto)

    return bloques_texto


def generar_embeddings_contexto(bloques_contexto):
    """Calcula los embeddings de todos los bloques del documento."""
    co = obtener_cliente_cohere()

    if not co or not bloques_contexto:
        return None

    response_contexto = co.embed(
        texts=bloques_contexto,
        model="embed-multilingual-v3.0",
        input_type="search_document"
    )

    return response_contexto.embeddings


def buscar_respuesta_semantica(pregunta, bloques_contexto, embeddings_contexto):
    """Encuentra el bloque de datos más relevante basado en la pregunta."""

    co = obtener_cliente_cohere()

    if not co or not bloques_contexto or not embeddings_contexto:
        return None

    response_pregunta = co.embed(
        texts=[pregunta],
        model="embed-multilingual-v3.0",
        input_type="search_query"
    )

    embedding_pregunta = response_pregunta.embeddings[0]

    mejor_similitud = -1
    mejor_bloque = ""

    for bloque, embedding_doc in zip(bloques_contexto, embeddings_contexto):
        similitud = sum(p * d for p, d in zip(embedding_pregunta, embedding_doc))

        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_bloque = bloque

    if mejor_similitud > 0.3:
        return mejor_bloque

    return None


def generar_respuesta_conversacional(pregunta, contexto_recuperado, historial_cohere=[]):
    """Usa el LLM de Cohere pasándole el historial de la conversación para mantener el hilo."""

    co = obtener_cliente_cohere()

    if not co:
        return "Cliente de Cohere no inicializado."

    prompt_sistema = (
        "Eres un asistente virtual especializado en responder preguntas sobre los términos y condiciones de una empresa de servicios de masaje.\n\n"
        "REGLAS DE OBLIGATORIO CUMPLIMIENTO:\n"
        "1. SI EL USUARIO DA RESPUESTAS CORTAS, AFIRMACIONES, NEGACIONES O EXCLAMACIONES (ej: 'no', 'sí', 'ok', 'gracias'): "
        "Mantén el hilo de la conversación de forma natural basándote en el historial. "
        "NO inventes información.\n"
        "2. SI EL USUARIO HACE UNA PREGUNTA SOBRE LOS TÉRMINOS Y CONDICIONES: "
        "Responde usando EXCLUSIVAMENTE el Contexto de Referencia proporcionado.\n"
        "3. SI LA INFORMACIÓN NO APARECE EN EL DOCUMENTO: "
        "Indica amablemente que esa información no se encuentra en los términos y condiciones disponibles."
    )

    contexto_texto = (
        contexto_recuperado
        if contexto_recuperado
        else "No hay contexto relevante para esta interacción."
    )

    prompt_usuario = (
        f"Contexto de Referencia:\n{contexto_texto}\n\n"
        f"Pregunta actual del Usuario: {pregunta}"
    )

    try:
        respuesta = co.chat(
            model="command-r-08-2024",
            message=prompt_usuario,
            preamble=prompt_sistema,
            chat_history=historial_cohere,
            temperature=0.2
        )

        return respuesta.text

    except Exception as e:
        return f"Error al generar la respuesta con el LLM de Cohere: {e}"


def responder_pregunta(pregunta_usuario):
    """Orquesta la detección de palabras clave, historial, búsqueda semántica y generación."""

    pregunta_limpia = (
        pregunta_usuario.strip()
        .lower()
        .replace("?", "")
        .replace("¡", "")
        .replace("!", "")
    )

    respuestas_cortas = [
        "hola",
        "buenas",
        "que tal",
        "no",
        "si",
        "sí",
        "ok",
        "vale",
        "gracias",
        "perfecto",
        "genial",
    ]

    historial_cohere = []

    if "mensajes" in st.session_state:
        for msg in st.session_state.mensajes[-6:]:
            role_cohere = "USER" if msg["role"] == "user" else "CHATBOT"

            historial_cohere.append(
                {
                    "role": role_cohere,
                    "message": msg["content"],
                }
            )

    if pregunta_limpia in respuestas_cortas or len(pregunta_limpia) < 4:
        return generar_respuesta_conversacional(
            pregunta_usuario,
            contexto_recuperado=None,
            historial_cohere=historial_cohere,
        )

    # Procedemos con RAG sobre el PDF
    bloques = st.session_state.get("bloques_evento", [])
    embeddings = st.session_state.get("embeddings_evento", None)

    if not bloques or embeddings is None:
        return " No se pudo cargar el documento de términos y condiciones."

    bloque_relevante = buscar_respuesta_semantica(
        pregunta_usuario,
        bloques,
        embeddings,
    )

    # Generamos la respuesta usando el bloque recuperado del PDF
    respuesta_final = generar_respuesta_conversacional(
        pregunta_usuario,
        bloque_relevante,
        historial_cohere,
    )

    return respuesta_final
