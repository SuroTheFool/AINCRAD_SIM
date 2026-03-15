# skill_data.py
# ============================================================
# PASSIVE_SKILLS — shown in SKILLS > PASSIF tab (read-only overview)
# ACTIVE_SKILLS  — shown in SKILLS > ACTIF tab  (purchasable + equippable)
#
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
        "description" : "Deal (click + STR) × √INT × 20x instantly",
        "type"        : "active",
        "effect_type" : "instant",
        "duration"    : 0.0,
        "cost_end"    : 30,
        "icon"        : "skill_sword_burst.png",
        "min_floor"   : 0,
        "base_cost"   : 300,
        "cost_growth" : 2.0,
        # Formula : (click_damage + strength) * sqrt(INT) * dmg_multiplier
        "dmg_multiplier": 2,
    },
    {
        "id"          : "battle_aura",
        "label"       : "Battle Aura",
        "description" : "+50% to (click + STR) × √INT for 5s",
        "type"        : "active",
        "effect_type" : "duration",
        "duration"    : 5.0,
        "cost_end"    : 25,
        "icon"        : "skill_battle_aura.png",
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