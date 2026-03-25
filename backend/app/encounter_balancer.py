"""
Encounter Balancer - CR-based encounter difficulty and XP budget system.

Implements D&D 5e SRD rules for encounter difficulty thresholds, XP budgets,
and encounter generation to ensure parties face appropriately challenging foes.
"""

from __future__ import annotations

import logging
import random
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Encounter difficulty thresholds (XP per character per level, D&D 5e SRD)
# ---------------------------------------------------------------------------

ENCOUNTER_DIFFICULTY_THRESHOLDS: dict[int, dict[str, int]] = {
    1:  {"easy": 25,   "medium": 50,   "hard": 75,   "deadly": 100},
    2:  {"easy": 50,   "medium": 100,  "hard": 150,  "deadly": 200},
    3:  {"easy": 75,   "medium": 150,  "hard": 225,  "deadly": 400},
    4:  {"easy": 125,  "medium": 250,  "hard": 375,  "deadly": 500},
    5:  {"easy": 250,  "medium": 500,  "hard": 750,  "deadly": 1100},
    6:  {"easy": 300,  "medium": 600,  "hard": 900,  "deadly": 1400},
    7:  {"easy": 350,  "medium": 750,  "hard": 1100, "deadly": 1700},
    8:  {"easy": 450,  "medium": 900,  "hard": 1400, "deadly": 2100},
    9:  {"easy": 550,  "medium": 1100, "hard": 1600, "deadly": 2400},
    10: {"easy": 600,  "medium": 1200, "hard": 1900, "deadly": 2800},
    11: {"easy": 800,  "medium": 1600, "hard": 2400, "deadly": 3600},
    12: {"easy": 1000, "medium": 2000, "hard": 3000, "deadly": 4500},
    13: {"easy": 1100, "medium": 2200, "hard": 3400, "deadly": 5100},
    14: {"easy": 1250, "medium": 2500, "hard": 3800, "deadly": 5700},
    15: {"easy": 1400, "medium": 2800, "hard": 4300, "deadly": 6400},
    16: {"easy": 1600, "medium": 3200, "hard": 4800, "deadly": 7200},
    17: {"easy": 2000, "medium": 3900, "hard": 5900, "deadly": 8800},
    18: {"easy": 2100, "medium": 4200, "hard": 6300, "deadly": 9500},
    19: {"easy": 2400, "medium": 4900, "hard": 7300, "deadly": 10900},
    20: {"easy": 2800, "medium": 5700, "hard": 8500, "deadly": 12700},
}

# ---------------------------------------------------------------------------
# CR to XP conversion (D&D 5e SRD)
# ---------------------------------------------------------------------------

CR_TO_XP: dict[str, int] = {
    "0":    10,
    "1/8":  25,
    "1/4":  50,
    "1/2":  100,
    "1":    200,
    "2":    450,
    "3":    700,
    "4":    1100,
    "5":    1800,
    "6":    2300,
    "7":    2900,
    "8":    3900,
    "9":    5000,
    "10":   5900,
    "11":   7200,
    "12":   8400,
    "13":   10000,
    "14":   11500,
    "15":   13000,
    "16":   15000,
    "17":   18000,
    "18":   20000,
    "19":   22000,
    "20":   25000,
    "21":   33000,
    "22":   41000,
    "23":   50000,
    "24":   62000,
    "30":   155000,
}

# ---------------------------------------------------------------------------
# Encounter multipliers based on number of monsters
# ---------------------------------------------------------------------------

# Base multiplier steps ordered from lowest to highest
_MULTIPLIER_STEPS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]


def _base_multiplier(num_monsters: int) -> float:
    """Return the base encounter multiplier for the given number of monsters."""
    if num_monsters <= 0:
        return 1.0
    if num_monsters == 1:
        return 1.0
    if num_monsters == 2:
        return 1.5
    if num_monsters <= 6:
        return 2.0
    if num_monsters <= 10:
        return 2.5
    if num_monsters <= 14:
        return 3.0
    return 4.0


def get_encounter_multiplier(num_monsters: int, party_size: int) -> float:
    """
    Return the XP multiplier for an encounter.

    Small parties (1-2) face tougher odds, so multiply up one step.
    Large parties (6+) have an advantage, so multiply down one step.

    Args:
        num_monsters: Total number of monsters in the encounter.
        party_size: Number of player characters in the party.

    Returns:
        Floating-point XP multiplier.
    """
    base = _base_multiplier(num_monsters)
    idx = _MULTIPLIER_STEPS.index(base) if base in _MULTIPLIER_STEPS else 2

    if party_size <= 2:
        idx = min(idx + 1, len(_MULTIPLIER_STEPS) - 1)
    elif party_size >= 6:
        idx = max(idx - 1, 0)

    return _MULTIPLIER_STEPS[idx]


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------


def cr_to_xp(cr: str) -> int:
    """Convert a Challenge Rating string to its XP value.

    Args:
        cr: Challenge Rating as a string (e.g. "1/4", "5", "0").

    Returns:
        Integer XP value.  Returns 0 for unknown CRs.
    """
    return CR_TO_XP.get(str(cr), 0)


def calculate_encounter_xp(
    monsters: list[dict[str, Any]], party_size: int
) -> dict[str, Any]:
    """Calculate the adjusted XP budget for an encounter.

    The *adjusted* XP is used only to determine difficulty; the *raw* XP is
    what characters actually earn.

    Args:
        monsters: List of monster stat-block dicts.  Each must have a ``"cr"``
            (or ``"xp"``) key.
        party_size: Number of player characters in the party.

    Returns:
        Dict with keys:
            - ``raw_xp``: Sum of individual monster XP values.
            - ``adjusted_xp``: raw_xp × encounter multiplier.
            - ``multiplier``: The multiplier applied.
            - ``monster_count``: Number of monsters.
    """
    if not monsters:
        return {"raw_xp": 0, "adjusted_xp": 0, "multiplier": 1.0, "monster_count": 0}

    raw_xp = sum(
        m.get("xp") or cr_to_xp(str(m.get("cr", "0"))) for m in monsters
    )
    multiplier = get_encounter_multiplier(len(monsters), party_size)
    adjusted_xp = int(raw_xp * multiplier)

    return {
        "raw_xp": raw_xp,
        "adjusted_xp": adjusted_xp,
        "multiplier": multiplier,
        "monster_count": len(monsters),
    }


def get_party_xp_budget(party_levels: list[int], difficulty: str) -> int:
    """Return the total XP budget for the party at the requested difficulty.

    Args:
        party_levels: List of character levels (one entry per character).
        difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``, ``"deadly"``.

    Returns:
        Total XP budget (sum of per-character thresholds).
    """
    difficulty = difficulty.lower()
    total = 0
    for level in party_levels:
        level = max(1, min(20, level))  # clamp to [1, 20]
        thresholds = ENCOUNTER_DIFFICULTY_THRESHOLDS[level]
        total += thresholds.get(difficulty, thresholds["medium"])
    return total


def get_encounter_difficulty(
    party_levels: list[int],
    monsters: list[dict[str, Any]],
) -> str:
    """Determine the difficulty label for an encounter.

    Args:
        party_levels: List of character levels.
        monsters: List of monster stat-block dicts.

    Returns:
        One of ``"trivial"``, ``"easy"``, ``"medium"``, ``"hard"``, or
        ``"deadly"``.
    """
    if not party_levels or not monsters:
        return "trivial"

    party_size = len(party_levels)
    xp_info = calculate_encounter_xp(monsters, party_size)
    adjusted_xp = xp_info["adjusted_xp"]

    deadly_budget = get_party_xp_budget(party_levels, "deadly")
    hard_budget   = get_party_xp_budget(party_levels, "hard")
    medium_budget = get_party_xp_budget(party_levels, "medium")
    easy_budget   = get_party_xp_budget(party_levels, "easy")

    if adjusted_xp >= deadly_budget:
        return "deadly"
    if adjusted_xp >= hard_budget:
        return "hard"
    if adjusted_xp >= medium_budget:
        return "medium"
    if adjusted_xp >= easy_budget:
        return "easy"
    return "trivial"


def calculate_xp_award(
    monsters: list[dict[str, Any]],
    party_size: int,
) -> dict[str, Any]:
    """Calculate XP awarded to each character after defeating the monsters.

    Characters earn the *raw* (not adjusted) XP split evenly.

    Args:
        monsters: List of monster stat-block dicts.
        party_size: Number of player characters receiving XP.

    Returns:
        Dict with keys:
            - ``total_xp``: Total raw XP from all monsters.
            - ``xp_per_character``: XP each character earns (floored int).
            - ``party_size``: Number of characters.
    """
    if not monsters or party_size <= 0:
        return {"total_xp": 0, "xp_per_character": 0, "party_size": party_size}

    total_xp = sum(
        m.get("xp") or cr_to_xp(str(m.get("cr", "0"))) for m in monsters
    )
    xp_per_character = total_xp // max(party_size, 1)

    return {
        "total_xp": total_xp,
        "xp_per_character": xp_per_character,
        "party_size": party_size,
    }


# ---------------------------------------------------------------------------
# Encounter generator
# ---------------------------------------------------------------------------


def generate_balanced_encounter(
    party_levels: list[int],
    difficulty: str = "medium",
    location: str = "dungeon",
    available_monsters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate a balanced encounter for a party.

    Selects monsters from ``available_monsters`` (or loads the SRD monsters if
    not provided) until the adjusted XP reaches (but does not greatly exceed)
    the requested difficulty budget.

    Args:
        party_levels: List of character levels.
        difficulty: Desired difficulty (``"easy"``, ``"medium"``, ``"hard"``,
            ``"deadly"``).
        location: Location hint for thematic monster selection.
        available_monsters: Optional list of monster dicts to draw from.  If
            omitted the SRD monster list is loaded automatically.

    Returns:
        Dict with keys:
            - ``monsters``: List of selected monster dicts.
            - ``difficulty``: Actual difficulty label of the generated encounter.
            - ``xp_budget``: Target XP budget.
            - ``adjusted_xp``: Actual adjusted XP of the encounter.
            - ``raw_xp``: Total raw (award) XP.
            - ``xp_per_character``: XP each character earns.
            - ``party_size``: Party size.
    """
    if not party_levels:
        party_levels = [1]

    difficulty = difficulty.lower()
    party_size = len(party_levels)

    # Load monster pool
    if available_monsters is None:
        try:
            from app.srd_data import load_monsters

            available_monsters = load_monsters()
        except Exception:
            available_monsters = []

    if not available_monsters:
        return {
            "monsters": [],
            "difficulty": "trivial",
            "xp_budget": 0,
            "adjusted_xp": 0,
            "raw_xp": 0,
            "xp_per_character": 0,
            "party_size": party_size,
        }

    # Determine target XP budget
    xp_budget = get_party_xp_budget(party_levels, difficulty)

    # Filter monsters to those thematically appropriate for the location
    location_pool = _filter_monsters_for_location(available_monsters, location)
    if not location_pool:
        location_pool = available_monsters

    # Build encounter iteratively
    selected: list[dict[str, Any]] = []
    remaining_budget = xp_budget

    # Shuffle to add variety
    pool = list(location_pool)
    random.shuffle(pool)  # noqa: S311  # game randomness — no crypto requirement

    avg_level = sum(party_levels) / len(party_levels)

    for monster in pool:
        monster_xp = monster.get("xp") or cr_to_xp(str(monster.get("cr", "0")))
        if monster_xp <= 0:
            continue

        # Rough CR appropriateness check: avoid monsters far out of level range
        if not _is_cr_appropriate(monster.get("cr", "0"), avg_level):
            continue

        # Tentatively add this monster and check the adjusted budget
        tentative = selected + [monster]
        info = calculate_encounter_xp(tentative, party_size)
        # Allow up to 50% over target budget when building the encounter
        if info["adjusted_xp"] <= xp_budget * 1.5:
            selected.append(monster)
            remaining_budget -= monster_xp
            if info["adjusted_xp"] >= xp_budget * 0.8:
                # Good enough — stop adding
                break

    if not selected:
        # Last resort: pick the single weakest monster from the full pool
        sorted_pool = sorted(
            available_monsters,
            key=lambda m: m.get("xp") or cr_to_xp(str(m.get("cr", "0"))),
        )
        if sorted_pool:
            selected = [sorted_pool[0]]

    actual_difficulty = get_encounter_difficulty(party_levels, selected)
    xp_info = calculate_encounter_xp(selected, party_size)
    award_info = calculate_xp_award(selected, party_size)

    return {
        "monsters": selected,
        "difficulty": actual_difficulty,
        "xp_budget": xp_budget,
        "adjusted_xp": xp_info["adjusted_xp"],
        "raw_xp": xp_info["raw_xp"],
        "xp_per_character": award_info["xp_per_character"],
        "party_size": party_size,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_CR_AS_FLOAT: dict[str, float] = {
    "0":    0.0,
    "1/8":  0.125,
    "1/4":  0.25,
    "1/2":  0.5,
    "1":    1.0,
    "2":    2.0,
    "3":    3.0,
    "4":    4.0,
    "5":    5.0,
    "6":    6.0,
    "7":    7.0,
    "8":    8.0,
    "9":    9.0,
    "10":   10.0,
    "11":   11.0,
    "12":   12.0,
    "13":   13.0,
    "14":   14.0,
    "15":   15.0,
    "16":   16.0,
    "17":   17.0,
    "18":   18.0,
    "19":   19.0,
    "20":   20.0,
}

_LOCATION_MONSTER_TYPES: dict[str, list[str]] = {
    "forest":   ["humanoid", "beast", "fey"],
    "dungeon":  ["undead", "humanoid", "construct", "aberration"],
    "mountain": ["humanoid", "giant", "beast", "monstrosity"],
    "city":     ["humanoid"],
    "coastal":  ["humanoid", "beast", "monstrosity"],
    "swamp":    ["undead", "beast", "humanoid"],
    "cave":     ["humanoid", "undead", "beast", "monstrosity"],
    "plains":   ["humanoid", "beast"],
}


def _filter_monsters_for_location(
    monsters: list[dict[str, Any]],
    location: str,
) -> list[dict[str, Any]]:
    """Return a sub-list of monsters suitable for the given location."""
    preferred_types = _LOCATION_MONSTER_TYPES.get(location.lower(), [])
    if not preferred_types:
        return monsters
    filtered = [m for m in monsters if m.get("type", "").lower() in preferred_types]
    return filtered if filtered else monsters


def _is_cr_appropriate(cr: str, avg_party_level: float) -> bool:
    """Return True when the CR is within a reasonable range of the party level."""
    cr_float = _CR_AS_FLOAT.get(str(cr))
    if cr_float is None:
        try:
            cr_float = float(cr)
        except (ValueError, TypeError):
            return True  # Unknown CR — don't exclude

    # Allow CR 0 through (party_level + 3) to give a reasonable range
    return cr_float <= avg_party_level + 3
