"""
무기 데이터 정의
이 파일을 수정하여 무기를 추가/수정/삭제할 수 있습니다.

사용법:
1. 새 무기 추가: WEAPONS 딕셔너리에 새 항목 추가
2. 무기 수정: 해당 무기의 속성 값 변경
3. 무기 삭제: 해당 무기 항목 삭제

무기 속성 설명:
- name: 무기 이름 (한글)
- char: ASCII 문자
- color: RGB 색상 튜플
- weapon_type: "melee" | "ranged" | "magic"
- damage: 기본 데미지
- range: 사거리 (근접=1, 원거리/마법=2+)
- accuracy: 명중률 보너스 (%)
- speed: 공격 속도 (낮을수록 빠름)
- durability: 내구도 (0=무한)
- mana_cost: 마나 소모량 (마법무기용)
- effects: 특수 효과 리스트
- value: 상점 가격
- rarity: "common" | "uncommon" | "rare" | "epic" | "legendary"
- description: 설명
"""

# =============================================================================
# 무기 타입 정의
# =============================================================================
WEAPON_TYPES = {
    "melee": "근접",
    "ranged": "원거리",
    "magic": "마법",
}

# =============================================================================
# 근접 무기 (Melee Weapons)
# =============================================================================
MELEE_WEAPONS = {
    # --- 단검류 ---
    "dagger": {
        "name": "단검",
        "char": ")",
        "color": (192, 192, 192),
        "weapon_type": "melee",
        "damage": 3,
        "range": 1,
        "accuracy": 10,
        "speed": 1,
        "durability": 50,
        "mana_cost": 0,
        "effects": [],
        "value": 30,
        "rarity": "common",
        "description": "가볍고 빠른 단검.",
    },
    "silver_dagger": {
        "name": "은 단검",
        "char": ")",
        "color": (220, 220, 255),
        "weapon_type": "melee",
        "damage": 4,
        "range": 1,
        "accuracy": 10,
        "speed": 1,
        "durability": 40,
        "mana_cost": 0,
        "effects": ["undead_bane"],  # 언데드에게 추가 데미지
        "value": 80,
        "rarity": "uncommon",
        "description": "언데드에게 효과적인 은 단검.",
    },

    # --- 검류 ---
    "short_sword": {
        "name": "숏소드",
        "char": ")",
        "color": (180, 180, 180),
        "weapon_type": "melee",
        "damage": 5,
        "range": 1,
        "accuracy": 5,
        "speed": 2,
        "durability": 80,
        "mana_cost": 0,
        "effects": [],
        "value": 60,
        "rarity": "common",
        "description": "균형 잡힌 짧은 검.",
    },
    "long_sword": {
        "name": "롱소드",
        "char": ")",
        "color": (200, 200, 200),
        "weapon_type": "melee",
        "damage": 7,
        "range": 1,
        "accuracy": 0,
        "speed": 3,
        "durability": 100,
        "mana_cost": 0,
        "effects": [],
        "value": 100,
        "rarity": "uncommon",
        "description": "표준적인 긴 검.",
    },
    "steel_sword": {
        "name": "강철 검",
        "char": ")",
        "color": (150, 150, 180),
        "weapon_type": "melee",
        "damage": 10,
        "range": 1,
        "accuracy": 5,
        "speed": 3,
        "durability": 150,
        "mana_cost": 0,
        "effects": [],
        "value": 200,
        "rarity": "rare",
        "description": "단단한 강철로 만든 검.",
    },

    # --- 도끼류 ---
    "hand_axe": {
        "name": "손도끼",
        "char": ")",
        "color": (139, 90, 43),
        "weapon_type": "melee",
        "damage": 6,
        "range": 1,
        "accuracy": -5,
        "speed": 2,
        "durability": 60,
        "mana_cost": 0,
        "effects": [],
        "value": 40,
        "rarity": "common",
        "description": "한 손으로 쓰는 작은 도끼.",
    },
    "battle_axe": {
        "name": "전투 도끼",
        "char": ")",
        "color": (160, 100, 50),
        "weapon_type": "melee",
        "damage": 12,
        "range": 1,
        "accuracy": -10,
        "speed": 4,
        "durability": 120,
        "mana_cost": 0,
        "effects": ["armor_pierce"],  # 방어력 무시
        "value": 150,
        "rarity": "uncommon",
        "description": "무거운 양손 전투 도끼.",
    },

    # --- 둔기류 ---
    "club": {
        "name": "곤봉",
        "char": ")",
        "color": (101, 67, 33),
        "weapon_type": "melee",
        "damage": 4,
        "range": 1,
        "accuracy": 0,
        "speed": 2,
        "durability": 30,
        "mana_cost": 0,
        "effects": [],
        "value": 10,
        "rarity": "common",
        "description": "단순한 나무 곤봉.",
    },
    "mace": {
        "name": "철퇴",
        "char": ")",
        "color": (128, 128, 128),
        "weapon_type": "melee",
        "damage": 8,
        "range": 1,
        "accuracy": -5,
        "speed": 3,
        "durability": 100,
        "mana_cost": 0,
        "effects": ["stun"],  # 기절 확률
        "value": 80,
        "rarity": "uncommon",
        "description": "적을 기절시킬 수 있는 철퇴.",
    },

    # --- 창류 ---
    "spear": {
        "name": "창",
        "char": "/",
        "color": (139, 119, 101),
        "weapon_type": "melee",
        "damage": 6,
        "range": 2,  # 2칸 거리에서도 공격 가능
        "accuracy": 5,
        "speed": 3,
        "durability": 70,
        "mana_cost": 0,
        "effects": ["reach"],
        "value": 70,
        "rarity": "common",
        "description": "긴 사거리의 창.",
    },
}

# =============================================================================
# 원거리 무기 (Ranged Weapons)
# =============================================================================
RANGED_WEAPONS = {
    # --- 활류 ---
    "short_bow": {
        "name": "단궁",
        "char": "}",
        "color": (139, 90, 43),
        "weapon_type": "ranged",
        "damage": 4,
        "range": 6,
        "accuracy": 5,
        "speed": 2,
        "durability": 50,
        "mana_cost": 0,
        "effects": [],
        "ammo_type": "arrow",
        "value": 50,
        "rarity": "common",
        "description": "가벼운 단궁.",
    },
    "long_bow": {
        "name": "장궁",
        "char": "}",
        "color": (160, 100, 50),
        "weapon_type": "ranged",
        "damage": 7,
        "range": 10,
        "accuracy": 0,
        "speed": 3,
        "durability": 80,
        "mana_cost": 0,
        "effects": [],
        "ammo_type": "arrow",
        "value": 100,
        "rarity": "uncommon",
        "description": "사거리가 긴 장궁.",
    },
    "composite_bow": {
        "name": "합성궁",
        "char": "}",
        "color": (180, 120, 60),
        "weapon_type": "ranged",
        "damage": 9,
        "range": 8,
        "accuracy": 10,
        "speed": 2,
        "durability": 100,
        "mana_cost": 0,
        "effects": [],
        "ammo_type": "arrow",
        "value": 200,
        "rarity": "rare",
        "description": "정교하게 만든 합성궁.",
    },

    # --- 석궁류 ---
    "crossbow": {
        "name": "석궁",
        "char": "}",
        "color": (100, 80, 60),
        "weapon_type": "ranged",
        "damage": 10,
        "range": 7,
        "accuracy": 15,
        "speed": 5,  # 재장전이 느림
        "durability": 120,
        "mana_cost": 0,
        "effects": ["armor_pierce"],
        "ammo_type": "bolt",
        "value": 150,
        "rarity": "uncommon",
        "description": "강력하지만 느린 석궁.",
    },

    # --- 투척류 ---
    "throwing_knife": {
        "name": "투척용 단검",
        "char": ")",
        "color": (180, 180, 180),
        "weapon_type": "ranged",
        "damage": 3,
        "range": 4,
        "accuracy": 10,
        "speed": 1,
        "durability": 1,  # 일회용
        "mana_cost": 0,
        "effects": ["consumable"],  # 사용 후 소멸
        "ammo_type": "none",  # 탄약 불필요 (자체가 탄약)
        "value": 5,
        "rarity": "common",
        "description": "던져서 사용하는 단검.",
    },
    "javelin": {
        "name": "투창",
        "char": "/",
        "color": (139, 119, 101),
        "weapon_type": "ranged",
        "damage": 6,
        "range": 5,
        "accuracy": 0,
        "speed": 2,
        "durability": 1,
        "mana_cost": 0,
        "effects": ["consumable"],
        "ammo_type": "none",
        "value": 15,
        "rarity": "common",
        "description": "던져서 사용하는 창.",
    },
}

# =============================================================================
# 마법 무기 (Magic Weapons)
# =============================================================================
MAGIC_WEAPONS = {
    # --- 지팡이류 ---
    "apprentice_staff": {
        "name": "견습 지팡이",
        "char": "/",
        "color": (139, 90, 200),
        "weapon_type": "magic",
        "damage": 3,
        "range": 5,
        "accuracy": 10,
        "speed": 2,
        "durability": 0,  # 무한
        "mana_cost": 5,
        "effects": ["magic_damage"],
        "element": "arcane",
        "value": 100,
        "rarity": "common",
        "description": "초보 마법사의 지팡이.",
    },
    "fire_staff": {
        "name": "화염 지팡이",
        "char": "/",
        "color": (255, 100, 0),
        "weapon_type": "magic",
        "damage": 8,
        "range": 6,
        "accuracy": 5,
        "speed": 3,
        "durability": 0,
        "mana_cost": 10,
        "effects": ["magic_damage", "burn"],
        "element": "fire",
        "value": 300,
        "rarity": "rare",
        "description": "적을 불태우는 화염 지팡이.",
    },
    "ice_staff": {
        "name": "냉기 지팡이",
        "char": "/",
        "color": (100, 200, 255),
        "weapon_type": "magic",
        "damage": 6,
        "range": 6,
        "accuracy": 10,
        "speed": 3,
        "durability": 0,
        "mana_cost": 10,
        "effects": ["magic_damage", "freeze"],
        "element": "ice",
        "value": 300,
        "rarity": "rare",
        "description": "적을 얼리는 냉기 지팡이.",
    },
    "lightning_staff": {
        "name": "번개 지팡이",
        "char": "/",
        "color": (255, 255, 100),
        "weapon_type": "magic",
        "damage": 10,
        "range": 8,
        "accuracy": 15,
        "speed": 2,
        "durability": 0,
        "mana_cost": 15,
        "effects": ["magic_damage", "chain"],  # 연쇄 번개
        "element": "lightning",
        "value": 500,
        "rarity": "epic",
        "description": "번개를 내리치는 강력한 지팡이.",
    },

    # --- 완드류 (작은 지팡이) ---
    "wand_of_magic_missile": {
        "name": "마법 화살 완드",
        "char": "-",
        "color": (200, 150, 255),
        "weapon_type": "magic",
        "damage": 5,
        "range": 7,
        "accuracy": 20,  # 자동 조준
        "speed": 1,
        "durability": 30,  # 충전 횟수
        "mana_cost": 3,
        "effects": ["magic_damage", "auto_hit"],
        "element": "arcane",
        "value": 150,
        "rarity": "uncommon",
        "description": "마법 화살을 발사하는 완드.",
    },
    "wand_of_fireball": {
        "name": "화염구 완드",
        "char": "-",
        "color": (255, 50, 0),
        "weapon_type": "magic",
        "damage": 12,
        "range": 6,
        "accuracy": 0,
        "speed": 3,
        "durability": 10,
        "mana_cost": 20,
        "effects": ["magic_damage", "aoe", "burn"],  # 범위 공격
        "element": "fire",
        "value": 400,
        "rarity": "rare",
        "description": "화염구를 발사하는 완드.",
    },

    # --- 마법 검류 ---
    "enchanted_sword": {
        "name": "마법 검",
        "char": ")",
        "color": (150, 150, 255),
        "weapon_type": "magic",
        "damage": 8,
        "range": 1,
        "accuracy": 10,
        "speed": 2,
        "durability": 0,
        "mana_cost": 3,  # 근접이지만 마나 소모
        "effects": ["magic_damage"],
        "element": "arcane",
        "value": 250,
        "rarity": "rare",
        "description": "마력이 깃든 검.",
    },
    "holy_sword": {
        "name": "신성한 검",
        "char": ")",
        "color": (255, 255, 200),
        "weapon_type": "magic",
        "damage": 12,
        "range": 1,
        "accuracy": 10,
        "speed": 3,
        "durability": 0,
        "mana_cost": 5,
        "effects": ["magic_damage", "undead_bane", "demon_bane", "holy"],
        "element": "holy",
        "value": 800,
        "rarity": "legendary",
        "description": "신의 축복이 깃든 전설의 검.",
    },
}

# =============================================================================
# 탄약 (Ammunition)
# =============================================================================
AMMUNITION = {
    "arrow": {
        "name": "화살",
        "char": "|",
        "color": (139, 90, 43),
        "damage_bonus": 0,
        "effects": [],
        "value": 1,
        "stack_size": 20,
    },
    "fire_arrow": {
        "name": "화염 화살",
        "char": "|",
        "color": (255, 100, 0),
        "damage_bonus": 2,
        "effects": ["burn"],
        "value": 5,
        "stack_size": 10,
    },
    "poison_arrow": {
        "name": "독화살",
        "char": "|",
        "color": (0, 200, 0),
        "damage_bonus": 1,
        "effects": ["poison"],
        "value": 5,
        "stack_size": 10,
    },
    "bolt": {
        "name": "석궁 볼트",
        "char": "|",
        "color": (100, 100, 100),
        "damage_bonus": 2,
        "effects": [],
        "value": 2,
        "stack_size": 20,
    },
}

# =============================================================================
# 모든 무기 통합 (편의용)
# =============================================================================
ALL_WEAPONS = {
    **MELEE_WEAPONS,
    **RANGED_WEAPONS,
    **MAGIC_WEAPONS,
}

# =============================================================================
# 효과 설명
# =============================================================================
EFFECT_DESCRIPTIONS = {
    "undead_bane": "언데드에게 2배 데미지",
    "demon_bane": "악마에게 2배 데미지",
    "armor_pierce": "방어력 50% 무시",
    "stun": "20% 확률로 기절",
    "reach": "2칸 거리에서 공격 가능",
    "consumable": "사용 후 소멸",
    "magic_damage": "마법 데미지 (방어력 무시)",
    "burn": "화상 (3턴간 추가 데미지)",
    "freeze": "30% 확률로 동결 (1턴 행동불가)",
    "poison": "독 (5턴간 추가 데미지)",
    "chain": "주변 적에게 연쇄 데미지",
    "aoe": "범위 공격 (3x3)",
    "auto_hit": "자동 명중",
    "holy": "신성 속성 (언데드/악마에게 효과적)",
}

# =============================================================================
# 헬퍼 함수
# =============================================================================

def get_weapon(weapon_id: str) -> dict:
    """무기 ID로 무기 데이터 가져오기"""
    return ALL_WEAPONS.get(weapon_id, None)


def get_weapons_by_type(weapon_type: str) -> dict:
    """무기 타입으로 무기 목록 가져오기"""
    if weapon_type == "melee":
        return MELEE_WEAPONS
    elif weapon_type == "ranged":
        return RANGED_WEAPONS
    elif weapon_type == "magic":
        return MAGIC_WEAPONS
    return {}


def get_weapons_by_rarity(rarity: str) -> list:
    """희귀도로 무기 목록 가져오기"""
    return [
        (wid, wdata) for wid, wdata in ALL_WEAPONS.items()
        if wdata.get("rarity") == rarity
    ]


def get_ammo(ammo_id: str) -> dict:
    """탄약 ID로 탄약 데이터 가져오기"""
    return AMMUNITION.get(ammo_id, None)
