"""
figures.py
-----------

This module provides a utility function for generating schematic body shape
illustrations used in the Guia de Tabela de Medidas application.  Because
copyrighted images cannot be bundled and the application must remain
self‑contained, the figures are rendered using matplotlib primitives.  The
resulting figure depicts six simplified silhouettes corresponding to the
Retangular, Violão, Ampulheta, Triângulo, Triângulo invertido and Oval
body types.  These drawings are intentionally abstract; their purpose is
purely didactic to help users recognise their body shape.

The exported function returns a matplotlib figure object that can be
displayed in a Streamlit interface via ``st.pyplot`` or saved to an image
buffer when generating a PDF report.
"""

import matplotlib.pyplot as plt
import numpy as np

def create_biotipos_figure() -> plt.Figure:
    """Create a matplotlib figure containing stylised body type silhouettes.

    The figure contains six subplots arranged in a 2×3 grid.  Each subplot
    shows a stylised representation of one of the six body types defined in
    the application (Retangular, Violão, Ampulheta, Triângulo, Triângulo
    invertido and Oval).  Colours are kept neutral to ensure the drawings
    integrate well with a light‑themed Streamlit app.

    Returns
    -------
    plt.Figure
        The created matplotlib figure.  The caller is responsible for
        disposing of the figure if re‑creating multiple times to avoid
        memory leaks.
    """
    # Create the figure and axes
    fig, axes = plt.subplots(2, 3, figsize=(10, 6))
    axes = axes.ravel()

    def draw_shape(ax, pts, title: str):
        """Helper to draw a polygon shape and its border on a given axis."""
        # Separate the x and y coordinates
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]
        ax.fill(xs, ys, alpha=0.35, color="#cccccc")
        ax.plot(xs, ys, linewidth=2, color="#555555")
        ax.set_title(title, fontsize=10, pad=6)
        ax.set_aspect('equal')
        ax.axis('off')

    # Define the coordinates for each body shape
    retangular = [(0.4, 0.1), (0.6, 0.1), (0.65, 0.55), (0.35, 0.55)]
    violao     = [(0.45, 0.1), (0.55, 0.1), (0.62, 0.40), (0.50, 0.55), (0.38, 0.40)]
    ampulheta  = [(0.42, 0.1), (0.58, 0.1), (0.66, 0.38), (0.50, 0.55), (0.34, 0.38)]
    triangulo  = [(0.46, 0.1), (0.54, 0.1), (0.57, 0.35), (0.70, 0.55), (0.30, 0.55), (0.43, 0.35)]
    tri_inv    = [(0.30, 0.1), (0.70, 0.1), (0.57, 0.35), (0.43, 0.35)]
    # For the oval, generate points along an ellipse
    t = np.linspace(0, 2 * np.pi, 200)
    oval_x = 0.5 + 0.12 * np.cos(t)
    oval_y = 0.33 + 0.22 * np.sin(t)

    # Draw the polygonal shapes
    draw_shape(axes[0], retangular, "Retangular")
    draw_shape(axes[1], violao,     "Violão")
    draw_shape(axes[2], ampulheta,  "Ampulheta")
    draw_shape(axes[3], triangulo,  "Triângulo")
    draw_shape(axes[4], tri_inv,    "Triângulo invertido")
    # Draw the oval separately
    axes[5].fill(oval_x, oval_y, alpha=0.35, color="#cccccc")
    axes[5].plot(oval_x, oval_y, linewidth=2, color="#555555")
    axes[5].set_title("Oval", fontsize=10, pad=6)
    axes[5].set_aspect('equal')
    axes[5].axis('off')

    # Overall title
    fig.suptitle("Biótipos (figuras esquemáticas didáticas)", fontsize=12, y=0.98)
    fig.tight_layout()
    return fig
