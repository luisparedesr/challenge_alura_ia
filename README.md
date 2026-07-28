# challenge_alura_ia
repositorio del challenge
Asistente Inteligente de Términos y Condiciones

## Descripción

Esta aplicación permite realizar preguntas sobre un documento de **términos y condiciones** de una empresa de servicios de masaje.

El sistema utiliza un modelo de inteligencia artificial para buscar la información más relevante dentro del documento PDF y responder las preguntas del usuario de forma precisa.

---

## Tecnologías utilizadas

- Python
- Streamlit
- Cohere API
- LangChain
- PyPDFLoader

---

## Cómo ejecutar el proyecto

1. Clonar el repositorio.

```bash
git clone https://github.com/usuario/repositorio.git
```

2. Instalar las dependencias.

```bash
pip install -r requirements.txt
```

3. Configurar la clave de Cohere en `secrets.toml`.

```toml
COHERE_API_KEY="TU_API_KEY"
```

4. Ejecutar la aplicación.

```bash
streamlit run main.py
```

---

## Evidencias del funcionamiento

### Pantalla principal

<img width="1853" height="961" alt="image" src="https://github.com/user-attachments/assets/3583d9b2-f5b5-4106-97ef-335c9e04bc90" />


### Consulta realizada y su respuesta

<img width="1862" height="960" alt="image" src="https://github.com/user-attachments/assets/87186fe2-41a8-422f-a4bc-d5694b64a18c" />


