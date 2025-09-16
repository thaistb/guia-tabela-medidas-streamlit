"""
export.py
-----------

This module encapsulates routines for exporting measurement results from the
Guia de Tabela de Medidas application.  It offers two high‑level
functions: one to serialise data to CSV format, and another to generate
a compact PDF report using the reportlab library.

The CSV export produces a flat file suitable for spreadsheet software or
database ingestion, while the PDF export compiles a human‑readable report
including the user's measurements, the suggested size, the top three
candidates and a small illustration of the body types.
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, List

import pandas as pd
try:
    # Attempt to import reportlab for PDF generation.  Reportlab provides
    # precise control over typography and layout and is preferred when
    # available.  If reportlab is not installed, we will fall back to
    # matplotlib's PDF backend.
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Image,
        Table,
        TableStyle,
    )
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False


def generate_csv(result_data: Dict[str, any], inputs: Dict[str, float]) -> bytes:
    """Create a CSV representation of the result and user inputs.

    Parameters
    ----------
    result_data : dict
        Dictionary containing the outcome of the sizing calculation.  Expected
        keys include 'date_time', 'biotipo', 'estatura', 'suggested_size' and
        'top3'.
    inputs : dict
        Dictionary of user inputs with keys 'altura', 'busto', 'cintura' and
        'quadril'.

    Returns
    -------
    bytes
        UTF‑8 encoded CSV data ready for download.
    """
    # Flatten the top3 list into a comma‑separated string of sizes
    top3_sizes = ", ".join(str(item["size"]) for item in result_data.get("top3", []))
    df = pd.DataFrame({
        "data_hora": [result_data.get("date_time")],
        "altura_cm": [inputs.get("altura")],
        "busto_cm": [inputs.get("busto")],
        "cintura_cm": [inputs.get("cintura")],
        "quadril_cm": [inputs.get("quadril")],
        "biotipo": [result_data.get("biotipo")],
        "estatura": [result_data.get("estatura")],
        "tamanho_sugerido": [result_data.get("suggested_size")],
        "top3": [top3_sizes],
    })
    return df.to_csv(index=False).encode("utf-8")

def generate_pdf(result_data: Dict[str, any], inputs: Dict[str, float], fig) -> bytes:
    """Generate a PDF report from the result data and user inputs.

    This function attempts to use reportlab for high‑quality PDF output.  If
    reportlab is not available in the execution environment, it falls back
    to matplotlib's PDF backend to create a simple but effective report.

    Parameters
    ----------
    result_data : dict
        Dictionary containing the sizing result (see ``generate_csv``).
    inputs : dict
        Dictionary of user measurements.
    fig : matplotlib.figure.Figure
        Figure illustrating the body types; may be None.

    Returns
    -------
    bytes
        The binary content of the generated PDF.
    """
    if _REPORTLAB_AVAILABLE:
        # High‑fidelity report using reportlab
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()
        elements: List = []
        # Title
        title_style = styles["Title"]
        elements.append(Paragraph("Guia de Tabela de Medidas", title_style))
        elements.append(Spacer(1, 12))
        # Timestamp
        now_str = result_data.get("date_time", datetime.now().strftime("%Y-%m-%d %H:%M"))
        elements.append(Paragraph(f"Data/hora: {now_str}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        # Measurements summary
        elements.append(Paragraph("<b>Medidas informadas</b>", styles["Heading2"]))
        measurements_html = (
            f"Altura: {inputs.get('altura')} cm<br/>"
            f"Busto: {inputs.get('busto')} cm<br/>"
            f"Cintura: {inputs.get('cintura')} cm<br/>"
            f"Quadril: {inputs.get('quadril')} cm"
        )
        elements.append(Paragraph(measurements_html, styles["Normal"]))
        elements.append(Spacer(1, 12))
        # Body type and estatura
        elements.append(Paragraph("<b>Bíotipo selecionado:</b> " + str(result_data.get("biotipo")), styles["Normal"]))
        elements.append(Paragraph("<b>Estatura de referência:</b> " + str(result_data.get("estatura")).upper(), styles["Normal"]))
        elements.append(Spacer(1, 12))
        # Suggested size
        elements.append(Paragraph(f"<b>Tamanho sugerido:</b> {result_data.get('suggested_size')}", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        # Top 3 table
        top3 = result_data.get("top3", [])
        if top3:
            table_data = [["Rank", "Tamanho", "Distância", "Busto ref.", "Cintura ref.", "Quadril ref."]]
            for idx, item in enumerate(top3, 1):
                table_data.append([
                    idx,
                    item["size"],
                    f"{item['dist']:.2f}",
                    item["bust"],
                    item["waist"],
                    item["hip"],
                ])
            table_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ])
            table = Table(table_data)
            table.setStyle(table_style)
            elements.append(Paragraph("<b>Top 3 tamanhos mais próximos:</b>", styles["Heading2"]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        # Tips
        tip = result_data.get("tip")
        if tip:
            elements.append(Paragraph("<b>Dica para o seu bíotipo:</b>", styles["Heading2"]))
            elements.append(Paragraph(tip, styles["Normal"]))
            elements.append(Spacer(1, 12))
        # Insert figure
        if fig is not None:
            try:
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format="png", bbox_inches='tight')
                img_buffer.seek(0)
                max_width = 500
                img = Image(img_buffer, width=max_width, height=max_width * 0.6)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except Exception:
                pass
        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
    else:
        # Fallback PDF generation using matplotlib
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.pyplot as plt
        # Create a BytesIO to capture the PDF
        buf = BytesIO()
        # Use a PdfPages context to add pages
        with PdfPages(buf) as pdf:
            # First page with text
            fig_page = plt.figure(figsize=(8.5, 11))
            fig_page.patch.set_facecolor('white')
            y = 0.95
            # Title
            fig_page.text(0.5, y, 'Guia de Tabela de Medidas', ha='center', fontsize=16, weight='bold')
            y -= 0.05
            # Timestamp
            now_str = result_data.get('date_time', datetime.now().strftime('%Y-%m-%d %H:%M'))
            fig_page.text(0.1, y, f'Data/hora: {now_str}', fontsize=10)
            y -= 0.05
            # Measurements
            fig_page.text(0.1, y, 'Medidas informadas:', fontsize=12, weight='bold')
            y -= 0.03
            fig_page.text(0.1, y, f"Altura: {inputs.get('altura')} cm", fontsize=10)
            y -= 0.03
            fig_page.text(0.1, y, f"Busto: {inputs.get('busto')} cm", fontsize=10)
            y -= 0.03
            fig_page.text(0.1, y, f"Cintura: {inputs.get('cintura')} cm", fontsize=10)
            y -= 0.03
            fig_page.text(0.1, y, f"Quadril: {inputs.get('quadril')} cm", fontsize=10)
            y -= 0.05
            # Body type and estatura
            fig_page.text(0.1, y, f"Bíotipo: {result_data.get('biotipo')}", fontsize=10)
            y -= 0.03
            fig_page.text(0.1, y, f"Estatura: {result_data.get('estatura').upper()}", fontsize=10)
            y -= 0.05
            # Suggested size
            fig_page.text(0.1, y, f"Tamanho sugerido: {result_data.get('suggested_size')}", fontsize=12, weight='bold')
            y -= 0.05
            # Top 3
            fig_page.text(0.1, y, 'Top 3 tamanhos mais próximos:', fontsize=12, weight='bold')
            y -= 0.04
            top3 = result_data.get('top3', [])
            for idx, item in enumerate(top3, 1):
                fig_page.text(0.1, y, f"{idx}. Tamanho {item['size']} – Distância {item['dist']:.2f} | "
                                f"Ref.: {item['bust']} / {item['waist']} / {item['hip']} cm", fontsize=9)
                y -= 0.03
            # Tip
            tip = result_data.get('tip')
            if tip:
                y -= 0.02
                fig_page.text(0.1, y, 'Dica para o seu bíotipo:', fontsize=12, weight='bold')
                y -= 0.03
                # Wrap tip text across lines if necessary
                import textwrap
                for line in textwrap.wrap(tip, width=70):
                    fig_page.text(0.1, y, line, fontsize=9)
                    y -= 0.03
            # Add page
            pdf.savefig(fig_page)
            plt.close(fig_page)
            # Second page with the illustration, if provided
            if fig is not None:
                fig2 = plt.figure(figsize=(8.5, 11))
                fig2.patch.set_facecolor('white')
                # Title for the figures page
                fig2.text(0.5, 0.95, 'Biótipos (figuras esquemáticas)', ha='center', fontsize=14, weight='bold')
                # Convert the passed figure into an array and embed it
                from io import BytesIO as _BytesIO
                import matplotlib.image as mpimg
                tmp = _BytesIO()
                try:
                    fig.savefig(tmp, format='png', bbox_inches='tight')
                    tmp.seek(0)
                    img_arr = mpimg.imread(tmp)
                    # Create an axes that covers most of the page and display the image
                    ax_img = fig2.add_axes([0.05, 0.1, 0.9, 0.8])
                    ax_img.imshow(img_arr)
                    ax_img.axis('off')
                except Exception:
                    # If embedding fails, just leave the page blank beneath the title
                    pass
                pdf.savefig(fig2)
                plt.close(fig2)
        buf.seek(0)
        return buf.read()
