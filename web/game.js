/**
 * ASCII Roguelike Survival - JavaScript Version
 * Nethack + Unreal World Style
 */

// ============================================================================
// 게임 설정
// ============================================================================
const CONFIG = {
    MAP_WIDTH: 60,
    MAP_HEIGHT: 30,
    FOV_RADIUS: 10,
    MAX_ROOMS: 20,
    ROOM_MIN_SIZE: 4,
    ROOM_MAX_SIZE: 10,
    MAX_MONSTERS_PER_ROOM: 3,
    MAX_ITEMS_PER_ROOM: 2,
    MAX_DUNGEON_LEVEL: 20,
};

// ============================================================================
// 몬스터 데이터 (층별 출현 및 난이도)
// ============================================================================
const MONSTER_DATA = {
    // ========== 약한 몬스터 (1-5층) ==========
    'r': {
        name: '쥐', char: 'r',
        minFloor: 1, maxFloor: 5, spawnWeight: 100,
        stats: { maxHp: 5, defense: 0, power: 2, detectionRange: 5 }
    },
    'b': {
        name: '박쥐', char: 'b',
        minFloor: 1, maxFloor: 6, spawnWeight: 80,
        stats: { maxHp: 4, defense: 0, power: 1, detectionRange: 8 }
    },
    'x': {
        name: '거미', char: 'x',
        minFloor: 1, maxFloor: 7, spawnWeight: 60,
        stats: { maxHp: 6, defense: 0, power: 3, detectionRange: 6 }
    },
    'a': {
        name: '거대 개미', char: 'a',
        minFloor: 2, maxFloor: 8, spawnWeight: 50,
        stats: { maxHp: 8, defense: 1, power: 2, detectionRange: 5 }
    },

    // ========== 일반 몬스터 (3-10층) ==========
    'g': {
        name: '고블린', char: 'g',
        minFloor: 2, maxFloor: 10, spawnWeight: 80,
        stats: { maxHp: 10, defense: 0, power: 3, detectionRange: 6 }
    },
    'S': {
        name: '뱀', char: 'S',
        minFloor: 3, maxFloor: 12, spawnWeight: 50,
        stats: { maxHp: 8, defense: 0, power: 4, detectionRange: 5 }
    },
    'j': {
        name: '슬라임', char: 'j',
        minFloor: 3, maxFloor: 15, spawnWeight: 40,
        stats: { maxHp: 15, defense: 2, power: 2, detectionRange: 4 }
    },
    's': {
        name: '해골', char: 's',
        minFloor: 4, maxFloor: 12, spawnWeight: 45,
        stats: { maxHp: 12, defense: 1, power: 4, detectionRange: 6 }
    },

    // ========== 중급 몬스터 (5-15층) ==========
    'o': {
        name: '오크', char: 'o',
        minFloor: 4, maxFloor: 14, spawnWeight: 60,
        stats: { maxHp: 16, defense: 1, power: 4, detectionRange: 8 }
    },
    'w': {
        name: '늑대', char: 'w',
        minFloor: 5, maxFloor: 15, spawnWeight: 50,
        stats: { maxHp: 14, defense: 0, power: 5, detectionRange: 10 }
    },
    'Z': {
        name: '좀비', char: 'Z',
        minFloor: 5, maxFloor: 16, spawnWeight: 40,
        stats: { maxHp: 20, defense: 2, power: 4, detectionRange: 5 }
    },
    'h': {
        name: '유령', char: 'h',
        minFloor: 6, maxFloor: 18, spawnWeight: 30,
        stats: { maxHp: 10, defense: 3, power: 5, detectionRange: 8 }
    },
    'u': {
        name: '구울', char: 'u',
        minFloor: 6, maxFloor: 16, spawnWeight: 35,
        stats: { maxHp: 18, defense: 1, power: 6, detectionRange: 7 }
    },

    // ========== 강한 몬스터 (8-18층) ==========
    'T': {
        name: '트롤', char: 'T',
        minFloor: 8, maxFloor: 18, spawnWeight: 30,
        stats: { maxHp: 30, defense: 2, power: 6, detectionRange: 6 }
    },
    'B': {
        name: '곰', char: 'B',
        minFloor: 7, maxFloor: 16, spawnWeight: 25,
        stats: { maxHp: 35, defense: 3, power: 7, detectionRange: 7 }
    },
    'Y': {
        name: '미라', char: 'Y',
        minFloor: 9, maxFloor: 18, spawnWeight: 25,
        stats: { maxHp: 25, defense: 3, power: 6, detectionRange: 6 }
    },
    'J': {
        name: '젤리', char: 'J',
        minFloor: 8, maxFloor: 20, spawnWeight: 20,
        stats: { maxHp: 40, defense: 4, power: 5, detectionRange: 4 }
    },
    'K': {
        name: '다크 나이트', char: 'K',
        minFloor: 10, maxFloor: 18, spawnWeight: 20,
        stats: { maxHp: 35, defense: 4, power: 8, detectionRange: 8 }
    },

    // ========== 엘리트 몬스터 (12-20층) ==========
    'R': {
        name: '레이스', char: 'R',
        minFloor: 12, maxFloor: 20, spawnWeight: 15,
        stats: { maxHp: 30, defense: 5, power: 8, detectionRange: 10 }
    },
    'V': {
        name: '뱀파이어', char: 'V',
        minFloor: 12, maxFloor: 20, spawnWeight: 15,
        stats: { maxHp: 40, defense: 3, power: 10, detectionRange: 10 }
    },
    'M': {
        name: '어둠 마법사', char: 'M',
        minFloor: 14, maxFloor: 20, spawnWeight: 10,
        stats: { maxHp: 25, defense: 2, power: 12, detectionRange: 12 }
    },
    'I': {
        name: '비홀더', char: 'I',
        minFloor: 14, maxFloor: 20, spawnWeight: 8,
        stats: { maxHp: 45, defense: 4, power: 10, detectionRange: 10 }
    },
    'c': {
        name: '젤라틴 큐브', char: 'c',
        minFloor: 10, maxFloor: 20, spawnWeight: 12,
        stats: { maxHp: 50, defense: 5, power: 6, detectionRange: 3 }
    },

    // ========== 보스급 몬스터 (15-20층) ==========
    'L': {
        name: '리치', char: 'L',
        minFloor: 16, maxFloor: 20, spawnWeight: 5,
        stats: { maxHp: 50, defense: 5, power: 15, detectionRange: 12 }
    },
    'D': {
        name: '드래곤', char: 'D',
        minFloor: 18, maxFloor: 20, spawnWeight: 3,
        stats: { maxHp: 100, defense: 8, power: 20, detectionRange: 15 }
    },

    // ========== 특수 몬스터 ==========
    '?': {
        name: '미믹', char: '?',
        minFloor: 5, maxFloor: 20, spawnWeight: 5,
        stats: { maxHp: 20, defense: 2, power: 8, detectionRange: 0 }
    },
    'e': {
        name: '불 정령', char: 'e',
        minFloor: 10, maxFloor: 20, spawnWeight: 10,
        stats: { maxHp: 20, defense: 2, power: 10, detectionRange: 8 }
    },
    'E': {
        name: '물 정령', char: 'E',
        minFloor: 10, maxFloor: 20, spawnWeight: 10,
        stats: { maxHp: 25, defense: 3, power: 8, detectionRange: 8 }
    },
};

// ============================================================================
// 타일 타입
// ============================================================================
const TILES = {
    FLOOR: { char: '.', walkable: true, transparent: true, color: 'tile-floor' },
    WALL: { char: '#', walkable: false, transparent: false, color: 'tile-wall' },
    WATER: { char: '~', walkable: true, transparent: true, color: 'tile-water' },
    TREE: { char: 'T', walkable: false, transparent: false, color: 'tile-tree' },
    GRASS: { char: '"', walkable: true, transparent: true, color: 'tile-grass' },
    STAIRS_DOWN: { char: '>', walkable: true, transparent: true, color: 'tile-stairs' },
    STAIRS_UP: { char: '<', walkable: true, transparent: true, color: 'tile-stairs' },
};

// ============================================================================
// 엔티티 클래스들
// ============================================================================

class Entity {
    constructor(x, y, char, color, name, blocksMovement = false) {
        this.x = x;
        this.y = y;
        this.char = char;
        this.color = color;
        this.name = name;
        this.blocksMovement = blocksMovement;
    }

    move(dx, dy) {
        this.x += dx;
        this.y += dy;
    }

    distanceTo(other) {
        return Math.sqrt((other.x - this.x) ** 2 + (other.y - this.y) ** 2);
    }
}

class Actor extends Entity {
    constructor(x, y, char, color, name, options = {}) {
        super(x, y, char, color, name, true);

        // Fighter 컴포넌트
        this.maxHp = options.maxHp || 30;
        this.hp = options.hp || this.maxHp;
        this.defense = options.defense || 0;
        this.power = options.power || 5;

        // Survival 컴포넌트
        this.maxHunger = options.maxHunger || 1000;
        this.hunger = options.hunger || this.maxHunger;
        this.maxThirst = options.maxThirst || 1000;
        this.thirst = options.thirst || this.maxThirst;
        this.bodyTemp = 37.0;

        // 경제
        this.gold = options.gold || 0;

        // 인벤토리
        this.inventory = [];
        this.inventoryCapacity = 26;

        // AI (몬스터용)
        this.ai = options.ai || null;
        this.isHostile = options.isHostile || false;
        this.detectionRange = options.detectionRange || 8;

        // NPC
        this.isNPC = options.isNPC || false;
        this.npcRole = options.npcRole || null;
        this.dialogues = options.dialogues || null;
        this.shopInventory = options.shopInventory || [];

        // 퀘스트
        this.questLog = null;

        // 종교
        this.religion = null;

        // 통계
        this.kills = 0;
    }

    get isAlive() {
        return this.hp > 0;
    }

    takeDamage(amount) {
        const actual = Math.max(0, amount - this.defense);
        this.hp = Math.max(0, this.hp - actual);
        return actual;
    }

    heal(amount) {
        const old = this.hp;
        this.hp = Math.min(this.maxHp, this.hp + amount);
        return this.hp - old;
    }

    get hungerPercent() {
        return (this.hunger / this.maxHunger) * 100;
    }

    get thirstPercent() {
        return (this.thirst / this.maxThirst) * 100;
    }
}

class Item extends Entity {
    constructor(x, y, char, color, name, options = {}) {
        super(x, y, char, color, name, false);
        this.consumable = options.consumable || false;
        this.nutrition = options.nutrition || 0;
        this.hydration = options.hydration || 0;
        this.healAmount = options.healAmount || 0;
        this.value = options.value || 10;
        this.itemType = options.itemType || 'misc';
    }
}

// ============================================================================
// 퀘스트 시스템
// ============================================================================

class Quest {
    constructor(id, name, description, objectives, rewards) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.objectives = objectives; // [{type, target, required, current}]
        this.rewards = rewards; // {gold, xp}
        this.status = 'active'; // active, completed, failed
    }

    updateProgress(type, target, amount = 1) {
        let updated = false;
        for (const obj of this.objectives) {
            if (obj.type === type && obj.target === target && obj.current < obj.required) {
                obj.current = Math.min(obj.current + amount, obj.required);
                updated = true;
            }
        }
        if (updated && this.isComplete) {
            this.status = 'completed';
        }
        return updated;
    }

    get isComplete() {
        return this.objectives.every(obj => obj.current >= obj.required);
    }
}

class QuestLog {
    constructor() {
        this.active = [];
        this.completed = [];
    }

    addQuest(quest) {
        this.active.push(quest);
    }

    updateKillQuest(monsterName) {
        const messages = [];
        for (const quest of this.active) {
            if (quest.updateProgress('kill', monsterName)) {
                const obj = quest.objectives.find(o => o.type === 'kill' && o.target === monsterName);
                if (obj) {
                    messages.push(`[퀘스트] ${quest.name}: ${obj.target} 처치 (${obj.current}/${obj.required})`);
                }
                if (quest.isComplete) {
                    messages.push(`[퀘스트] '${quest.name}' 완료!`);
                }
            }
        }
        return messages;
    }
}

// ============================================================================
// 종교 시스템
// ============================================================================

const DEITIES = {
    solarius: {
        id: 'solarius',
        name: '솔라리우스',
        title: '빛의 신',
        domain: 'light',
        description: '치유와 정의의 신',
    },
    grommash: {
        id: 'grommash',
        name: '그롬마쉬',
        title: '전쟁의 신',
        domain: 'war',
        description: '힘과 전투의 신',
    },
    sylvana: {
        id: 'sylvana',
        name: '실바나',
        title: '자연의 여신',
        domain: 'nature',
        description: '숲과 생명의 여신',
    },
    mortis: {
        id: 'mortis',
        name: '모르티스',
        title: '죽음의 신',
        domain: 'death',
        description: '죽음과 영혼의 신',
    },
};

class Religion {
    constructor() {
        this.deity = null;
        this.faithPoints = 0;
        this.favor = 0; // -100 ~ 100
        this.prayerTimeout = 0;
    }

    get favorLevel() {
        if (this.favor <= -50) return '분노';
        if (this.favor < 0) return '불쾌';
        if (this.favor < 25) return '중립';
        if (this.favor < 50) return '기쁨';
        if (this.favor < 80) return '축복';
        return '찬양';
    }

    convert(deity) {
        this.deity = deity;
        this.favor = 10;
        this.faithPoints = 0;
        return `${deity.name}에게 귀의했다.`;
    }

    pray() {
        if (!this.deity) return { success: false, message: '섬기는 신이 없다.' };
        if (this.prayerTimeout > 0) return { success: false, message: `아직 기도할 수 없다. (${this.prayerTimeout}턴)` };

        this.prayerTimeout = 300;

        if (this.favor < 0) {
            return { success: false, message: `${this.deity.name}은(는) 응답하지 않는다.` };
        }

        const roll = Math.random();
        if (roll < 0.3 + (this.favor / 200)) {
            return { success: true, message: `${this.deity.name}이(가) 은총을 내린다!`, blessing: true };
        }
        return { success: false, message: `${this.deity.name}은(는) 침묵한다.` };
    }

    processTurn() {
        if (this.prayerTimeout > 0) this.prayerTimeout--;
    }
}

// ============================================================================
// 상점 시스템
// ============================================================================

const ITEM_PRICES = {
    '마른 고기': 10,
    '빵': 5,
    '물병': 5,
    '치료 물약': 50,
    '단검': 30,
    '숏소드': 60,
    '가죽 갑옷': 50,
};

class Shop {
    constructor(name, items, buyMultiplier = 1.0, sellMultiplier = 0.5) {
        this.name = name;
        this.items = items; // [{item, quantity}]
        this.buyMultiplier = buyMultiplier;
        this.sellMultiplier = sellMultiplier;
        this.gold = 500;
    }

    getBuyPrice(itemName) {
        return Math.floor((ITEM_PRICES[itemName] || 10) * this.buyMultiplier);
    }

    getSellPrice(itemName) {
        return Math.floor((ITEM_PRICES[itemName] || 10) * this.sellMultiplier);
    }
}

// ============================================================================
// 맵 생성
// ============================================================================

class GameMap {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.tiles = [];
        this.visible = [];
        this.explored = [];
        this.entities = [];
        this.items = [];

        // 초기화
        for (let x = 0; x < width; x++) {
            this.tiles[x] = [];
            this.visible[x] = [];
            this.explored[x] = [];
            for (let y = 0; y < height; y++) {
                this.tiles[x][y] = { ...TILES.WALL };
                this.visible[x][y] = false;
                this.explored[x][y] = false;
            }
        }
    }

    inBounds(x, y) {
        return x >= 0 && x < this.width && y >= 0 && y < this.height;
    }

    isWalkable(x, y) {
        if (!this.inBounds(x, y)) return false;
        if (!this.tiles[x][y].walkable) return false;
        return !this.getBlockingEntityAt(x, y);
    }

    getBlockingEntityAt(x, y) {
        return this.entities.find(e => e.blocksMovement && e.x === x && e.y === y);
    }

    getActorAt(x, y) {
        return this.entities.find(e => e instanceof Actor && e.x === x && e.y === y);
    }

    getItemsAt(x, y) {
        return this.items.filter(i => i.x === x && i.y === y);
    }

    addEntity(entity) {
        this.entities.push(entity);
    }

    removeEntity(entity) {
        const idx = this.entities.indexOf(entity);
        if (idx >= 0) this.entities.splice(idx, 1);
    }

    addItem(item) {
        this.items.push(item);
    }

    removeItem(item) {
        const idx = this.items.indexOf(item);
        if (idx >= 0) this.items.splice(idx, 1);
    }

    computeFOV(centerX, centerY, radius) {
        // Reset visibility
        for (let x = 0; x < this.width; x++) {
            for (let y = 0; y < this.height; y++) {
                this.visible[x][y] = false;
            }
        }

        // 플레이어 위치는 항상 visible
        if (this.inBounds(centerX, centerY)) {
            this.visible[centerX][centerY] = true;
            this.explored[centerX][centerY] = true;
        }

        // Simple raycasting FOV
        for (let angle = 0; angle < 360; angle += 1) {
            const rad = angle * Math.PI / 180;
            const dx = Math.cos(rad);
            const dy = Math.sin(rad);

            let x = centerX + 0.5;
            let y = centerY + 0.5;

            for (let i = 0; i < radius; i++) {
                x += dx;
                y += dy;

                const tileX = Math.floor(x);
                const tileY = Math.floor(y);

                if (!this.inBounds(tileX, tileY)) break;

                this.visible[tileX][tileY] = true;
                this.explored[tileX][tileY] = true;

                if (!this.tiles[tileX][tileY].transparent) break;
            }
        }
    }
}

// 던전 생성
function generateDungeon(width, height, maxRooms, roomMinSize, roomMaxSize, dungeonLevel = 1) {
    const map = new GameMap(width, height);
    const rooms = [];

    for (let i = 0; i < maxRooms; i++) {
        const w = randomInt(roomMinSize, roomMaxSize);
        const h = randomInt(roomMinSize, roomMaxSize);
        const x = randomInt(1, width - w - 1);
        const y = randomInt(1, height - h - 1);

        const room = { x1: x, y1: y, x2: x + w, y2: y + h };

        // 겹치는지 확인
        let overlaps = false;
        for (const other of rooms) {
            if (roomsIntersect(room, other)) {
                overlaps = true;
                break;
            }
        }

        if (overlaps) continue;

        // 방 파기
        for (let rx = room.x1; rx < room.x2; rx++) {
            for (let ry = room.y1; ry < room.y2; ry++) {
                map.tiles[rx][ry] = { ...TILES.FLOOR };
            }
        }

        if (rooms.length > 0) {
            // 이전 방과 연결
            const prev = rooms[rooms.length - 1];
            const [cx1, cy1] = roomCenter(prev);
            const [cx2, cy2] = roomCenter(room);

            if (Math.random() < 0.5) {
                createHTunnel(map, cx1, cx2, cy1);
                createVTunnel(map, cy1, cy2, cx2);
            } else {
                createVTunnel(map, cy1, cy2, cx1);
                createHTunnel(map, cx1, cx2, cy2);
            }
        }

        rooms.push(room);
    }

    // 첫 번째 방에 상승 계단 (1층 제외)
    if (rooms.length > 0 && dungeonLevel > 1) {
        const [ux, uy] = roomCenter(rooms[0]);
        map.tiles[ux][uy] = { ...TILES.STAIRS_UP };
    }

    // 마지막 방에 하강 계단 (최하층 제외)
    if (rooms.length > 0 && dungeonLevel < CONFIG.MAX_DUNGEON_LEVEL) {
        const [sx, sy] = roomCenter(rooms[rooms.length - 1]);
        map.tiles[sx][sy] = { ...TILES.STAIRS_DOWN };
    }

    return { map, rooms };
}

function roomsIntersect(a, b) {
    return a.x1 <= b.x2 && a.x2 >= b.x1 && a.y1 <= b.y2 && a.y2 >= b.y1;
}

function roomCenter(room) {
    return [Math.floor((room.x1 + room.x2) / 2), Math.floor((room.y1 + room.y2) / 2)];
}

function createHTunnel(map, x1, x2, y) {
    for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) {
        map.tiles[x][y] = { ...TILES.FLOOR };
    }
}

function createVTunnel(map, y1, y2, x) {
    for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) {
        map.tiles[x][y] = { ...TILES.FLOOR };
    }
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ============================================================================
// 메인 게임 클래스
// ============================================================================

class Game {
    constructor() {
        this.player = null;
        this.gameMap = null;
        this.turnCount = 0;
        this.hour = 8;
        this.day = 1;
        this.dungeonLevel = 1; // 현재 던전 층
        this.gameState = 'title'; // title, playing, dead
        this.currentModal = null;

        this.messageLog = [];

        // 3D 렌더러
        this.renderer3D = new ASCII3DRenderer(50, 18);
        this.compass = new Compass();
        this.playerDirection = { dx: 0, dy: -1 }; // 초기 방향: 북쪽
        this.viewMode = 'both'; // 'both', '3d-only', '2d-only'

        this.setupEventListeners();
    }

    // ========================================================================
    // 초기화
    // ========================================================================

    newGame() {
        // 플레이어 생성
        this.player = new Actor(0, 0, '@', 'tile-player', '당신', {
            maxHp: 30,
            defense: 2,
            power: 5,
            gold: 100,
        });
        this.player.questLog = new QuestLog();
        this.player.religion = new Religion();

        // 시작 퀘스트 추가
        this.player.questLog.addQuest(new Quest(
            'rat_hunt', '쥐 사냥',
            '마을 창고의 쥐를 처치하라.',
            [{ type: 'kill', target: '쥐', required: 5, current: 0 }],
            { gold: 50 }
        ));

        // 던전 생성
        const { map, rooms } = generateDungeon(
            CONFIG.MAP_WIDTH,
            CONFIG.MAP_HEIGHT,
            CONFIG.MAX_ROOMS,
            CONFIG.ROOM_MIN_SIZE,
            CONFIG.ROOM_MAX_SIZE,
            this.dungeonLevel
        );
        this.gameMap = map;

        // 플레이어 배치
        if (rooms.length > 0) {
            const [px, py] = roomCenter(rooms[0]);
            this.player.x = px;
            this.player.y = py;
        }
        this.gameMap.addEntity(this.player);

        // 몬스터/아이템 배치
        for (let i = 1; i < rooms.length; i++) {
            this.placeEntities(rooms[i]);
        }

        // NPC 배치 (두 번째 방에)
        if (rooms.length > 1) {
            const [nx, ny] = roomCenter(rooms[1]);
            const merchant = new Actor(nx, ny, '@', 'tile-npc', '상인 마르코', {
                isNPC: true,
                npcRole: 'merchant',
                gold: 500,
            });
            merchant.isHostile = false;
            merchant.blocksMovement = true;
            this.gameMap.addEntity(merchant);
        }

        // 게임 상태 초기화
        this.turnCount = 0;
        this.hour = 8;
        this.day = 1;
        this.dungeonLevel = 1;
        this.gameState = 'playing';
        this.messageLog = [];

        this.addMessage(`던전 ${this.dungeonLevel}층에 입장했다. 살아남아야 한다!`, 'system');
        this.addMessage('[?]를 눌러 도움말을 볼 수 있다.', 'system');
        this.addMessage('[>] 계단을 이용해 더 깊은 층으로 내려갈 수 있다.', 'system');

        this.updateFOV();
        this.showScreen('game-screen');
        this.render();
    }

    // 현재 층에서 출현 가능한 몬스터 목록 반환
    getSpawnableMonsters(floor) {
        const spawnable = [];
        for (const [char, data] of Object.entries(MONSTER_DATA)) {
            if (floor >= data.minFloor && floor <= data.maxFloor) {
                spawnable.push({ char, ...data });
            }
        }
        return spawnable;
    }

    // 가중치 기반 랜덤 몬스터 선택
    selectWeightedMonster(monsters) {
        const totalWeight = monsters.reduce((sum, m) => sum + m.spawnWeight, 0);
        let roll = Math.random() * totalWeight;

        for (const monster of monsters) {
            roll -= monster.spawnWeight;
            if (roll <= 0) return monster;
        }
        return monsters[monsters.length - 1];
    }

    placeEntities(room) {
        // 현재 층에서 출현 가능한 몬스터 목록
        const spawnableMonsters = this.getSpawnableMonsters(this.dungeonLevel);

        // 층이 깊어질수록 몬스터 수 증가
        const bonusMonsters = Math.floor(this.dungeonLevel / 5);
        const maxMonsters = Math.min(CONFIG.MAX_MONSTERS_PER_ROOM + bonusMonsters, 5);
        const numMonsters = randomInt(0, maxMonsters);

        for (let i = 0; i < numMonsters; i++) {
            const x = randomInt(room.x1 + 1, room.x2 - 1);
            const y = randomInt(room.y1 + 1, room.y2 - 1);

            if (this.gameMap.getBlockingEntityAt(x, y)) continue;

            // 가중치 기반 몬스터 선택
            const monsterData = this.selectWeightedMonster(spawnableMonsters);
            const stats = monsterData.stats;

            // 층 보너스: 깊은 층일수록 몬스터가 약간 강해짐
            const floorBonus = Math.floor((this.dungeonLevel - monsterData.minFloor) / 3);
            const monster = new Actor(x, y, monsterData.char, 'tile-monster', monsterData.name, {
                maxHp: stats.maxHp + floorBonus * 2,
                defense: stats.defense,
                power: stats.power + floorBonus,
                isHostile: true,
                detectionRange: stats.detectionRange
            });
            monster.ai = 'hostile';
            this.gameMap.addEntity(monster);
        }

        // 아이템 배치
        const numItems = randomInt(0, CONFIG.MAX_ITEMS_PER_ROOM);
        for (let i = 0; i < numItems; i++) {
            const x = randomInt(room.x1 + 1, room.x2 - 1);
            const y = randomInt(room.y1 + 1, room.y2 - 1);

            if (this.gameMap.getItemsAt(x, y).length > 0) continue;

            let item;
            const roll = Math.random();
            if (roll < 0.5) {
                item = new Item(x, y, '%', 'tile-food', '마른 고기', {
                    consumable: true, nutrition: 200, itemType: 'food', value: 10
                });
            } else if (roll < 0.8) {
                item = new Item(x, y, '!', 'tile-item', '물병', {
                    consumable: true, hydration: 300, itemType: 'drink', value: 5
                });
            } else {
                item = new Item(x, y, '!', 'tile-potion', '치료 물약', {
                    consumable: true, healAmount: 20, itemType: 'potion', value: 50
                });
            }
            this.gameMap.addItem(item);
        }
    }

    // ========================================================================
    // 층 이동
    // ========================================================================

    // 다음 층으로 내려가기
    goToNextFloor() {
        const tile = this.gameMap.tiles[this.player.x][this.player.y];
        if (tile.char !== '>') {
            this.addMessage('여기에는 내려가는 계단이 없다.', 'system');
            return;
        }

        if (this.dungeonLevel >= CONFIG.MAX_DUNGEON_LEVEL) {
            this.addMessage('더 이상 내려갈 수 없다. 이곳이 최하층이다.', 'system');
            return;
        }

        this.dungeonLevel++;
        this.generateNewFloor('down');
        this.addMessage(`던전 ${this.dungeonLevel}층으로 내려왔다.`, 'system');

        // 깊은 층 경고 메시지
        if (this.dungeonLevel === 5) {
            this.addMessage('공기가 더 차가워졌다. 더 강한 적들이 도사리고 있다.', 'system');
        } else if (this.dungeonLevel === 10) {
            this.addMessage('어둠이 짙어진다. 위험한 기운이 느껴진다...', 'system');
        } else if (this.dungeonLevel === 15) {
            this.addMessage('지옥의 문턱에 다가서고 있다. 각오해라.', 'system');
        } else if (this.dungeonLevel === 18) {
            this.addMessage('드래곤의 숨결이 느껴진다...', 'system');
        }

        this.endTurn();
    }

    // 이전 층으로 올라가기
    goToPrevFloor() {
        const tile = this.gameMap.tiles[this.player.x][this.player.y];
        if (tile.char !== '<') {
            this.addMessage('여기에는 올라가는 계단이 없다.', 'system');
            return;
        }

        if (this.dungeonLevel <= 1) {
            this.addMessage('던전 입구다. 밖으로 나갈 수 없다.', 'system');
            return;
        }

        this.dungeonLevel--;
        this.generateNewFloor('up');
        this.addMessage(`던전 ${this.dungeonLevel}층으로 올라왔다.`, 'system');
        this.endTurn();
    }

    // 새 층 생성
    generateNewFloor(direction) {
        // 새 던전 생성
        const { map, rooms } = generateDungeon(
            CONFIG.MAP_WIDTH,
            CONFIG.MAP_HEIGHT,
            CONFIG.MAX_ROOMS,
            CONFIG.ROOM_MIN_SIZE,
            CONFIG.ROOM_MAX_SIZE,
            this.dungeonLevel
        );

        // 기존 맵의 플레이어 제거
        this.gameMap.removeEntity(this.player);

        // 새 맵 설정
        this.gameMap = map;

        // 플레이어 위치 설정 (올라왔으면 하강계단, 내려왔으면 상승계단에 배치)
        if (direction === 'down' && rooms.length > 0) {
            // 상승 계단 위치 (첫 번째 방)에 배치
            const [px, py] = roomCenter(rooms[0]);
            this.player.x = px;
            this.player.y = py;
        } else if (direction === 'up' && rooms.length > 0) {
            // 하강 계단 위치 (마지막 방)에 배치
            const [px, py] = roomCenter(rooms[rooms.length - 1]);
            this.player.x = px;
            this.player.y = py;
        }

        this.gameMap.addEntity(this.player);

        // 몬스터/아이템 배치
        for (let i = 1; i < rooms.length; i++) {
            this.placeEntities(rooms[i]);
        }

        // FOV 업데이트
        this.updateFOV();
        this.render();
    }

    // ========================================================================
    // 게임 로직
    // ========================================================================

    handlePlayerTurn(dx, dy) {
        if (this.gameState !== 'playing') return;

        // 플레이어 방향 업데이트 (3D 뷰용)
        if (dx !== 0 || dy !== 0) {
            this.playerDirection = { dx, dy };
            this.renderer3D.setAngleFromMovement(dx, dy);
        }

        const newX = this.player.x + dx;
        const newY = this.player.y + dy;

        if (!this.gameMap.inBounds(newX, newY)) {
            this.addMessage('그쪽으로는 갈 수 없다.', 'system');
            return;
        }

        if (!this.gameMap.tiles[newX][newY].walkable) {
            this.addMessage('벽이 막고 있다.', 'system');
            return;
        }

        const target = this.gameMap.getActorAt(newX, newY);
        if (target && target !== this.player) {
            if (target.isNPC && !target.isHostile) {
                this.talkToNPC(target);
                return;
            } else {
                this.meleeAttack(this.player, target);
            }
        } else if (this.gameMap.isWalkable(newX, newY)) {
            this.player.move(dx, dy);

            const items = this.gameMap.getItemsAt(this.player.x, this.player.y);
            if (items.length > 0) {
                this.addMessage(`여기에 ${items.map(i => i.name).join(', ')}이(가) 있다.`, 'item');
            }
        }

        this.endTurn();
    }

    meleeAttack(attacker, target) {
        const damage = target.takeDamage(attacker.power);

        if (attacker === this.player) {
            this.addMessage(`${target.name}에게 ${damage} 데미지를 입혔다!`, 'combat');
        } else {
            this.addMessage(`${attacker.name}이(가) ${damage} 데미지를 입혔다!`, 'combat');
        }

        if (!target.isAlive) {
            this.killEntity(target, attacker);
        }
    }

    killEntity(entity, killer) {
        if (entity === this.player) {
            this.addMessage('당신은 죽었다...', 'combat');
            this.gameState = 'dead';
            this.showGameOver('전투에서 패배했다.');
            return;
        }

        this.addMessage(`${entity.name}을(를) 처치했다!`, 'combat');

        // 퀘스트 업데이트
        if (killer === this.player && this.player.questLog) {
            const messages = this.player.questLog.updateKillQuest(entity.name);
            for (const msg of messages) {
                this.addMessage(msg, 'quest');
            }
            this.player.kills++;
        }

        // 시체/아이템 드롭
        const corpse = new Item(entity.x, entity.y, '%', 'tile-food', `${entity.name}의 시체`, {
            consumable: true, nutrition: 100, itemType: 'food', value: 5
        });
        this.gameMap.addItem(corpse);

        this.gameMap.removeEntity(entity);
    }

    endTurn() {
        // 적 턴
        this.handleEnemyTurns();

        // 생존 시스템
        this.processSurvival();

        // 종교 시스템
        if (this.player.religion) {
            this.player.religion.processTurn();
        }

        // 시간 경과
        this.turnCount++;
        if (this.turnCount % 60 === 0) {
            this.hour++;
            if (this.hour >= 24) {
                this.hour = 0;
                this.day++;
                this.addMessage(`Day ${this.day}이 밝았다.`, 'system');
            }
        }

        this.updateFOV();
        this.render();
    }

    handleEnemyTurns() {
        for (const entity of this.gameMap.entities) {
            if (entity === this.player || !entity.isAlive) continue;
            if (!entity.ai || !entity.isHostile) continue;

            const distance = entity.distanceTo(this.player);

            if (distance <= 1.5) {
                // 공격
                this.meleeAttack(entity, this.player);
            } else if (distance <= entity.detectionRange && this.gameMap.visible[entity.x][entity.y]) {
                // 추적
                const dx = Math.sign(this.player.x - entity.x);
                const dy = Math.sign(this.player.y - entity.y);

                if (this.gameMap.isWalkable(entity.x + dx, entity.y + dy)) {
                    entity.move(dx, dy);
                } else if (this.gameMap.isWalkable(entity.x + dx, entity.y)) {
                    entity.move(dx, 0);
                } else if (this.gameMap.isWalkable(entity.x, entity.y + dy)) {
                    entity.move(0, dy);
                }
            }
        }
    }

    processSurvival() {
        this.player.hunger -= 1;
        this.player.thirst -= 2;

        if (this.player.hunger <= 200 && this.player.hunger > 190) {
            this.addMessage('배가 고파진다.', 'survival');
        }
        if (this.player.thirst <= 200 && this.player.thirst > 190) {
            this.addMessage('목이 마르다.', 'survival');
        }

        if (this.player.hunger <= 0) {
            this.player.hp -= 1;
            if (this.turnCount % 10 === 0) {
                this.addMessage('굶주림으로 체력이 줄어든다!', 'survival');
            }
        }
        if (this.player.thirst <= 0) {
            this.player.hp -= 1;
            if (this.turnCount % 10 === 0) {
                this.addMessage('탈수로 체력이 줄어든다!', 'survival');
            }
        }

        if (this.player.hp <= 0) {
            this.gameState = 'dead';
            if (this.player.hunger <= 0) {
                this.showGameOver('굶주림으로 사망했다.');
            } else {
                this.showGameOver('탈수로 사망했다.');
            }
        }
    }

    // ========================================================================
    // 아이템/인벤토리
    // ========================================================================

    pickupItem() {
        const items = this.gameMap.getItemsAt(this.player.x, this.player.y);
        if (items.length === 0) {
            this.addMessage('여기에는 아무것도 없다.', 'system');
            return;
        }

        if (this.player.inventory.length >= this.player.inventoryCapacity) {
            this.addMessage('인벤토리가 가득 찼다!', 'system');
            return;
        }

        const item = items[0];
        this.gameMap.removeItem(item);
        this.player.inventory.push(item);
        this.addMessage(`${item.name}을(를) 주웠다.`, 'item');
        this.endTurn();
    }

    useItem(index) {
        if (index < 0 || index >= this.player.inventory.length) return;

        const item = this.player.inventory[index];

        if (!item.consumable) {
            this.addMessage(`${item.name}은(는) 사용할 수 없다.`, 'system');
            return;
        }

        if (item.nutrition > 0) {
            this.player.hunger = Math.min(this.player.maxHunger, this.player.hunger + item.nutrition);
            this.addMessage(`${item.name}을(를) 먹었다.`, 'item');
        }
        if (item.hydration > 0) {
            this.player.thirst = Math.min(this.player.maxThirst, this.player.thirst + item.hydration);
            this.addMessage(`${item.name}을(를) 마셨다.`, 'item');
        }
        if (item.healAmount > 0) {
            const healed = this.player.heal(item.healAmount);
            this.addMessage(`체력이 ${healed} 회복되었다!`, 'item');
        }

        this.player.inventory.splice(index, 1);
        this.closeModal();
        this.endTurn();
    }

    dropItem(index) {
        if (index < 0 || index >= this.player.inventory.length) return;

        const item = this.player.inventory.splice(index, 1)[0];
        item.x = this.player.x;
        item.y = this.player.y;
        this.gameMap.addItem(item);
        this.addMessage(`${item.name}을(를) 버렸다.`, 'item');
        this.renderInventory();
    }

    // ========================================================================
    // NPC 대화
    // ========================================================================

    talkToNPC(npc) {
        if (npc.npcRole === 'merchant') {
            this.openShop(npc);
        } else {
            this.addMessage(`${npc.name}: "안녕하시오, 여행자여."`, 'system');
        }
    }

    openShop(merchant) {
        this.currentModal = 'shop';
        document.getElementById('shop-modal').classList.remove('hidden');
        document.getElementById('shop-title').textContent = `${merchant.name}의 상점`;

        const shopDiv = document.getElementById('shop-inventory');
        shopDiv.innerHTML = `
            <p>당신의 골드: ${this.player.gold}G</p>
            <h3>구매 가능한 물품:</h3>
            <div class="shop-item"><span>마른 고기</span><span class="price">10G</span></div>
            <div class="shop-item"><span>물병</span><span class="price">5G</span></div>
            <div class="shop-item"><span>치료 물약</span><span class="price">50G</span></div>
            <p style="color: #666; margin-top: 15px;">[ESC] 닫기</p>
        `;
    }

    // ========================================================================
    // 종교
    // ========================================================================

    pray() {
        if (!this.player.religion.deity) {
            // 신 선택
            this.showReligionModal();
            return;
        }

        const result = this.player.religion.pray();
        this.addMessage(result.message, 'religion');

        if (result.blessing) {
            this.player.heal(10);
            this.addMessage('신성한 힘으로 체력이 회복되었다!', 'religion');
        }

        this.endTurn();
    }

    showReligionModal() {
        this.currentModal = 'religion';
        document.getElementById('religion-modal').classList.remove('hidden');

        const infoDiv = document.getElementById('religion-info');
        if (this.player.religion.deity) {
            const deity = this.player.religion.deity;
            infoDiv.innerHTML = `
                <div class="deity-name">${deity.name} - ${deity.title}</div>
                <p>${deity.description}</p>
                <p>신앙 포인트: ${this.player.religion.faithPoints}</p>
                <p>은총: ${this.player.religion.favorLevel} (${this.player.religion.favor})</p>
                <p>기도 가능: ${this.player.religion.prayerTimeout <= 0 ? '예' : this.player.religion.prayerTimeout + '턴 후'}</p>
            `;
        } else {
            infoDiv.innerHTML = `
                <p>신앙을 선택하세요:</p>
                <div class="dialogue-option" onclick="game.convertTo('solarius')">
                    <span class="key">[1]</span> 솔라리우스 - 빛의 신 (치유)
                </div>
                <div class="dialogue-option" onclick="game.convertTo('grommash')">
                    <span class="key">[2]</span> 그롬마쉬 - 전쟁의 신 (전투)
                </div>
                <div class="dialogue-option" onclick="game.convertTo('sylvana')">
                    <span class="key">[3]</span> 실바나 - 자연의 여신 (생존)
                </div>
                <div class="dialogue-option" onclick="game.convertTo('mortis')">
                    <span class="key">[4]</span> 모르티스 - 죽음의 신 (암흑)
                </div>
            `;
        }
    }

    convertTo(deityId) {
        const deity = DEITIES[deityId];
        const msg = this.player.religion.convert(deity);
        this.addMessage(msg, 'religion');
        this.closeModal();
        this.render();
    }

    // ========================================================================
    // 저장/불러오기
    // ========================================================================

    saveGame() {
        const saveData = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            player: {
                x: this.player.x,
                y: this.player.y,
                hp: this.player.hp,
                maxHp: this.player.maxHp,
                hunger: this.player.hunger,
                thirst: this.player.thirst,
                gold: this.player.gold,
                inventory: this.player.inventory.map(i => ({
                    name: i.name,
                    char: i.char,
                    color: i.color,
                    consumable: i.consumable,
                    nutrition: i.nutrition,
                    hydration: i.hydration,
                    healAmount: i.healAmount,
                })),
                kills: this.player.kills,
                religion: this.player.religion.deity ? {
                    deityId: this.player.religion.deity.id,
                    favor: this.player.religion.favor,
                    faithPoints: this.player.religion.faithPoints,
                } : null,
            },
            turnCount: this.turnCount,
            hour: this.hour,
            day: this.day,
            dungeonLevel: this.dungeonLevel,
            map: {
                width: this.gameMap.width,
                height: this.gameMap.height,
                tiles: this.gameMap.tiles.map(col => col.map(t => ({
                    w: t.walkable,
                    t: t.transparent,
                    c: t.char,
                }))),
                explored: this.gameMap.explored,
            },
            entities: this.gameMap.entities.filter(e => e !== this.player).map(e => ({
                x: e.x, y: e.y, char: e.char, color: e.color, name: e.name,
                hp: e.hp, maxHp: e.maxHp, power: e.power, defense: e.defense,
                isHostile: e.isHostile, isNPC: e.isNPC,
            })),
            items: this.gameMap.items.map(i => ({
                x: i.x, y: i.y, char: i.char, color: i.color, name: i.name,
                consumable: i.consumable, nutrition: i.nutrition, hydration: i.hydration,
                healAmount: i.healAmount,
            })),
        };

        try {
            localStorage.setItem('roguelike_save', JSON.stringify(saveData));
            this.addMessage('게임이 저장되었습니다.', 'system');
        } catch (e) {
            this.addMessage('저장 실패: ' + e.message, 'system');
        }
    }

    loadGame() {
        try {
            const data = localStorage.getItem('roguelike_save');
            if (!data) {
                this.addMessage('저장된 게임이 없습니다.', 'system');
                return;
            }

            const save = JSON.parse(data);

            // 플레이어 복원
            this.player = new Actor(save.player.x, save.player.y, '@', 'tile-player', '당신', {
                maxHp: save.player.maxHp,
                hp: save.player.hp,
                gold: save.player.gold,
            });
            this.player.hp = save.player.hp;
            this.player.hunger = save.player.hunger;
            this.player.thirst = save.player.thirst;
            this.player.kills = save.player.kills || 0;
            this.player.questLog = new QuestLog();
            this.player.religion = new Religion();

            if (save.player.religion) {
                this.player.religion.deity = DEITIES[save.player.religion.deityId];
                this.player.religion.favor = save.player.religion.favor;
                this.player.religion.faithPoints = save.player.religion.faithPoints;
            }

            // 인벤토리 복원
            for (const itemData of save.player.inventory || []) {
                const item = new Item(0, 0, itemData.char, itemData.color, itemData.name, {
                    consumable: itemData.consumable,
                    nutrition: itemData.nutrition,
                    hydration: itemData.hydration,
                    healAmount: itemData.healAmount,
                });
                this.player.inventory.push(item);
            }

            // 맵 복원
            this.gameMap = new GameMap(save.map.width, save.map.height);
            for (let x = 0; x < save.map.width; x++) {
                for (let y = 0; y < save.map.height; y++) {
                    const t = save.map.tiles[x][y];
                    this.gameMap.tiles[x][y] = t.w ? { ...TILES.FLOOR } : { ...TILES.WALL };
                    this.gameMap.explored[x][y] = save.map.explored[x][y];
                }
            }

            // 엔티티 복원
            this.gameMap.addEntity(this.player);
            for (const e of save.entities || []) {
                const actor = new Actor(e.x, e.y, e.char, e.color, e.name, {
                    maxHp: e.maxHp, hp: e.hp, power: e.power, defense: e.defense,
                    isHostile: e.isHostile, isNPC: e.isNPC,
                });
                actor.hp = e.hp;
                actor.ai = e.isHostile ? 'hostile' : null;
                this.gameMap.addEntity(actor);
            }

            // 아이템 복원
            for (const i of save.items || []) {
                const item = new Item(i.x, i.y, i.char, i.color, i.name, {
                    consumable: i.consumable, nutrition: i.nutrition,
                    hydration: i.hydration, healAmount: i.healAmount,
                });
                this.gameMap.addItem(item);
            }

            this.turnCount = save.turnCount;
            this.hour = save.hour;
            this.day = save.day;
            this.dungeonLevel = save.dungeonLevel || 1;
            this.gameState = 'playing';
            this.messageLog = [];

            this.addMessage(`던전 ${this.dungeonLevel}층에서 게임을 불러왔습니다.`, 'system');
            this.updateFOV();
            this.showScreen('game-screen');
            this.render();

        } catch (e) {
            this.addMessage('불러오기 실패: ' + e.message, 'system');
        }
    }

    // ========================================================================
    // 렌더링
    // ========================================================================

    updateFOV() {
        this.gameMap.computeFOV(this.player.x, this.player.y, CONFIG.FOV_RADIUS);
    }

    render() {
        this.renderMap();
        this.render3D();
        this.renderUI();
    }

    renderMap() {
        const display = document.getElementById('map-display');
        let html = '';

        for (let y = 0; y < this.gameMap.height; y++) {
            for (let x = 0; x < this.gameMap.width; x++) {
                const visible = this.gameMap.visible[x][y];
                const explored = this.gameMap.explored[x][y];
                const tile = this.gameMap.tiles[x][y];

                let char = ' ';
                let colorClass = 'tile-unexplored';

                if (visible) {
                    // 엔티티 체크
                    const entity = this.gameMap.getActorAt(x, y);
                    const items = this.gameMap.getItemsAt(x, y);

                    if (entity === this.player) {
                        // 플레이어 방향에 따른 화살표 표시
                        const dirArrows = {
                            '0,-1': '▲',  // 북
                            '0,1': '▼',   // 남
                            '-1,0': '◀',  // 서
                            '1,0': '▶',   // 동
                            '-1,-1': '◤', // 북서
                            '1,-1': '◥',  // 북동
                            '-1,1': '◣',  // 남서
                            '1,1': '◢'    // 남동
                        };
                        const dirKey = `${this.playerDirection.dx},${this.playerDirection.dy}`;
                        char = dirArrows[dirKey] || '▲';
                        colorClass = 'tile-player';
                    } else if (entity) {
                        char = entity.char;
                        colorClass = entity.isNPC ? 'tile-npc' : 'tile-monster';
                    } else if (items.length > 0) {
                        char = items[0].char;
                        colorClass = items[0].color;
                    } else {
                        char = tile.char;
                        colorClass = tile.walkable ? 'tile-floor' : 'tile-wall-visible';
                    }
                } else if (explored) {
                    char = tile.char;
                    colorClass = 'tile-dark';
                }

                html += `<span class="${colorClass}">${char}</span>`;
            }
            html += '\n';
        }

        display.innerHTML = html;
    }

    render3D() {
        const display = document.getElementById('view3d-display');
        const mobileDisplay = document.getElementById('mobile-view3d');
        const compassDisplay = document.getElementById('compass-display');

        if (!display && !mobileDisplay) return;

        // 맵을 2D 문자 배열로 변환
        const mapData = [];
        for (let y = 0; y < this.gameMap.height; y++) {
            const row = [];
            for (let x = 0; x < this.gameMap.width; x++) {
                const tile = this.gameMap.tiles[x][y];
                row.push(tile.walkable ? '.' : '#');
            }
            mapData.push(row);
        }

        // 시야 내의 엔티티 목록 생성
        // 비행 몬스터 목록 (공중에 떠 있음)
        const flyingMonsters = ['b', 'h', 'R', 'F', 'P', 'e', 'E', 'G', 'D'];
        const entities = [];
        for (const entity of this.gameMap.entities) {
            if (entity === this.player) continue;
            if (!this.gameMap.visible[entity.x][entity.y]) continue;

            let type = 'monster';
            let color = '#f00';

            if (entity.isNPC) {
                type = 'npc';
                color = '#ff0';
            } else if (!entity.isAlive) {
                // 시체 처리
                type = 'corpse';
                color = '#644';
            }

            // 비행 몬스터 여부 확인 (살아있는 경우만)
            const isFlying = entity.isAlive && flyingMonsters.includes(entity.char);
            const isCorpse = !entity.isAlive;

            entities.push({
                x: entity.x,
                y: entity.y,
                char: isCorpse ? '%' : entity.char,  // 시체는 % 기호
                type: type,
                color: color,
                isFlying: isFlying,
                isGrounded: !isFlying && !isCorpse,
                isCorpse: isCorpse,
                isFloorItem: isCorpse,  // 바닥에 놓이는 것들
                name: entity.name,
            });
        }

        // 아이템 추가 (바닥에 놓임)
        for (const item of this.gameMap.items) {
            if (!this.gameMap.visible[item.x][item.y]) continue;

            entities.push({
                x: item.x,
                y: item.y,
                char: item.char,
                type: 'item',
                color: '#88f',
                isFlying: false,
                isGrounded: false,
                isItem: true,
                isFloorItem: true,  // 바닥에 놓이는 것들
                name: item.name,
            });
        }

        // 3D 뷰 렌더링
        const html = this.renderer3D.renderToHTML(
            mapData,
            this.player.x,
            this.player.y,
            entities
        );
        if (display) display.innerHTML = html;
        if (mobileDisplay) mobileDisplay.innerHTML = html;

        // 나침반 업데이트
        if (compassDisplay) {
            const angle = this.renderer3D.playerAngle;
            let direction;
            if (angle > -Math.PI/4 && angle <= Math.PI/4) direction = 'E';
            else if (angle > Math.PI/4 && angle <= 3*Math.PI/4) direction = 'S';
            else if (angle > -3*Math.PI/4 && angle <= -Math.PI/4) direction = 'N';
            else direction = 'W';
            compassDisplay.textContent = `[${direction}]`;
        }
    }

    toggleView() {
        const container = document.getElementById('view-container');
        container.classList.remove('view-3d-only', 'view-2d-only');

        if (this.viewMode === 'both') {
            this.viewMode = '3d-only';
            container.classList.add('view-3d-only');
            this.addMessage('3D 뷰 전용 모드', 'system');
        } else if (this.viewMode === '3d-only') {
            this.viewMode = '2d-only';
            container.classList.add('view-2d-only');
            this.addMessage('2D 맵 전용 모드', 'system');
        } else {
            this.viewMode = 'both';
            this.addMessage('분할 뷰 모드', 'system');
        }
        this.render();
    }

    renderUI() {
        // HP 바
        const hpPercent = (this.player.hp / this.player.maxHp) * 100;
        document.getElementById('hp-bar').style.width = hpPercent + '%';
        document.getElementById('hp-text').textContent = `${this.player.hp}/${this.player.maxHp}`;

        const hpBar = document.getElementById('hp-bar');
        hpBar.classList.remove('low', 'critical');
        if (hpPercent < 20) hpBar.classList.add('critical');
        else if (hpPercent < 50) hpBar.classList.add('low');

        // 배고픔 바
        const hungerPercent = this.player.hungerPercent;
        document.getElementById('hunger-bar').style.width = hungerPercent + '%';
        document.getElementById('hunger-text').textContent = Math.floor(hungerPercent) + '%';

        const hungerBar = document.getElementById('hunger-bar');
        hungerBar.classList.remove('low', 'critical');
        if (hungerPercent < 10) hungerBar.classList.add('critical');
        else if (hungerPercent < 30) hungerBar.classList.add('low');

        // 갈증 바
        const thirstPercent = this.player.thirstPercent;
        document.getElementById('thirst-bar').style.width = thirstPercent + '%';
        document.getElementById('thirst-text').textContent = Math.floor(thirstPercent) + '%';

        const thirstBar = document.getElementById('thirst-bar');
        thirstBar.classList.remove('low', 'critical');
        if (thirstPercent < 10) thirstBar.classList.add('critical');
        else if (thirstPercent < 30) thirstBar.classList.add('low');

        // 정보 바
        document.getElementById('time-display').textContent =
            `Day ${this.day}, ${String(this.hour).padStart(2, '0')}:00 (${this.getTimePeriod()})`;
        document.getElementById('turn-display').textContent = `Turn: ${this.turnCount}`;
        document.getElementById('gold-display').textContent = `Gold: ${this.player.gold}`;
        document.getElementById('position-display').textContent = `(${this.player.x}, ${this.player.y})`;

        // 던전 층 표시
        const floorDisplay = document.getElementById('floor-display');
        if (floorDisplay) {
            floorDisplay.textContent = `B${this.dungeonLevel}F`;
            // 층에 따른 색상 변경
            if (this.dungeonLevel >= 15) {
                floorDisplay.style.color = '#ff4444';
            } else if (this.dungeonLevel >= 10) {
                floorDisplay.style.color = '#ff8800';
            } else if (this.dungeonLevel >= 5) {
                floorDisplay.style.color = '#ffcc00';
            } else {
                floorDisplay.style.color = '#88ff88';
            }
        }

        // 메시지 로그
        this.renderMessages();

        // 모바일 UI 업데이트
        this.renderMobileUI();
    }

    renderMobileUI() {
        // 모바일 HP 바
        const hpPercent = (this.player.hp / this.player.maxHp) * 100;
        const mobileHpBar = document.getElementById('mobile-hp-bar');
        const mobileHpText = document.getElementById('mobile-hp-text');
        if (mobileHpBar) mobileHpBar.style.width = hpPercent + '%';
        if (mobileHpText) mobileHpText.textContent = `${this.player.hp}/${this.player.maxHp}`;

        // 모바일 배고픔 바
        const hungerPercent = this.player.hungerPercent;
        const mobileHungerBar = document.getElementById('mobile-hunger-bar');
        const mobileHungerText = document.getElementById('mobile-hunger-text');
        if (mobileHungerBar) mobileHungerBar.style.width = hungerPercent + '%';
        if (mobileHungerText) mobileHungerText.textContent = Math.floor(hungerPercent) + '%';

        // 모바일 갈증 바
        const thirstPercent = this.player.thirstPercent;
        const mobileThirstBar = document.getElementById('mobile-thirst-bar');
        const mobileThirstText = document.getElementById('mobile-thirst-text');
        if (mobileThirstBar) mobileThirstBar.style.width = thirstPercent + '%';
        if (mobileThirstText) mobileThirstText.textContent = Math.floor(thirstPercent) + '%';

        // 모바일 정보
        const mobileFloor = document.getElementById('mobile-floor');
        const mobileTime = document.getElementById('mobile-time');
        const mobileGold = document.getElementById('mobile-gold');
        if (mobileFloor) {
            mobileFloor.textContent = `B${this.dungeonLevel}F`;
            // 층에 따른 색상 변경
            if (this.dungeonLevel >= 15) {
                mobileFloor.style.color = '#ff4444';
            } else if (this.dungeonLevel >= 10) {
                mobileFloor.style.color = '#ff8800';
            } else if (this.dungeonLevel >= 5) {
                mobileFloor.style.color = '#ffcc00';
            } else {
                mobileFloor.style.color = '#88ff88';
            }
        }
        if (mobileTime) mobileTime.textContent = `D${this.day} ${String(this.hour).padStart(2, '0')}:00`;
        if (mobileGold) mobileGold.textContent = `💰${this.player.gold}`;

        // 모바일 메시지 (최근 1개)
        const mobileMessage = document.getElementById('mobile-message');
        if (mobileMessage && this.messageLog.length > 0) {
            const lastMsg = this.messageLog[this.messageLog.length - 1];
            mobileMessage.textContent = lastMsg.text;
            mobileMessage.style.color = this.getMessageColor(lastMsg.type);
        }
    }

    getMessageColor(type) {
        const colors = {
            'combat': '#ff6666',
            'item': '#6699ff',
            'survival': '#ffcc00',
            'quest': '#66ff66',
            'religion': '#cc99ff',
            'system': '#888888'
        };
        return colors[type] || '#888888';
    }

    renderMessages() {
        const logDiv = document.getElementById('message-log');
        logDiv.innerHTML = this.messageLog.slice(-5).map(m =>
            `<div class="msg msg-${m.type}">${m.text}</div>`
        ).join('');
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    addMessage(text, type = 'system') {
        this.messageLog.push({ text, type });
        if (this.messageLog.length > 100) {
            this.messageLog.shift();
        }
        this.renderMessages();
    }

    getTimePeriod() {
        if (this.hour >= 6 && this.hour < 12) return '아침';
        if (this.hour >= 12 && this.hour < 18) return '낮';
        if (this.hour >= 18 && this.hour < 21) return '저녁';
        return '밤';
    }

    // ========================================================================
    // 모달/화면
    // ========================================================================

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
        document.getElementById(screenId).classList.remove('hidden');
    }

    showInventory() {
        this.currentModal = 'inventory';
        document.getElementById('inventory-modal').classList.remove('hidden');
        this.renderInventory();
    }

    renderInventory() {
        const listDiv = document.getElementById('inventory-list');

        if (this.player.inventory.length === 0) {
            listDiv.innerHTML = '<div class="inventory-empty">(비어 있음)</div>';
            return;
        }

        listDiv.innerHTML = this.player.inventory.map((item, i) => {
            const key = String.fromCharCode(97 + i); // a, b, c, ...
            return `
                <div class="inventory-item ${item.itemType}" onclick="game.useItem(${i})">
                    <span class="key">${key})</span>
                    <span class="char">${item.char}</span>
                    <span class="name">${item.name}</span>
                </div>
            `;
        }).join('');
    }

    showQuestLog() {
        this.currentModal = 'quest';
        document.getElementById('quest-modal').classList.remove('hidden');

        const listDiv = document.getElementById('quest-list');
        const quests = this.player.questLog.active;

        if (quests.length === 0) {
            listDiv.innerHTML = '<p style="color: #666;">진행 중인 퀘스트가 없습니다.</p>';
            return;
        }

        listDiv.innerHTML = quests.map(q => `
            <div class="quest-item ${q.status}">
                <div class="quest-name">${q.name}</div>
                <div class="quest-desc">${q.description}</div>
                <div class="quest-progress">
                    ${q.objectives.map(o => `${o.target}: ${o.current}/${o.required}`).join(', ')}
                </div>
            </div>
        `).join('');
    }

    showHelp() {
        this.currentModal = 'help';
        document.getElementById('help-modal').classList.remove('hidden');
    }

    showTitle() {
        this.gameState = 'title';
        this.showScreen('title-screen');
    }

    showGameOver(reason) {
        document.getElementById('death-reason').textContent = reason;
        document.getElementById('final-days').textContent = this.day;
        document.getElementById('final-turns').textContent = this.turnCount;
        document.getElementById('final-kills').textContent = this.player.kills;
        this.showScreen('gameover-screen');
    }

    closeModal() {
        this.currentModal = null;
        document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
        this.render();
    }

    // ========================================================================
    // 입력 처리
    // ========================================================================

    setupEventListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.setupTouchControls();
    }

    setupTouchControls() {
        // 방향키 버튼
        const dpadButtons = document.querySelectorAll('.dpad-btn[data-dir]');
        // 9방향 이동 맵 (로그라이크 스타일)
        const dirMap = {
            'up': [0, -1],
            'down': [0, 1],
            'left': [-1, 0],
            'right': [1, 0],
            'up-left': [-1, -1],
            'up-right': [1, -1],
            'down-left': [-1, 1],
            'down-right': [1, 1]
        };

        dpadButtons.forEach(btn => {
            const handleMove = (e) => {
                e.preventDefault();
                const dir = btn.dataset.dir;
                if (dirMap[dir]) {
                    const [dx, dy] = dirMap[dir];
                    this.handlePlayerTurn(dx, dy);
                }
            };
            btn.addEventListener('touchstart', handleMove);
            btn.addEventListener('click', handleMove);
        });

        // 대기 버튼 (중앙)
        const waitBtn = document.querySelector('.dpad-center');
        if (waitBtn) {
            const handleWait = (e) => {
                e.preventDefault();
                if (this.gameState === 'playing' && !this.currentModal) {
                    this.addMessage('잠시 쉬었다.', 'system');
                    this.endTurn();
                }
            };
            waitBtn.addEventListener('touchstart', handleWait);
            waitBtn.addEventListener('click', handleWait);
        }

        // 기능키 버튼
        const actionButtons = document.querySelectorAll('.action-btn');
        actionButtons.forEach(btn => {
            const handleAction = (e) => {
                e.preventDefault();
                if (this.gameState !== 'playing') return;

                const action = btn.dataset.action;
                switch (action) {
                    case 'pickup':
                        if (!this.currentModal) this.pickupItem();
                        break;
                    case 'inventory':
                        if (this.currentModal === 'inventory') {
                            this.closeModal();
                        } else {
                            this.closeModal();
                            this.showInventory();
                        }
                        break;
                    case 'rest':
                        if (!this.currentModal) {
                            this.addMessage('잠시 휴식을 취했다.', 'system');
                            this.player.heal(1);
                            this.endTurn();
                        }
                        break;
                    case 'stairs':
                        if (!this.currentModal) {
                            // 계단 사용
                            const tile = this.gameMap.tiles[this.player.y][this.player.x];
                            if (tile.type === 'stairs_down') {
                                this.descendStairs();
                            } else if (tile.type === 'stairs_up') {
                                this.ascendStairs();
                            } else {
                                this.addMessage('여기에는 계단이 없다.', 'system');
                            }
                        }
                        break;
                }
            };
            btn.addEventListener('touchstart', handleAction);
            btn.addEventListener('click', handleAction);
        });
    }

    handleKeyDown(e) {
        // 모달이 열려있으면
        if (this.currentModal) {
            if (e.key === 'Escape') {
                this.closeModal();
                return;
            }

            if (this.currentModal === 'inventory') {
                const key = e.key.toLowerCase();
                if (key >= 'a' && key <= 'z') {
                    const index = key.charCodeAt(0) - 97;
                    if (e.shiftKey) {
                        this.dropItem(index);
                    } else {
                        this.useItem(index);
                    }
                }
            }
            return;
        }

        // 타이틀 화면이면
        if (this.gameState === 'title') {
            if (e.key === 'Enter' || e.key === ' ') {
                this.newGame();
            }
            return;
        }

        // 게임 오버면
        if (this.gameState === 'dead') {
            return;
        }

        // 게임 중
        if (this.gameState !== 'playing') return;

        const key = e.key;

        // 이동
        const moveKeys = {
            'ArrowUp': [0, -1], 'ArrowDown': [0, 1], 'ArrowLeft': [-1, 0], 'ArrowRight': [1, 0],
            'k': [0, -1], 'j': [0, 1], 'h': [-1, 0], 'l': [1, 0],
            'y': [-1, -1], 'u': [1, -1], 'b': [-1, 1], 'n': [1, 1],
            '8': [0, -1], '2': [0, 1], '4': [-1, 0], '6': [1, 0],
            '7': [-1, -1], '9': [1, -1], '1': [-1, 1], '3': [1, 1],
        };

        if (moveKeys[key]) {
            e.preventDefault();
            const [dx, dy] = moveKeys[key];
            this.handlePlayerTurn(dx, dy);
            return;
        }

        switch (key) {
            case '.':
            case '5':
                // 대기
                this.addMessage('잠시 쉬었다.', 'system');
                this.endTurn();
                break;

            case 'g':
            case ',':
                // 줍기
                this.pickupItem();
                break;

            case 'i':
                // 인벤토리
                this.showInventory();
                break;

            case 'q':
                // 퀘스트
                this.showQuestLog();
                break;

            case 'p':
                // 기도
                this.pray();
                break;

            case 'S':
                // 저장
                this.saveGame();
                break;

            case 'L':
                // 불러오기
                this.loadGame();
                break;

            case '?':
                // 도움말
                this.showHelp();
                break;

            case 'v':
            case 'V':
                // 뷰 전환
                this.toggleView();
                break;

            case '>':
                // 계단 내려가기
                this.goToNextFloor();
                break;

            case '<':
                // 계단 올라가기
                this.goToPrevFloor();
                break;

            case 'Escape':
                // ESC
                break;
        }
    }
}

// ============================================================================
// 게임 시작
// ============================================================================

const game = new Game();
