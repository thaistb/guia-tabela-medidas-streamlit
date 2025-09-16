"""
app.py
------

Entry point for the Streamlit application implementing the Guia de Tabela de
Medidas.  The app guides the user through a multi‑step interface: from a
welcome page to entering measurements and selecting a body type, and
finally to viewing the recommended size along with export options.  A
separate page provides information about the purpose of the tool, usage
limitations and privacy assurances.

To run the app locally, install the dependencies listed in requirements.txt
and execute:

    streamlit run app.py

On the Streamlit Community Cloud, this file will be detected as the main
module.  The app relies on the modules ``logic``, ``figures`` and
``export`` which reside in the same package directory.
"""

import datetime
import streamlit as st

from logic import (
    classify_estatura,
    suggest_size_and_top,
    BIOTIPO_WEIGHTS,
    BIOTIPO_TIPS,
)
from figures import create_biotipos_figure
from export import generate_csv, generate_pdf

# Configure the page
st.set_page_config(
    page_title="Guia de Tabela de Medidas",
    page_icon="📏",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialise session state variables
if "page" not in st.session_state:
    st.session_state["page"] = "Início"
if "result_data" not in st.session_state:
    st.session_state["result_data"] = None
if "inputs" not in st.session_state:
    st.session_state["inputs"] = {}

# Sidebar navigation
pages = ["Início", "Medidas & Bíotipo", "Resultado", "Sobre"]
with st.sidebar:
    st.header("Navegação")
    choice = st.radio("", pages, index=pages.index(st.session_state["page"]))
    if choice != st.session_state["page"]:
        # Reset result if navigating away from results
        if choice != "Resultado":
            st.session_state["result_data"] = None
        st.session_state["page"] = choice
        st.experimental_rerun()

def show_inicio():
    st.title("📏 Guia de Tabela de Medidas (ABNT)")
    st.markdown(
        """
        Bem‑vinda ao guia de tabela de medidas! Este aplicativo ajuda a
        identificar um tamanho numérico sugerido (34‑62) com base nas suas
        medidas de busto, cintura e quadril, bem como no seu bíotipo e
        estatura.  Use como referência inicial – as modelagens podem
        variar de marca para marca.

        **Observação:** este é um guia didático derivado de tabelas da ABNT
        e não substitui a consulta às tabelas oficiais da sua marca ou
        confecção.  Suas informações não são armazenadas; use com bom senso.
        """
    )
    if st.button("Começar", type="primary"):
        st.session_state["page"] = "Medidas & Bíotipo"
        st.experimental_rerun()

def show_inputs_page():
    st.header("Medidas & Bíotipo")
    st.markdown("Preencha suas medidas em centímetros. Valores decimais são aceitos (use ponto ou vírgula).")
    col1, col2 = st.columns(2)
    with col1:
        altura = st.number_input("Altura (cm)", min_value=120.0, max_value=200.0, value=160.0, step=0.5)
        busto  = st.number_input("Busto (cm)",  min_value=70.0,  max_value=160.0, value=90.0,  step=0.5)
    with col2:
        cintura= st.number_input("Cintura (cm)",min_value=50.0,  max_value=140.0, value=74.0,  step=0.5)
        quadril= st.number_input("Quadril (cm)",min_value=80.0,  max_value=170.0, value=100.0, step=0.5)
    # Body type selection
    biotipo = st.selectbox("Bíotipo", list(BIOTIPO_WEIGHTS.keys()), index=0)
    # Optional display of figures
    if st.checkbox("Mostrar figuras dos bíotipos"):
        fig = create_biotipos_figure()
        st.pyplot(fig, use_container_width=True)
    # Optional photo upload
    foto = st.file_uploader("Foto (opcional)", type=["png", "jpg", "jpeg"], accept_multiple_files=False)
    if foto is not None:
        st.image(foto, caption="Pré‑visualização da foto", use_column_width=True)
    # Compute button
    if st.button("Calcular tamanho sugerido", type="primary"):
        # Run the sizing algorithm
        best, top3 = suggest_size_and_top(busto, cintura, quadril, biotipo)
        estatura = classify_estatura(altura)
        # Prepare result data
        result = {
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "biotipo": biotipo,
            "estatura": estatura,
            "suggested_size": best["size"],
            "top3": top3,
            "tip": BIOTIPO_TIPS.get(biotipo),
        }
        st.session_state["result_data"] = result
        st.session_state["inputs"] = {
            "altura": altura,
            "busto": busto,
            "cintura": cintura,
            "quadril": quadril,
        }
        st.session_state["page"] = "Resultado"
        st.experimental_rerun()

def show_results_page():
    st.header("Resultado")
    result = st.session_state.get("result_data")
    if not result:
        st.info("Nenhum resultado ainda. Por favor, preencha suas medidas na aba anterior.")
        return
    inputs = st.session_state.get("inputs", {})
    # Display suggested size and details
    st.subheader(f"Tamanho sugerido: {result['suggested_size']}")
    st.write(f"Estatura de referência: **{result['estatura'].upper()}**")
    st.write(
        f"Medidas informadas – Altura: **{inputs.get('altura'):.1f} cm** | "
        f"Busto: **{inputs.get('busto'):.1f} cm** | "
        f"Cintura: **{inputs.get('cintura'):.1f} cm** | "
        f"Quadril: **{inputs.get('quadril'):.1f} cm**"
    )
    st.write(f"Bíotipo: **{result['biotipo']}**")
    # Tip
    tip = result.get("tip")
    if tip:
        st.markdown(f"**Dica para o seu bíotipo:** {tip}")
    # Show top 3
    st.markdown("### Top 3 tamanhos mais próximos")
    for idx, item in enumerate(result["top3"], 1):
        st.write(
            f"{idx}. Tamanho {item['size']} – Distância: {item['dist']:.2f} | "
            f"Ref. busto: {item['bust']} cm, cintura: {item['waist']} cm, quadril: {item['hip']} cm"
        )
    # Download exports
    st.markdown("### Exportar resultados")
    # Generate current figure for export
    fig = create_biotipos_figure()
    csv_bytes = generate_csv(result, inputs)
    pdf_bytes = generate_pdf(result, inputs, fig)
    st.download_button(
        label="Baixar CSV",
        data=csv_bytes,
        file_name="resultado_medidas.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Baixar PDF",
        data=pdf_bytes,
        file_name="relatorio_medidas.pdf",
        mime="application/pdf",
    )
    # Allow recalculation
    if st.button("Nova consulta", type="secondary"):
        st.session_state["page"] = "Medidas & Bíotipo"
        st.experimental_rerun()

def show_about_page():
    st.header("Sobre o aplicativo")
    st.markdown(
        """
        Este guia utiliza incrementos regulares para busto, cintura e quadril
        baseados em exemplos de tabelas da ABNT, com o propósito de oferecer
        uma referência inicial para o tamanho numérico de roupas (34‑62).  As
        recomendações são calculadas com base na diferença entre suas
        medidas e os valores de referência, ponderadas pelo bíotipo selecionado.

        **Limitações:** As modelagens variam entre marcas e estilos de peças.
        Use este guia como orientação inicial e consulte as tabelas oficiais
        fornecidas pela marca para ajustes precisos.  A classificação de
        estatura (baixa/média/alta) é aproximada e não reflete variações
        individuais de comprimento de perna ou tronco.

        **Privacidade:** Nenhuma informação é armazenada em servidores.  Seus
        dados permanecem apenas na sua sessão local.  Fotos carregadas são
        exibidas apenas para você e não são enviadas ou salvas.

        **Contato:** Para sugestões ou dúvidas, entre em contato com a
        desenvolvedora via o e‑mail disponível no site da TB Concept.
        """
    )

# Router: display appropriate page
if st.session_state["page"] == "Início":
    show_inicio()
elif st.session_state["page"] == "Medidas & Bíotipo":
    show_inputs_page()
elif st.session_state["page"] == "Resultado":
    show_results_page()
elif st.session_state["page"] == "Sobre":
    show_about_page()
