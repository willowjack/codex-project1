// ASCII 3D Dungeon Crawler Renderer
// Eye of the Beholder 스타일의 타일 기반 1인칭 렌더링

class ASCII3DRenderer {
    constructor(width = 40, height = 18) {
        this.width = width;
        this.height = height;
        this.maxDepth = 4;  // 최대 4타일 앞까지 렌더링

        // 방향 벡터 (dx, dy)
        this.directions = {
            'N': { dx: 0, dy: -1 },
            'S': { dx: 0, dy: 1 },
            'E': { dx: 1, dy: 0 },
            'W': { dx: -1, dy: 0 }
        };

        // 현재 바라보는 방향
        this.facing = 'N';

        // 방향별 좌/우 벡터
        this.sideVectors = {
            'N': { left: { dx: -1, dy: 0 }, right: { dx: 1, dy: 0 } },
            'S': { left: { dx: 1, dy: 0 }, right: { dx: -1, dy: 0 } },
            'E': { left: { dx: 0, dy: -1 }, right: { dx: 0, dy: 1 } },
            'W': { left: { dx: 0, dy: 1 }, right: { dx: 0, dy: -1 } }
        };

        // 깊이별 벽 크기 (원근감)
        // [시작Y, 끝Y, 시작X, 끝X, 두께]
        this.depthParams = {
            0: { wallHeight: 18, wallInset: 0, shade: '█' },   // 바로 앞
            1: { wallHeight: 14, wallInset: 3, shade: '▓' },   // 1타일 앞
            2: { wallHeight: 10, wallInset: 6, shade: '▒' },   // 2타일 앞
            3: { wallHeight: 6, wallInset: 9, shade: '░' },    // 3타일 앞
            4: { wallHeight: 4, wallInset: 11, shade: '∙' }    // 4타일 앞
        };

        // 기본 엔티티 크기
        this.defaultEntitySize = {
            height: 1.0,
            width: 1.0,
            weight: 1.0
        };

        // 몬스터 패턴
        this.asciiScalePatterns = this.initAsciiPatterns();
    }

    // 방향 설정
    setPlayerDirection(direction) {
        const dirMap = {
            'up': 'N', 'down': 'S', 'left': 'W', 'right': 'E',
            'N': 'N', 'S': 'S', 'E': 'E', 'W': 'W'
        };
        if (dirMap[direction]) {
            this.facing = dirMap[direction];
        }
    }

    // 라디안 각도로 방향 설정
    setAngleFromMovement(dx, dy) {
        if (dx > 0) this.facing = 'E';
        else if (dx < 0) this.facing = 'W';
        else if (dy > 0) this.facing = 'S';
        else if (dy < 0) this.facing = 'N';
    }

    // 메인 렌더링 함수
    render(gameMap, playerX, playerY, entities = []) {
        // 버퍼 초기화 (빈 공간으로)
        const buffer = this.createBuffer();

        // 바닥과 천장 그리기
        this.drawFloorAndCeiling(buffer);

        // 뒤에서부터 앞으로 벽 그리기 (painter's algorithm)
        for (let depth = this.maxDepth; depth >= 0; depth--) {
            this.drawWallsAtDepth(buffer, gameMap, playerX, playerY, depth);
        }

        // 엔티티 그리기
        this.drawEntities(buffer, gameMap, playerX, playerY, entities);

        return this.bufferToColoredArray(buffer);
    }

    // 버퍼 생성
    createBuffer() {
        const buffer = [];
        for (let y = 0; y < this.height; y++) {
            buffer[y] = [];
            for (let x = 0; x < this.width; x++) {
                buffer[y][x] = { char: ' ', color: '#222' };
            }
        }
        return buffer;
    }

    // 바닥과 천장 그리기
    drawFloorAndCeiling(buffer) {
        const midY = Math.floor(this.height / 2);

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (y < midY) {
                    // 천장 - 거리에 따라 어두워짐
                    const dist = midY - y;
                    const shade = dist > 6 ? ' ' : (dist > 3 ? '·' : '∙');
                    const bright = Math.max(20, 50 - dist * 5);
                    buffer[y][x] = { char: shade, color: `rgb(${bright},${bright+5},${bright+10})` };
                } else {
                    // 바닥 - 거리에 따라 밝아짐
                    const dist = y - midY;
                    const shade = dist < 2 ? '·' : (dist < 4 ? '∙' : '░');
                    const bright = Math.max(30, 80 - dist * 6);
                    buffer[y][x] = { char: shade, color: `rgb(${bright},${bright-10},${bright-20})` };
                }
            }
        }
    }

    // 특정 깊이의 벽 그리기
    drawWallsAtDepth(buffer, gameMap, playerX, playerY, depth) {
        const dir = this.directions[this.facing];
        const side = this.sideVectors[this.facing];

        // 해당 깊이의 타일 위치
        const checkX = Math.floor(playerX) + dir.dx * depth;
        const checkY = Math.floor(playerY) + dir.dy * depth;

        // 좌/우/중앙 타일 체크
        const leftX = checkX + side.left.dx;
        const leftY = checkY + side.left.dy;
        const rightX = checkX + side.right.dx;
        const rightY = checkY + side.right.dy;

        const params = this.depthParams[depth] || this.depthParams[this.maxDepth];
        const midY = Math.floor(this.height / 2);
        const halfHeight = Math.floor(params.wallHeight / 2);
        const startY = midY - halfHeight;
        const endY = midY + halfHeight;

        // 정면 벽 체크
        const hasFrontWall = this.isWall(gameMap, checkX, checkY);

        // 옆 벽 체크 (현재 위치 기준으로 좌우)
        const hasLeftWall = this.isWall(gameMap, leftX, leftY);
        const hasRightWall = this.isWall(gameMap, rightX, rightY);

        // 문 체크
        const isFrontDoor = this.isDoor(gameMap, checkX, checkY);

        if (depth === 0) {
            // 바로 앞에 벽이 있으면 화면 가득 채움
            if (hasFrontWall) {
                this.drawFrontWall(buffer, 0, this.width, startY, endY, 0, isFrontDoor);
            }
        } else {
            // 정면 벽 그리기 (가운데)
            if (hasFrontWall) {
                const inset = params.wallInset;
                this.drawFrontWall(buffer, inset, this.width - inset, startY, endY, depth, isFrontDoor);
            }

            // 좌측 벽 그리기 (원근감 있는 사다리꼴)
            if (hasLeftWall) {
                this.drawSideWall(buffer, 'left', depth, startY, endY, params);
            }

            // 우측 벽 그리기
            if (hasRightWall) {
                this.drawSideWall(buffer, 'right', depth, startY, endY, params);
            }
        }
    }

    // 정면 벽 그리기
    drawFrontWall(buffer, startX, endX, startY, endY, depth, isDoor = false) {
        const params = this.depthParams[depth];
        const shade = params.shade;
        const brightness = Math.max(40, 150 - depth * 30);

        for (let y = startY; y < endY && y < this.height; y++) {
            if (y < 0) continue;
            for (let x = startX; x < endX && x < this.width; x++) {
                if (x < 0) continue;

                let char = shade;
                let r = brightness, g = brightness, b = brightness + 10;

                // 벽 테두리 효과
                const isTopEdge = y === startY || y === startY + 1;
                const isBottomEdge = y === endY - 1 || y === endY - 2;
                const isLeftEdge = x === startX || x === startX + 1;
                const isRightEdge = x === endX - 1 || x === endX - 2;

                if (isTopEdge || isBottomEdge) {
                    char = '═';
                    r += 20; g += 20; b += 20;
                } else if (isLeftEdge || isRightEdge) {
                    char = '║';
                    r += 20; g += 20; b += 20;
                }

                // 문 효과
                if (isDoor && !isTopEdge && !isBottomEdge) {
                    const doorWidth = Math.floor((endX - startX) * 0.6);
                    const doorStart = startX + Math.floor((endX - startX - doorWidth) / 2);
                    const doorEnd = doorStart + doorWidth;

                    if (x >= doorStart && x < doorEnd) {
                        char = depth < 2 ? '▒' : '░';
                        r = Math.floor(brightness * 0.6);
                        g = Math.floor(brightness * 0.4);
                        b = Math.floor(brightness * 0.2);

                        // 문 손잡이
                        const handleX = doorEnd - 3;
                        const handleY = Math.floor((startY + endY) / 2);
                        if (x === handleX && y === handleY && depth < 2) {
                            char = '●';
                            r = 180; g = 150; b = 50;
                        }
                    }
                }

                buffer[y][x] = { char, color: `rgb(${r},${g},${b})` };
            }
        }
    }

    // 측면 벽 그리기 (원근감 있는 사다리꼴)
    drawSideWall(buffer, side, depth, startY, endY, params) {
        const prevParams = this.depthParams[depth - 1] || params;
        const brightness = Math.max(30, 120 - depth * 25);

        // 사다리꼴 벽 계산
        let nearInset, farInset, nearStart, nearEnd, farStart, farEnd;

        if (side === 'left') {
            nearInset = prevParams.wallInset;
            farInset = params.wallInset;
            nearStart = 0;
            nearEnd = nearInset;
            farStart = 0;
            farEnd = farInset;
        } else {
            nearInset = prevParams.wallInset;
            farInset = params.wallInset;
            nearStart = this.width - nearInset;
            nearEnd = this.width;
            farStart = this.width - farInset;
            farEnd = this.width;
        }

        const prevHalfHeight = Math.floor(prevParams.wallHeight / 2);
        const halfHeight = Math.floor(params.wallHeight / 2);
        const midY = Math.floor(this.height / 2);

        const nearStartY = midY - prevHalfHeight;
        const nearEndY = midY + prevHalfHeight;
        const farStartY = midY - halfHeight;
        const farEndY = midY + halfHeight;

        // 벽 그리기 (선형 보간)
        for (let y = Math.min(nearStartY, farStartY); y < Math.max(nearEndY, farEndY) && y < this.height; y++) {
            if (y < 0) continue;

            // Y 위치에 따른 X 범위 보간
            const t = (y - nearStartY) / (nearEndY - nearStartY);
            let xStart, xEnd;

            if (side === 'left') {
                xStart = 0;
                xEnd = Math.floor(nearEnd + (farEnd - nearEnd) * Math.abs(y - midY) / halfHeight);
            } else {
                xStart = Math.floor(nearStart - (nearStart - farStart) * Math.abs(y - midY) / halfHeight);
                xEnd = this.width;
            }

            // 벽 범위 체크
            const isInWallY = y >= farStartY && y < farEndY;

            for (let x = Math.max(0, xStart); x < Math.min(this.width, xEnd); x++) {
                if (!isInWallY) continue;

                const shade = params.shade;
                const isEdge = (side === 'left' && x === xEnd - 1) ||
                              (side === 'right' && x === xStart);

                let r = brightness - 20;
                let g = brightness - 20;
                let b = brightness;

                const char = isEdge ? '│' : shade;
                if (isEdge) { r += 30; g += 30; b += 30; }

                buffer[y][x] = { char, color: `rgb(${r},${g},${b})` };
            }
        }
    }

    // 벽 체크
    isWall(gameMap, x, y) {
        if (y < 0 || y >= gameMap.length || x < 0 || x >= gameMap[0].length) {
            return true;  // 맵 밖은 벽
        }
        const tile = gameMap[y][x];
        return tile === '#' || tile === '+';
    }

    // 문 체크
    isDoor(gameMap, x, y) {
        if (y < 0 || y >= gameMap.length || x < 0 || x >= gameMap[0].length) {
            return false;
        }
        return gameMap[y][x] === '+';
    }

    // 엔티티 그리기
    drawEntities(buffer, gameMap, playerX, playerY, entities) {
        const dir = this.directions[this.facing];
        const side = this.sideVectors[this.facing];

        // 엔티티를 거리순으로 정렬 (먼 것부터)
        const visibleEntities = [];

        for (const entity of entities) {
            // 플레이어 기준 상대 위치 계산
            const relX = entity.x - playerX;
            const relY = entity.y - playerY;

            // 전방 거리 계산
            const forwardDist = relX * dir.dx + relY * dir.dy;

            // 측면 거리 계산
            const sideDist = relX * side.right.dx + relY * side.right.dy;

            if (forwardDist > 0 && forwardDist <= this.maxDepth) {
                visibleEntities.push({
                    ...entity,
                    depth: Math.floor(forwardDist),
                    sideDist: sideDist
                });
            }
        }

        // 먼 것부터 그리기
        visibleEntities.sort((a, b) => b.depth - a.depth);

        for (const entity of visibleEntities) {
            this.drawEntity(buffer, entity, gameMap);
        }
    }

    // 개별 엔티티 그리기
    drawEntity(buffer, entity, gameMap) {
        const depth = entity.depth;
        const params = this.depthParams[depth] || this.depthParams[this.maxDepth];

        const midY = Math.floor(this.height / 2);
        const midX = Math.floor(this.width / 2);

        // 측면 오프셋에 따른 X 위치
        const sideOffset = Math.floor(entity.sideDist * (this.width / 4) / depth);
        const entityCenterX = midX + sideOffset;

        // 스케일 레벨
        const scaleLevel = this.getScaleLevel(depth);
        const entityChar = entity.char || '?';
        const pattern = this.getEntityPattern(entityChar, scaleLevel);

        if (!pattern) return;

        const patternHeight = pattern.length;
        const patternWidth = pattern[0] ? pattern[0].length : 0;

        // 엔티티 위치 계산
        const startY = midY - Math.floor(patternHeight / 2);
        const startX = entityCenterX - Math.floor(patternWidth / 2);

        // 패턴 그리기
        const brightness = Math.max(0.4, 1 - depth * 0.2);
        const baseColor = entity.color || '#ff6666';

        for (let py = 0; py < patternHeight; py++) {
            const bufY = startY + py;
            if (bufY < 0 || bufY >= this.height) continue;

            for (let px = 0; px < patternWidth; px++) {
                const bufX = startX + px;
                if (bufX < 0 || bufX >= this.width) continue;

                const char = pattern[py][px];
                if (char && char !== ' ') {
                    buffer[bufY][bufX] = {
                        char: char,
                        color: this.dimColor(baseColor, brightness)
                    };
                }
            }
        }
    }

    // 거리에 따른 스케일 레벨
    getScaleLevel(depth) {
        if (depth <= 1) return 5;
        if (depth <= 2) return 4;
        if (depth <= 3) return 3;
        return 2;
    }

    // 색상 어둡게
    dimColor(color, brightness) {
        let r, g, b;
        if (color.startsWith('#')) {
            const hex = color.slice(1);
            if (hex.length === 3) {
                r = parseInt(hex[0] + hex[0], 16);
                g = parseInt(hex[1] + hex[1], 16);
                b = parseInt(hex[2] + hex[2], 16);
            } else {
                r = parseInt(hex.slice(0, 2), 16);
                g = parseInt(hex.slice(2, 4), 16);
                b = parseInt(hex.slice(4, 6), 16);
            }
        } else {
            return color;
        }

        r = Math.floor(r * brightness);
        g = Math.floor(g * brightness);
        b = Math.floor(b * brightness);

        return `rgb(${r},${g},${b})`;
    }

    // 버퍼를 컬러 배열로 변환
    bufferToColoredArray(buffer) {
        return buffer;
    }

    // HTML로 렌더링
    renderToHTML(gameMap, playerX, playerY, entities = []) {
        const lines = this.render(gameMap, playerX, playerY, entities);
        let html = '';

        for (const line of lines) {
            for (const cell of line) {
                html += `<span style="color:${cell.color}">${cell.char}</span>`;
            }
            html += '\n';
        }

        return html;
    }

    // 몬스터 패턴 초기화
    initAsciiPatterns() {
        if (typeof MONSTER_PATTERNS !== 'undefined') {
            return this.convertExternalPatterns(MONSTER_PATTERNS);
        }
        return this.getDefaultPatterns();
    }

    convertExternalPatterns(externalPatterns) {
        const patterns = {};
        for (const [char, data] of Object.entries(externalPatterns)) {
            patterns[char] = data.patterns;
            if (data.size) {
                if (!this.entitySizes) this.entitySizes = {};
                this.entitySizes[char] = data.size;
            }
            if (data.color) {
                if (!this.entityColors) this.entityColors = {};
                this.entityColors[char] = data.color;
            }
        }
        return patterns;
    }

    getEntitySize(char) {
        if (this.entitySizes && this.entitySizes[char]) {
            return this.entitySizes[char];
        }
        return this.defaultEntitySize;
    }

    getEntityColor(char) {
        if (this.entityColors && this.entityColors[char]) {
            return this.entityColors[char];
        }
        return '#ff0000';
    }

    getEntityPattern(char, scaleLevel) {
        const patterns = this.asciiScalePatterns[char] || this.asciiScalePatterns['default'];
        if (!patterns) return null;
        return patterns[scaleLevel] || patterns[1];
    }

    getDefaultPatterns() {
        return {
            'g': {
                5: ["  ▄▄▄  ", " █░░░█ ", " █◕_◕█ ", "  ███  ", " ▄███▄ ", " █ g █ ", " ▀   ▀ "],
                4: [" ▄▄▄ ", " █▪█ ", "  █  ", " ▄█▄ ", " ▀ ▀ "],
                3: [" ▄ ", "█g█", " ▀ "],
                2: ["▄▄", "▀▀"],
                1: ["g"]
            },
            'o': {
                5: [" ▄███▄ ", "██◕▄◕██", " █▀▀▀█ ", "▄█████▄", "██ o ██", "█▀   ▀█", "▀     ▀"],
                4: [" ▄█▄ ", "█▪▄▪█", " ███ ", "█▀o▀█", "▀   ▀"],
                3: ["▄█▄", "█o█", "▀▀▀"],
                2: ["██", "▀▀"],
                1: ["o"]
            },
            'default': {
                5: ["  ▄▄▄  ", " █???█ ", " █   █ ", "  ███  ", " █   █ ", " █ ? █ ", " ▀   ▀ "],
                4: [" ▄▄▄ ", " █?█ ", "  █  ", " █?█ ", " ▀ ▀ "],
                3: [" ▄ ", "█?█", " ▀ "],
                2: ["??", "▀▀"],
                1: ["?"]
            }
        };
    }

    updatePatterns(newPatterns) {
        this.asciiScalePatterns = this.convertExternalPatterns(newPatterns);
    }

    addMonsterPattern(char, patternData) {
        this.asciiScalePatterns[char] = patternData.patterns;
        if (patternData.size) {
            if (!this.entitySizes) this.entitySizes = {};
            this.entitySizes[char] = patternData.size;
        }
        if (patternData.color) {
            if (!this.entityColors) this.entityColors = {};
            this.entityColors[char] = patternData.color;
        }
    }

    // 미니맵 (호환성)
    renderMinimap(gameMap, playerX, playerY, radius = 5) {
        const dirChars = { 'N': '▲', 'S': '▼', 'E': '▶', 'W': '◀' };
        const lines = [];

        for (let dy = -radius; dy <= radius; dy++) {
            let line = '';
            for (let dx = -radius; dx <= radius; dx++) {
                const mapX = Math.floor(playerX) + dx;
                const mapY = Math.floor(playerY) + dy;

                if (dx === 0 && dy === 0) {
                    line += dirChars[this.facing];
                } else if (mapX >= 0 && mapX < gameMap[0].length &&
                          mapY >= 0 && mapY < gameMap.length) {
                    line += gameMap[mapY][mapX];
                } else {
                    line += ' ';
                }
            }
            lines.push(line);
        }

        return lines.join('\n');
    }

    // playerAngle getter (호환성)
    get playerAngle() {
        const angles = { 'N': -Math.PI/2, 'S': Math.PI/2, 'E': 0, 'W': Math.PI };
        return angles[this.facing] || 0;
    }
}

// 컴퍼스 클래스
class Compass {
    constructor() {
        this.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    }

    render(angle) {
        let normalized = angle + Math.PI / 2;
        while (normalized < 0) normalized += 2 * Math.PI;
        while (normalized >= 2 * Math.PI) normalized -= 2 * Math.PI;

        const index = Math.round(normalized / (Math.PI / 4)) % 8;
        const facing = this.directions[index];

        return `    N\n  W + E  [${facing}]\n    S`;
    }
}

// 전역 내보내기
window.ASCII3DRenderer = ASCII3DRenderer;
window.Compass = Compass;
