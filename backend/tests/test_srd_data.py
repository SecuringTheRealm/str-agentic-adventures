"""
Tests for expanded SRD reference data:
- XP_THRESHOLDS
- Monster stat blocks
- Weapon tables
- Armor AC table
"""


from app.srd_data import (
    XP_THRESHOLDS,
    calculate_armor_class,
    get_all_armor,
    get_all_weapons,
    get_armor_by_category,
    get_armor_by_id,
    get_level_for_xp,
    get_monster_by_id,
    get_monster_by_name,
    get_monsters_by_cr,
    get_monsters_by_type,
    get_weapon_by_id,
    get_weapons_by_category,
    get_weapons_with_property,
    load_armor,
    load_monsters,
    load_weapons,
)

# ---------------------------------------------------------------------------
# XP Thresholds
# ---------------------------------------------------------------------------


class TestXPThresholds:
    """Tests for XP_THRESHOLDS constant."""

    def test_all_20_levels_present(self) -> None:
        assert len(XP_THRESHOLDS) == 20
        for level in range(1, 21):
            assert level in XP_THRESHOLDS

    def test_level_1_starts_at_zero(self) -> None:
        assert XP_THRESHOLDS[1] == 0

    def test_level_20_threshold(self) -> None:
        assert XP_THRESHOLDS[20] == 355000

    def test_thresholds_are_strictly_increasing(self) -> None:
        values = [XP_THRESHOLDS[lvl] for lvl in range(1, 21)]
        for i in range(1, len(values)):
            assert values[i] > values[i - 1], (
                f"Level {i + 1} threshold {values[i]} is not greater than "
                f"level {i} threshold {values[i - 1]}"
            )

    def test_spot_check_values(self) -> None:
        assert XP_THRESHOLDS[2] == 300
        assert XP_THRESHOLDS[5] == 6500
        assert XP_THRESHOLDS[10] == 64000
        assert XP_THRESHOLDS[15] == 165000

    def test_get_level_for_xp_level_1(self) -> None:
        assert get_level_for_xp(0) == 1
        assert get_level_for_xp(100) == 1
        assert get_level_for_xp(299) == 1

    def test_get_level_for_xp_level_2(self) -> None:
        assert get_level_for_xp(300) == 2
        assert get_level_for_xp(500) == 2

    def test_get_level_for_xp_level_5(self) -> None:
        assert get_level_for_xp(6500) == 5

    def test_get_level_for_xp_level_20(self) -> None:
        assert get_level_for_xp(355000) == 20
        assert get_level_for_xp(1000000) == 20


# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------


class TestMonsters:
    """Tests for monster stat block data."""

    REQUIRED_MONSTER_IDS = [
        "goblin",
        "kobold",
        "skeleton",
        "zombie",
        "wolf",
        "giant_spider",
        "orc",
        "ogre",
        "troll",
        "owlbear",
        "giant_rat",
        "bandit",
        "guard",
        "commoner",
        "animated_armor",
    ]

    REQUIRED_FIELDS = [
        "id",
        "name",
        "cr",
        "xp",
        "ac",
        "hp",
        "abilities",
        "attack_bonus",
        "damage_dice",
    ]

    def test_load_returns_list(self) -> None:
        monsters = load_monsters()
        assert isinstance(monsters, list)
        assert len(monsters) >= 15

    def test_all_required_monsters_present(self) -> None:
        monster_ids = {m["id"] for m in load_monsters()}
        for mid in self.REQUIRED_MONSTER_IDS:
            assert mid in monster_ids, f"Monster '{mid}' missing from data"

    def test_each_monster_has_required_fields(self) -> None:
        for monster in load_monsters():
            for field in self.REQUIRED_FIELDS:
                assert field in monster, (
                    f"Monster '{monster.get('id')}' missing field '{field}'"
                )

    def test_abilities_block_has_six_scores(self) -> None:
        ability_keys = {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }
        for monster in load_monsters():
            abilities = monster.get("abilities", {})
            assert ability_keys == set(abilities.keys()), (
                f"Monster '{monster.get('id')}' has unexpected abilities: "
                f"{set(abilities.keys())}"
            )

    def test_xp_is_non_negative_integer(self) -> None:
        for monster in load_monsters():
            xp = monster.get("xp")
            assert isinstance(xp, int), f"Monster '{monster.get('id')}' xp is not int"
            assert xp >= 0, f"Monster '{monster.get('id')}' xp is negative"

    def test_get_monster_by_id_goblin(self) -> None:
        goblin = get_monster_by_id("goblin")
        assert goblin is not None
        assert goblin["name"] == "Goblin"
        assert goblin["cr"] == "1/4"
        assert goblin["xp"] == 50

    def test_get_monster_by_id_returns_none_for_unknown(self) -> None:
        assert get_monster_by_id("nonexistent_monster") is None

    def test_get_monster_by_name_case_insensitive(self) -> None:
        assert get_monster_by_name("Goblin") is not None
        assert get_monster_by_name("goblin") is not None
        assert get_monster_by_name("GOBLIN") is not None

    def test_get_monster_by_name_returns_none_for_unknown(self) -> None:
        assert get_monster_by_name("Purple Dragon") is None

    def test_get_monsters_by_cr(self) -> None:
        quarter_cr = get_monsters_by_cr("1/4")
        assert len(quarter_cr) >= 1
        assert all(str(m["cr"]) == "1/4" for m in quarter_cr)

    def test_get_monsters_by_type_undead(self) -> None:
        undead = get_monsters_by_type("undead")
        assert len(undead) >= 2
        ids = {m["id"] for m in undead}
        assert "skeleton" in ids
        assert "zombie" in ids

    def test_get_monsters_by_type_humanoid(self) -> None:
        humanoids = get_monsters_by_type("humanoid")
        assert len(humanoids) >= 4

    def test_animated_armor_has_immunities(self) -> None:
        animated = get_monster_by_id("animated_armor")
        assert animated is not None
        immunities = animated.get("damage_immunities", [])
        assert "poison" in immunities
        assert "psychic" in immunities


# ---------------------------------------------------------------------------
# Weapons
# ---------------------------------------------------------------------------


class TestWeapons:
    """Tests for weapon damage table data."""

    REQUIRED_SIMPLE_MELEE = [
        "club",
        "dagger",
        "greatclub",
        "handaxe",
        "javelin",
        "light_hammer",
        "mace",
        "quarterstaff",
        "sickle",
        "spear",
    ]

    REQUIRED_SIMPLE_RANGED = ["light_crossbow", "dart", "shortbow", "sling"]

    REQUIRED_MARTIAL_MELEE = [
        "battleaxe",
        "glaive",
        "greataxe",
        "greatsword",
        "longsword",
        "rapier",
        "scimitar",
        "shortsword",
    ]

    REQUIRED_MARTIAL_RANGED = [
        "hand_crossbow",
        "heavy_crossbow",
        "longbow",
    ]

    REQUIRED_FIELDS = ["id", "name", "damage_dice", "damage_type", "properties"]

    def test_load_returns_dict_with_categories(self) -> None:
        weapons = load_weapons()
        assert isinstance(weapons, dict)
        assert "simple_melee" in weapons
        assert "simple_ranged" in weapons
        assert "martial_melee" in weapons
        assert "martial_ranged" in weapons

    def test_all_simple_melee_present(self) -> None:
        category = get_weapons_by_category("simple_melee")
        ids = {w["id"] for w in category}
        for wid in self.REQUIRED_SIMPLE_MELEE:
            assert wid in ids, f"Simple melee weapon '{wid}' missing"

    def test_all_simple_ranged_present(self) -> None:
        category = get_weapons_by_category("simple_ranged")
        ids = {w["id"] for w in category}
        for wid in self.REQUIRED_SIMPLE_RANGED:
            assert wid in ids, f"Simple ranged weapon '{wid}' missing"

    def test_all_martial_melee_present(self) -> None:
        category = get_weapons_by_category("martial_melee")
        ids = {w["id"] for w in category}
        for wid in self.REQUIRED_MARTIAL_MELEE:
            assert wid in ids, f"Martial melee weapon '{wid}' missing"

    def test_all_martial_ranged_present(self) -> None:
        category = get_weapons_by_category("martial_ranged")
        ids = {w["id"] for w in category}
        for wid in self.REQUIRED_MARTIAL_RANGED:
            assert wid in ids, f"Martial ranged weapon '{wid}' missing"

    def test_each_weapon_has_required_fields(self) -> None:
        for weapon in get_all_weapons():
            for field in self.REQUIRED_FIELDS:
                assert field in weapon, (
                    f"Weapon '{weapon.get('id')}' missing field '{field}'"
                )

    def test_properties_is_list(self) -> None:
        for weapon in get_all_weapons():
            assert isinstance(weapon["properties"], list), (
                f"Weapon '{weapon.get('id')}' properties is not a list"
            )

    def test_get_weapon_by_id_longsword(self) -> None:
        longsword = get_weapon_by_id("longsword")
        assert longsword is not None
        assert longsword["name"] == "Longsword"
        assert longsword["damage_dice"] == "1d8"
        assert longsword["damage_type"] == "slashing"
        assert "versatile" in longsword["properties"]

    def test_get_weapon_by_id_unknown(self) -> None:
        assert get_weapon_by_id("laser_rifle") is None

    def test_get_weapons_with_property_finesse(self) -> None:
        finesse = get_weapons_with_property("finesse")
        ids = {w["id"] for w in finesse}
        assert "dagger" in ids
        assert "rapier" in ids
        assert "scimitar" in ids

    def test_get_weapons_with_property_heavy(self) -> None:
        heavy = get_weapons_with_property("heavy")
        ids = {w["id"] for w in heavy}
        assert "greataxe" in ids
        assert "greatsword" in ids

    def test_dagger_has_thrown_property_with_range(self) -> None:
        dagger = get_weapon_by_id("dagger")
        assert dagger is not None
        assert "thrown" in dagger["properties"]
        assert "range" in dagger

    def test_versatile_weapons_have_versatile_damage(self) -> None:
        for weapon in get_all_weapons():
            if "versatile" in weapon.get("properties", []):
                assert "versatile_damage_dice" in weapon, (
                    f"Versatile weapon '{weapon.get('id')}' "
                    "missing versatile_damage_dice"
                )

    def test_get_all_weapons_flat_list(self) -> None:
        all_weapons = get_all_weapons()
        assert isinstance(all_weapons, list)
        assert len(all_weapons) >= 30


# ---------------------------------------------------------------------------
# Armor
# ---------------------------------------------------------------------------


class TestArmor:
    """Tests for armor AC table data."""

    REQUIRED_ARMOR_IDS = [
        "padded",
        "leather",
        "studded_leather",
        "hide",
        "chain_shirt",
        "scale_mail",
        "breastplate",
        "half_plate",
        "ring_mail",
        "chain_mail",
        "splint",
        "plate",
        "shield",
    ]

    REQUIRED_FIELDS = [
        "id",
        "name",
        "category",
        "base_ac",
        "dex_bonus_cap",
        "strength_req",
        "stealth_disadvantage",
    ]

    def test_load_returns_dict_with_categories(self) -> None:
        armor = load_armor()
        assert isinstance(armor, dict)
        assert "light" in armor
        assert "medium" in armor
        assert "heavy" in armor
        assert "shield" in armor

    def test_all_required_armor_present(self) -> None:
        all_ids = {a["id"] for a in get_all_armor()}
        for aid in self.REQUIRED_ARMOR_IDS:
            assert aid in all_ids, f"Armor '{aid}' missing from data"

    def test_each_armor_has_required_fields(self) -> None:
        for armor in get_all_armor():
            for field in self.REQUIRED_FIELDS:
                assert field in armor, (
                    f"Armor '{armor.get('id')}' missing field '{field}'"
                )

    def test_stealth_disadvantage_is_bool(self) -> None:
        for armor in get_all_armor():
            val = armor.get("stealth_disadvantage")
            assert isinstance(val, bool), (
                f"Armor '{armor.get('id')}' stealth_disadvantage is not bool"
            )

    def test_light_armor_has_no_dex_cap(self) -> None:
        for armor in get_armor_by_category("light"):
            assert armor.get("dex_bonus_cap") is None, (
                f"Light armor '{armor.get('id')}' should have no DEX cap"
            )

    def test_heavy_armor_has_zero_dex_bonus(self) -> None:
        for armor in get_armor_by_category("heavy"):
            assert armor.get("dex_bonus_cap") == 0, (
                f"Heavy armor '{armor.get('id')}' should have dex_bonus_cap=0"
            )

    def test_plate_requires_strength(self) -> None:
        plate = get_armor_by_id("plate")
        assert plate is not None
        assert plate["strength_req"] == 15
        assert plate["base_ac"] == 18

    def test_get_armor_by_id_leather(self) -> None:
        leather = get_armor_by_id("leather")
        assert leather is not None
        assert leather["base_ac"] == 11
        assert leather["stealth_disadvantage"] is False

    def test_get_armor_by_id_unknown(self) -> None:
        assert get_armor_by_id("mithral_shirt") is None

    def test_calculate_ac_unarmored(self) -> None:
        # No armor ID should yield 10 + DEX mod
        assert calculate_armor_class("none", 3) == 13

    def test_calculate_ac_leather(self) -> None:
        # Leather: 11 + DEX (no cap)
        assert calculate_armor_class("leather", 3) == 14
        assert calculate_armor_class("leather", 5) == 16

    def test_calculate_ac_chain_mail(self) -> None:
        # Chain mail: 16, no DEX bonus
        assert calculate_armor_class("chain_mail", 3) == 16
        assert calculate_armor_class("chain_mail", -1) == 16

    def test_calculate_ac_breastplate(self) -> None:
        # Breastplate: 14 + max 2 DEX
        assert calculate_armor_class("breastplate", 3) == 16
        assert calculate_armor_class("breastplate", 5) == 16  # capped at +2

    def test_calculate_ac_with_shield(self) -> None:
        # Leather + shield: 11 + DEX + 2
        assert calculate_armor_class("leather", 2, shield=True) == 15

    def test_get_all_armor_flat_list(self) -> None:
        all_armor = get_all_armor()
        assert isinstance(all_armor, list)
        assert len(all_armor) >= 13
