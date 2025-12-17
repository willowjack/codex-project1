/**
 * 무기 데이터 정의
 * 이 파일을 수정하여 무기를 추가/수정/삭제할 수 있습니다.
 *
 * 무기 속성:
 * - name: 무기 이름
 * - char: ASCII 문자
 * - color: CSS 색상 클래스
 * - weaponType: "melee" | "ranged" | "magic"
 * - damage: 기본 데미지
 * - range: 사거리
 * - accuracy: 명중률 보너스
 * - speed: 공격 속도
 * - manaCost: 마나 소모
 * - effects: 특수 효과 배열
 * - value: 가격
 * - rarity: 희귀도
 */

// =============================================================================
// 근접 무기
// =============================================================================
const MELEE_WEAPONS = {
    dagger: {
        name: "단검",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 3,
        range: 1,
        accuracy: 10,
        speed: 1,
        manaCost: 0,
        effects: [],
        value: 30,
        rarity: "common",
        description: "가볍고 빠른 단검."
    },
    silver_dagger: {
        name: "은 단검",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 4,
        range: 1,
        accuracy: 10,
        speed: 1,
        manaCost: 0,
        effects: ["undead_bane"],
        value: 80,
        rarity: "uncommon",
        description: "언데드에게 효과적인 은 단검."
    },
    short_sword: {
        name: "숏소드",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 5,
        range: 1,
        accuracy: 5,
        speed: 2,
        manaCost: 0,
        effects: [],
        value: 60,
        rarity: "common",
        description: "균형 잡힌 짧은 검."
    },
    long_sword: {
        name: "롱소드",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 7,
        range: 1,
        accuracy: 0,
        speed: 3,
        manaCost: 0,
        effects: [],
        value: 100,
        rarity: "uncommon",
        description: "표준적인 긴 검."
    },
    steel_sword: {
        name: "강철 검",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 10,
        range: 1,
        accuracy: 5,
        speed: 3,
        manaCost: 0,
        effects: [],
        value: 200,
        rarity: "rare",
        description: "단단한 강철로 만든 검."
    },
    battle_axe: {
        name: "전투 도끼",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 12,
        range: 1,
        accuracy: -10,
        speed: 4,
        manaCost: 0,
        effects: ["armor_pierce"],
        value: 150,
        rarity: "uncommon",
        description: "무거운 양손 전투 도끼."
    },
    mace: {
        name: "철퇴",
        char: ")",
        color: "tile-item",
        weaponType: "melee",
        damage: 8,
        range: 1,
        accuracy: -5,
        speed: 3,
        manaCost: 0,
        effects: ["stun"],
        value: 80,
        rarity: "uncommon",
        description: "적을 기절시킬 수 있는 철퇴."
    },
    spear: {
        name: "창",
        char: "/",
        color: "tile-item",
        weaponType: "melee",
        damage: 6,
        range: 2,
        accuracy: 5,
        speed: 3,
        manaCost: 0,
        effects: ["reach"],
        value: 70,
        rarity: "common",
        description: "긴 사거리의 창."
    }
};

// =============================================================================
// 원거리 무기
// =============================================================================
const RANGED_WEAPONS = {
    short_bow: {
        name: "단궁",
        char: "}",
        color: "tile-item",
        weaponType: "ranged",
        damage: 4,
        range: 6,
        accuracy: 5,
        speed: 2,
        manaCost: 0,
        effects: [],
        ammoType: "arrow",
        value: 50,
        rarity: "common",
        description: "가벼운 단궁."
    },
    long_bow: {
        name: "장궁",
        char: "}",
        color: "tile-item",
        weaponType: "ranged",
        damage: 7,
        range: 10,
        accuracy: 0,
        speed: 3,
        manaCost: 0,
        effects: [],
        ammoType: "arrow",
        value: 100,
        rarity: "uncommon",
        description: "사거리가 긴 장궁."
    },
    crossbow: {
        name: "석궁",
        char: "}",
        color: "tile-item",
        weaponType: "ranged",
        damage: 10,
        range: 7,
        accuracy: 15,
        speed: 5,
        manaCost: 0,
        effects: ["armor_pierce"],
        ammoType: "bolt",
        value: 150,
        rarity: "uncommon",
        description: "강력하지만 느린 석궁."
    },
    throwing_knife: {
        name: "투척용 단검",
        char: ")",
        color: "tile-item",
        weaponType: "ranged",
        damage: 3,
        range: 4,
        accuracy: 10,
        speed: 1,
        manaCost: 0,
        effects: ["consumable"],
        ammoType: "none",
        value: 5,
        rarity: "common",
        description: "던져서 사용하는 단검."
    }
};

// =============================================================================
// 마법 무기
// =============================================================================
const MAGIC_WEAPONS = {
    apprentice_staff: {
        name: "견습 지팡이",
        char: "/",
        color: "tile-potion",
        weaponType: "magic",
        damage: 3,
        range: 5,
        accuracy: 10,
        speed: 2,
        manaCost: 5,
        effects: ["magic_damage"],
        element: "arcane",
        value: 100,
        rarity: "common",
        description: "초보 마법사의 지팡이."
    },
    fire_staff: {
        name: "화염 지팡이",
        char: "/",
        color: "tile-monster",
        weaponType: "magic",
        damage: 8,
        range: 6,
        accuracy: 5,
        speed: 3,
        manaCost: 10,
        effects: ["magic_damage", "burn"],
        element: "fire",
        value: 300,
        rarity: "rare",
        description: "적을 불태우는 화염 지팡이."
    },
    ice_staff: {
        name: "냉기 지팡이",
        char: "/",
        color: "tile-water",
        weaponType: "magic",
        damage: 6,
        range: 6,
        accuracy: 10,
        speed: 3,
        manaCost: 10,
        effects: ["magic_damage", "freeze"],
        element: "ice",
        value: 300,
        rarity: "rare",
        description: "적을 얼리는 냉기 지팡이."
    },
    lightning_staff: {
        name: "번개 지팡이",
        char: "/",
        color: "tile-npc",
        weaponType: "magic",
        damage: 10,
        range: 8,
        accuracy: 15,
        speed: 2,
        manaCost: 15,
        effects: ["magic_damage", "chain"],
        element: "lightning",
        value: 500,
        rarity: "epic",
        description: "번개를 내리치는 강력한 지팡이."
    },
    enchanted_sword: {
        name: "마법 검",
        char: ")",
        color: "tile-potion",
        weaponType: "magic",
        damage: 8,
        range: 1,
        accuracy: 10,
        speed: 2,
        manaCost: 3,
        effects: ["magic_damage"],
        element: "arcane",
        value: 250,
        rarity: "rare",
        description: "마력이 깃든 검."
    },
    holy_sword: {
        name: "신성한 검",
        char: ")",
        color: "tile-npc",
        weaponType: "magic",
        damage: 12,
        range: 1,
        accuracy: 10,
        speed: 3,
        manaCost: 5,
        effects: ["magic_damage", "undead_bane", "holy"],
        element: "holy",
        value: 800,
        rarity: "legendary",
        description: "신의 축복이 깃든 전설의 검."
    }
};

// =============================================================================
// 모든 무기 통합
// =============================================================================
const ALL_WEAPONS = {
    ...MELEE_WEAPONS,
    ...RANGED_WEAPONS,
    ...MAGIC_WEAPONS
};

// =============================================================================
// 효과 설명
// =============================================================================
const EFFECT_DESCRIPTIONS = {
    undead_bane: "언데드에게 2배 데미지",
    armor_pierce: "방어력 50% 무시",
    stun: "20% 확률로 기절",
    reach: "2칸 거리에서 공격 가능",
    consumable: "사용 후 소멸",
    magic_damage: "마법 데미지 (방어력 무시)",
    burn: "화상 (3턴간 추가 데미지)",
    freeze: "30% 확률로 동결",
    chain: "주변 적에게 연쇄 데미지",
    holy: "신성 속성"
};

// =============================================================================
// 무기 생성 함수
// =============================================================================
function createWeapon(weaponId) {
    const data = ALL_WEAPONS[weaponId];
    if (!data) return null;

    return {
        id: weaponId,
        ...data,
        durability: 100,
        maxDurability: 100
    };
}

function createRandomWeapon(weaponType = null, rarity = null) {
    let candidates = Object.entries(ALL_WEAPONS);

    if (weaponType) {
        candidates = candidates.filter(([id, w]) => w.weaponType === weaponType);
    }
    if (rarity) {
        candidates = candidates.filter(([id, w]) => w.rarity === rarity);
    }

    if (candidates.length === 0) return null;

    const [weaponId, data] = candidates[Math.floor(Math.random() * candidates.length)];
    return createWeapon(weaponId);
}

// 희귀도별 색상
const RARITY_COLORS = {
    common: '#ffffff',
    uncommon: '#00ff00',
    rare: '#0080ff',
    epic: '#a020f0',
    legendary: '#ffa500'
};
