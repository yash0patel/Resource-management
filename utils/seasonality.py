from __future__ import annotations


def season_from_month(month: int) -> str:
    """
    Map month to the one-hot season labels used by the ML models.

    US retail-inspired mapping:
    - Dec–Feb -> Winter
    - Mar–May -> Spring
    - Jun–Sep -> Summer
    - Oct–Nov -> Autumn
    """
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8, 9):
        return "Summer"
    return "Autumn"

