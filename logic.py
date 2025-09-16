"""
logic.py
-----------

This module contains the core sizing logic for the Guia de Tabela de Medidas
application. It defines a reference size chart based on ABNT-like increments,
utilities for classifying estatura (height ranges), and functions for
computing the best matching clothing size given a person's measurements and
biótipo (body type).

The chart uses a numeric size progression (34–62) with regular 4 cm
increments for bust, waist and hip circumferences. While the actual ABNT
standards include more granular grading and may vary by garment or brand,
this simplified table provides a didactic reference as requested by the
project specification.

All distances are calculated using a weighted Euclidean metric: the
difference between the user’s measurement and the reference value is
multiplied by a weight for each body type before summing and taking the
square root. A smaller distance indicates a better fit. See
``BIOTIPO_WEIGHTS`` for the weighting scheme.

"""

import math
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# Size chart definition
# ---------------------------------------------------------------------------

# Numeric sizes from 34 to 62 (inclusive) in steps of 2.  This yields 15
# possible sizes: 34, 36, ..., 62.
SIZES: List[int] = list(range(34, 64, 2))

# Reference circumferences in centimetres.  Each sequence begins with the
# smallest plausible value for size 34 and increases by 4 cm with each size.
BUST_SEQ: List[int] = [80 + 4 * i for i in range(len(SIZES))]
WAIST_SEQ: List[int] = [68 + 4 * i for i in range(len(SIZES))]
HIP_SEQ: List[int] = [86 + 4 * i for i in range(len(SIZES))]

# Combine the numeric size and reference measurements into a single list of
# dictionaries.  Each entry holds the numeric size along with the bust,
# waist and hip circumferences for that size.
SIZE_CHART: List[Dict[str, float]] = [
    {"size": s, "bust": b, "waist": w, "hip": h}
    for s, b, w, h in zip(SIZES, BUST_SEQ, WAIST_SEQ, HIP_SEQ)
]

# ---------------------------------------------------------------------------
# Estatura (height) classification
# ---------------------------------------------------------------------------

# Height bins for classifying the user's estatura into baixa, média or alta.
STATURE_BINS: Dict[str, Tuple[int, int]] = {
    "baixa": (150, 157),
    "média": (158, 165),
    "alta":  (166, 181),
}

def classify_estatura(altura_cm: float) -> str:
    """Classify height into 'baixa', 'média' or 'alta'.

    If the height falls outside the defined bins, it will be approximated to
    the nearest category. Heights below the lowest bin map to 'baixa' and
    heights above the highest bin map to 'alta'.

    Parameters
    ----------
    altura_cm : float
        Height in centimetres.

    Returns
    -------
    str
        One of 'baixa', 'média' or 'alta'.
    """
    for nome, (lo, hi) in STATURE_BINS.items():
        if lo <= altura_cm <= hi:
            return nome
    # If outside the bins, approximate to nearest category
    min_bin_low = min(bin_range[0] for bin_range in STATURE_BINS.values())
    max_bin_high = max(bin_range[1] for bin_range in STATURE_BINS.values())
    if altura_cm < min_bin_low:
        return "baixa"
    if altura_cm > max_bin_high:
        return "alta"
    # In-between gaps: default to média
    return "média"

# ---------------------------------------------------------------------------
# Body type weighting
# ---------------------------------------------------------------------------

# Weighting factors for each body type.  These values influence the
# importance of bust, waist and hip deviations when computing the distance
# between the user's measurements and the reference chart.  Higher weights
# indicate a greater impact on the distance.  See the project specification
# for an explanation of these values.
BIOTIPO_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Retangular":          {"bust": 1.0, "waist": 1.0, "hip": 1.0},
    "Violão":              {"bust": 0.8, "waist": 1.0, "hip": 1.2},
    "Ampulheta":           {"bust": 1.2, "waist": 1.4, "hip": 1.2},
    "Triângulo":           {"bust": 0.8, "waist": 1.0, "hip": 1.4},
    "Triângulo invertido": {"bust": 1.4, "waist": 1.0, "hip": 0.8},
    "Oval":                {"bust": 1.0, "waist": 1.6, "hip": 1.0},
}

# Short advisory text per body type.  These are used in the app to offer
# qualitative guidance alongside the numeric size suggestion.
BIOTIPO_TIPS: Dict[str, str] = {
    "Retangular":          "Cintura pouco marcada: recortes que criem leve definição ajudam.",
    "Violão":              "Priorize ajuste pelo quadril; cintura pode pedir ajuste.",
    "Ampulheta":           "Busque equilíbrio; atenção à folga confortável na cintura.",
    "Triângulo":           "Escolha pelo quadril e ajuste cintura/gancho se preciso.",
    "Triângulo invertido": "Escolha pelo busto; barra/quadril podem ajustar.",
    "Oval":                "Conforto na região média; caimento reto com folga adequada.",
}

def score_sizes(user_bust: float, user_waist: float, user_hip: float, biotipo: str) -> List[Dict[str, float]]:
    """Compute a list of candidate sizes ordered by fit distance.

    The distance metric used is a weighted Euclidean distance between the
    user's measurements and each entry in the reference size chart.  The
    weights applied depend on the chosen body type (bíotipo).

    Parameters
    ----------
    user_bust : float
        User's bust circumference in centimetres.
    user_waist : float
        User's waist circumference in centimetres.
    user_hip : float
        User's hip circumference in centimetres.
    biotipo : str
        The name of the body type.  If an unknown value is provided, the
        weights default to those for the 'Retangular' type.

    Returns
    -------
    List[Dict[str, float]]
        A list of dictionaries sorted in ascending order of distance.  Each
        dictionary contains the keys 'size', 'dist', 'bust', 'waist' and
        'hip'.  The 'dist' key holds the computed distance to the user.
    """
    weights = BIOTIPO_WEIGHTS.get(biotipo, BIOTIPO_WEIGHTS["Retangular"])
    scored: List[Dict[str, float]] = []
    for row in SIZE_CHART:
        db = (user_bust - row["bust"]) * weights["bust"]
        dw = (user_waist - row["waist"]) * weights["waist"]
        dh = (user_hip - row["hip"]) * weights["hip"]
        dist = math.sqrt(db ** 2 + dw ** 2 + dh ** 2)
        scored.append({
            "size": row["size"],
            "dist": dist,
            "bust": row["bust"],
            "waist": row["waist"],
            "hip": row["hip"],
        })
    # Sort by ascending distance
    scored.sort(key=lambda x: x["dist"])
    return scored

def suggest_size_and_top(user_bust: float, user_waist: float, user_hip: float, biotipo: str, top_n: int = 3):
    """Return the best size suggestion and a list of top candidates.

    Parameters
    ----------
    user_bust : float
        User's bust circumference in centimetres.
    user_waist : float
        User's waist circumference in centimetres.
    user_hip : float
        User's hip circumference in centimetres.
    biotipo : str
        Body type name used to select weighting factors.
    top_n : int, optional
        Number of top candidate sizes to return.  Defaults to 3.

    Returns
    -------
    Tuple[Dict[str, float], List[Dict[str, float]]]
        A tuple containing the best-matching size (the first entry of the
        scored list) and a list of the top ``top_n`` candidate sizes.
    """
    scored = score_sizes(user_bust, user_waist, user_hip, biotipo)
    best = scored[0] if scored else None
    top_candidates = scored[:top_n]
    return best, top_candidates
