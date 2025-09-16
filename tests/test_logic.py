"""
Basic tests for the sizing logic. These tests validate that the distance
computation in logic.score_sizes produces an ascending ordering of
distances and that increasing all measurements results in a suggested size
that is the same or larger.
"""

from logic import score_sizes, suggest_size_and_top

def test_scores_are_sorted():
    """The scores returned should be sorted by ascending distance."""
    scores = score_sizes(user_bust=90, user_waist=74, user_hip=98, biotipo="Retangular")
    dists = [entry["dist"] for entry in scores]
    assert dists == sorted(dists), "Distances are not sorted ascendingly"


def test_size_increases_with_measurements():
    """Increasing all measurements should not yield a smaller suggested size."""
    # Person A has smaller measurements
    best_small, _ = suggest_size_and_top(user_bust=90, user_waist=74, user_hip=98, biotipo="Retangular")
    # Person B has larger measurements
    best_big, _ = suggest_size_and_top(user_bust=110, user_waist=94, user_hip=118, biotipo="Retangular")
    assert best_big["size"] >= best_small["size"], (
        f"Expected larger measurements to yield same or larger size; got {best_small['size']} and {best_big['size']}"
    )
