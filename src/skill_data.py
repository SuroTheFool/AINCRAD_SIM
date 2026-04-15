# skill_data.py
# ============================================================
# PASSIVE_SKILLS — shown in SKILLS > PASSIF tab (read-only overview)
# ACTIVE_SKILLS  — shown in SKILLS > ACTIF tab  (purchasable + equippable)
# HIDDEN_SKILLS   — obtainable ONLY via quest rewards, never in shop
# Active skill damage formula (same as normal clicks) :
#   instant  : damage = (click_damage + strength) * sqrt(INT) * dmg_multiplier
#   duration : the buff amplifies the normal click formula while active
# ============================================================

PASSIVE_SKILLS = [
    {
        "id"         : "click_damage",
        "label"      : "Swordsmanship Mastery",
        "description": "+3 damage per click",
        "type"       : "passive",
        "icon"       : "skill_swordsmanship.png",
    },
    {
        "id"         : "crit_chance",
        "label"      : "Spot Weakness",
        "description": "+5% critical hit chance",
        "type"       : "passive",
        "icon"       : "skill_weakness_spot.png",
    },
    {
        "id"         : "crit_multiplier",
        "label"      : "Berserker Rage",
        "description": "+0.5x critical multiplier",
        "type"       : "passive",
        "icon"       : "skill_critical_hit_amplifier.png",
    },
    {
        "id"         : "auto_dps",
        "label"      : "Fast Slash",
        "description": "+2 damage per second (auto)",
        "type"       : "passive",
        "icon"       : "skill_slashing_auto.png",
    },
    {
        "id"         : "gold_multiplier",
        "label"      : "Profit Maker",
        "description": "+0.2x Magic Stone rewards",
        "type"       : "passive",
        "icon"       : "skill_profit_maker.png",
    },
    {
        "id"         : "strength",
        "label"      : "Body Enhancement",
        "description": "+1 STR — flat bonus to every hit",
        "type"       : "passive",
        "icon"       : "skill_strength.png",
    },
    {
        "id"         : "intelligence",
        "label"      : "Spell Amplifier",
        "description": "+1 INT — multiplies damage via √INT",
        "type"       : "passive",
        "icon"       : "skill_intelligence.png",
    },
    {
        "id"         : "endurance",
        "label"      : "Iron Will",
        "description": "+1 END — increases endurance bar by 10",
        "type"       : "passive",
        "icon"       : "skill_endurance.png",
    },
]

ACTIVE_SKILLS = [
    {
        "id"          : "sword_burst",
        "label"       : "Sword Burst",
        "description" : "Deal damages instantly",
        "type"        : "active",
        "effect_type" : "instant",
        "duration"    : 0.0,
        "cost_end"    : 10,
        "icon"        : "skill_burst.png",
        "min_floor"   : 0,
        "base_cost"   : 300,
        "cost_growth" : 2.0,
        # Formula : (click_damage + strength) * sqrt(INT) * dmg_multiplier
        "dmg_multiplier": 2,
    },
    {
        "id"          : "battle_aura",
        "label"       : "Battle Aura",
        "description" : "+50% to you basic slash for 5s",
        "type"        : "active",
        "effect_type" : "duration",
        "duration"    : 5.0,
        "cost_end"    : 25,
        "icon"        : "skill_aura.png",
        "min_floor"   : 0,
        "base_cost"   : 250,
        "cost_growth" : 1.9,
        # Multiplies final damage by (1 + dmg_bonus_pct) while active
        "dmg_bonus_pct": 0.50,
    },
    {
        "id"          : "shadow_step",
        "label"       : "Shadow Step",
        "description" : "Double crit chance for 3 seconds",
        "type"        : "active",
        "effect_type" : "duration",
        "duration"    : 3.0,
        "cost_end"    : 20,
        "icon"        : "skill_shadow_step.png",
        "min_floor"   : 1,
        "base_cost"   : 200,
        "cost_growth" : 1.8,
            "crit_multiplier": 2.0,
    },
]

# ============================================================
# HIDDEN SKILLS
# ============================================================
# Rules :
#   - Never appear in the shop purchase list
#   - Unlocked exclusively through quest rewards (one per floor)
#   - Upgradable via the shop AFTER unlock (new tab "HIDDEN" to add later)
#   - upgrade_per_level : how much the key stat increases per upgrade
#   - base_upgrade_cost / upgrade_cost_growth : upgrade pricing
#
# Double Strike — Floor 1 hidden skill
#   While active, every click fires TWICE.
#   Stacks with other active skills :
#     - sword_burst  triggers twice  (2x instant damage)
#     - battle_aura  keeps its +50%  bonus on both clicks
#     - shadow_step  keeps its crit  bonus on both clicks
#   Base duration : 3s   (+0.5s per upgrade level)
# ============================================================

HIDDEN_SKILLS = [
    {
        "id": "double_strike",
        "label": "Double Strike",
        "description": "Every click hits twice for 3s",
        "type": "active",
        "effect_type": "duration",
        "hidden": True,  # never shown in normal shop list
        "floor_source": 1,  # rewarded by Floor 1 quest
        "icon": "skill_double_strike.png",

        "cost_end": 15,
        "base_duration": 3.0,
        "upgrade_per_level": 0.5,  # +0.5s per level
        # duration at level N = base_duration + upgrade_per_level * N

        # --- Upgrade cost (paid with Magic Stones in shop) ---
        "base_upgrade_cost": 400,
        "upgrade_cost_growth": 2.2,

        # --- Equip slot (same system as ACTIVE_SKILLS) ---
        "min_floor": 0,  # no floor restriction once unlocked
    },
]


# ============================================================
# HELPERS
# ============================================================

def get_skill_by_id(skill_id: str):
    """Search ACTIVE_SKILLS then HIDDEN_SKILLS. Returns None if not found."""
    for skill in ACTIVE_SKILLS:
        if skill["id"] == skill_id:
            return skill
    for skill in HIDDEN_SKILLS:
        if skill["id"] == skill_id:
            return skill
    return None


def get_hidden_skill_duration(skill_id: str, level: int) -> float:
    """
    Compute the effective duration of a hidden skill at a given upgrade level.
    Returns base_duration + upgrade_per_level * level.
    """
    for skill in HIDDEN_SKILLS:
        if skill["id"] == skill_id:
            return skill["base_duration"] + skill["upgrade_per_level"] * level
    return 0.0


def get_hidden_skill_upgrade_cost(skill_id: str, level: int) -> int:
    """
    Cost to upgrade a hidden skill from `level` to `level + 1`.
    Formula : base_upgrade_cost * (upgrade_cost_growth ^ level)
    """
    for skill in HIDDEN_SKILLS:
        if skill["id"] == skill_id:
            return int(
                skill["base_upgrade_cost"]
                * (skill["upgrade_cost_growth"] ** level)
            )
    return 0
