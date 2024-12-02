import httpx
import streamlit as st

# Access sensitive variables from Streamlit's secrets
BASE_URL = st.secrets["BASE_URL"]
API_KEY = st.secrets["API_KEY"]

st.title("Depósito de Pólizas")

# Input for the ID
id_input = st.text_input("ID Póliza", "")
id_input = id_input.upper().strip()


def fetch_data(document_id):
    try:
        url = f"{BASE_URL}/api/v1/policy/{document_id}"
        headers = {"X-API-KEY": API_KEY}
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.status_code, response.json()
    except httpx.HTTPStatusError as http_err:
        status_code = http_err.response.status_code
        try:
            error_detail = http_err.response.json().get("detail", "Error...")
        except ValueError:
            error_detail = http_err.response.text or "Error..."
        return status_code, {"detail": error_detail}
    except Exception as err:
        return 500, {"detail": str(err)}


def display_main_info(data):
    st.write("### Información")
    st.write(f"**Nombre:** {data.get('title', 'N/A')}")
    st.write(f"**Empresa:** {data.get('company', 'N/A')}")
    st.write(f"**Fecha:** {data.get('date', 'N/A')}")
    url = data.get("url")
    if url:
        st.markdown(f"[Url Póliza]({url})", unsafe_allow_html=True)
    search_url = data.get("search_url")
    if search_url:
        st.markdown(f"[Url búsqueda]({search_url})", unsafe_allow_html=True)


def display_tags(tags):
    if tags:
        st.markdown(
            """
            <style>
            .badge {
              display: inline-block;
              padding: 0.3em 0.5em;
              font-size: 85%;
              font-weight: 600;
              color: #333;
              background-color: #e0e0e0;
              border-radius: 12px;
              margin-right: 0.5em;
              margin-bottom: 0.5em;
              box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.write("**Ramas**")
        tag_badges = " ".join([f'<span class="badge">{tag}</span>' for tag in tags])
        st.markdown(tag_badges, unsafe_allow_html=True)


def display_articles(articles):
    if articles:
        for article in articles:
            with st.expander(article.get("name", "N/A").capitalize()):
                description = article.get("description", "N/A")
                st.markdown(description, unsafe_allow_html=True)
    else:
        st.write("No articles available.")


def display_related_documents(data):
    related_docs = data.get("related", [])
    if related_docs:
        st.markdown(
            """
            <style>
            .related-tag {
              display: inline-block;
              padding: 0.3em 0.5em;
              font-size: 85%;
              font-weight: 600;
              color: #333;
              background-color: #e0e0e0;
              border-radius: 12px;
              margin-right: 0.5em;
              margin-bottom: 0.5em;
              box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .related-tag:hover {
              background-color: #d0d0d0;
              box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.write("**Relacionados:**")
        tags = " ".join(
            [f'<span class="related-tag">{related}</span>' for related in related_docs]
        )
        st.markdown(tags, unsafe_allow_html=True)


# Process the input when the user presses ENTER
if id_input:
    with st.spinner("Buscando..."):
        status_code, data = fetch_data(id_input)
    if status_code == 200 and data:
        display_main_info(data)
        display_tags(data.get("tags", []))
        display_related_documents(data)
        display_articles(data.get("articles", []))
    elif status_code == 404:
        st.error("Documento no encontrado...")
    else:
        st.error("Error...")
else:
    st.info("Ingrese ID póliza/cláusula y presione Enter.")
