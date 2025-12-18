// ASCII 3D Raycasting Renderer
// Wolfenstein 3D 스타일의 1인칭 ASCII 렌더링

class ASCII3DRenderer {
    constructor(width = 60, height = 20) {
        this.width = width;      // 3D 뷰 너비 (문자 수)
        this.height = height;    // 3D 뷰 높이 (문자 수)
        this.fov = Math.PI / 3;  // 시야각 (60도)
        this.maxDepth = 16;      // 최대 렌더링 거리

        // 거리에 따른 벽 문자 (가까울수록 진하게)
        this.wallShades = ['█', '▓', '▒', '░', '·', ' '];

        // 바닥/천장 문자
        this.floorChar = '.';
        this.ceilingChar = ' ';

        // 플레이어 방향 (라디안)
        this.playerAngle = 0;

        // 방향키에 따른 각도 매핑
        this.directionAngles = {
            'up': -Math.PI / 2,      // 북쪽
            'down': Math.PI / 2,     // 남쪽
            'left': Math.PI,         // 서쪽
            'right': 0,              // 동쪽
            'up-left': -3 * Math.PI / 4,
            'up-right': -Math.PI / 4,
            'down-left': 3 * Math.PI / 4,
            'down-right': Math.PI / 4,
        };

        // 기본 엔티티 크기 설정 (나중에 몬스터별로 커스터마이징 가능)
        this.defaultEntitySize = {
            height: 1.0,   // 기본 높이 배율
            width: 1.0,    // 기본 너비 배율
            weight: 1.0    // 기본 무게 (미래 사용)
        };

        // ASCII 확대 패턴 정의 (각 문자를 크기별로 확대)
        this.asciiScalePatterns = this.initAsciiPatterns();
    }

    // ASCII 문자 확대 패턴 초기화
    initAsciiPatterns() {
        return {
            // 고블린 (g) - 5단계 크기
            'g': {
                5: [  // 매우 가까움 (5x7)
                    "  ▄▄▄  ",
                    " █░░░█ ",
                    " █◕_◕█ ",
                    "  ███  ",
                    " ▄███▄ ",
                    " █ g █ ",
                    " ▀   ▀ "
                ],
                4: [  // 가까움 (4x5)
                    " ▄▄▄ ",
                    " █▪█ ",
                    "  █  ",
                    " ▄█▄ ",
                    " ▀ ▀ "
                ],
                3: [  // 보통 (3x3)
                    " ▄ ",
                    "█g█",
                    " ▀ "
                ],
                2: [  // 멀리 (2x2)
                    "▄▄",
                    "▀▀"
                ],
                1: [  // 매우 멀리 (1x1)
                    "g"
                ]
            },
            // 오크 (o) - 더 크고 근육질
            'o': {
                5: [
                    " ▄███▄ ",
                    "██◕▄◕██",
                    " █▀▀▀█ ",
                    "▄█████▄",
                    "██ o ██",
                    "█▀   ▀█",
                    "▀     ▀"
                ],
                4: [
                    " ▄█▄ ",
                    "█▪▄▪█",
                    " ███ ",
                    "█▀o▀█",
                    "▀   ▀"
                ],
                3: [
                    "▄█▄",
                    "█o█",
                    "▀▀▀"
                ],
                2: [
                    "██",
                    "▀▀"
                ],
                1: [
                    "o"
                ]
            },
            // 트롤 (T) - 거대함
            'T': {
                5: [
                    "▄▄███▄▄",
                    "██◕█◕██",
                    " ██▀██ ",
                    "▄█████▄",
                    "███T███",
                    "██▀ ▀██",
                    "▀▀   ▀▀"
                ],
                4: [
                    "▄███▄",
                    "█◕█◕█",
                    " ███ ",
                    "██T██",
                    "▀▀ ▀▀"
                ],
                3: [
                    "███",
                    "█T█",
                    "▀▀▀"
                ],
                2: [
                    "██",
                    "▀▀"
                ],
                1: [
                    "T"
                ]
            },
            // 쥐 (r) - 작음
            'r': {
                5: [
                    "       ",
                    "  ▄▄   ",
                    " ◕ ◕▄  ",
                    "  ▀▀▀▀~",
                    "   r   ",
                    "       ",
                    "       "
                ],
                4: [
                    "     ",
                    " ▄▄  ",
                    "◕◕▀▀~",
                    "     ",
                    "     "
                ],
                3: [
                    "   ",
                    "▄r~",
                    "   "
                ],
                2: [
                    "r~",
                    "  "
                ],
                1: [
                    "r"
                ]
            },
            // 늑대 (w)
            'w': {
                5: [
                    " ▲   ▲ ",
                    "██▄▄▄██",
                    "█ ◕ ◕ █",
                    " █▀▀▀█ ",
                    "▄█████▄",
                    "██ w ██",
                    "▀▀   ▀▀"
                ],
                4: [
                    "▲   ▲",
                    "█▄▄▄█",
                    " ███ ",
                    "█ w █",
                    "▀   ▀"
                ],
                3: [
                    "▲ ▲",
                    "█w█",
                    "▀ ▀"
                ],
                2: [
                    "▲▲",
                    "▀▀"
                ],
                1: [
                    "w"
                ]
            },
            // NPC (@) - 노란색
            '@': {
                5: [
                    "  ▄▄▄  ",
                    " █   █ ",
                    " █◕◕█ ",
                    "  ▀█▀  ",
                    " ▄███▄ ",
                    " █ @ █ ",
                    " ▀   ▀ "
                ],
                4: [
                    " ▄▄▄ ",
                    " █◕█ ",
                    "  █  ",
                    " █@█ ",
                    " ▀ ▀ "
                ],
                3: [
                    " ▄ ",
                    "█@█",
                    " ▀ "
                ],
                2: [
                    "@@",
                    "▀▀"
                ],
                1: [
                    "@"
                ]
            },
            // 기본 패턴 (알 수 없는 문자용)
            'default': {
                5: [
                    "  ▄▄▄  ",
                    " █???█ ",
                    " █   █ ",
                    "  ███  ",
                    " █   █ ",
                    " █ ? █ ",
                    " ▀   ▀ "
                ],
                4: [
                    " ▄▄▄ ",
                    " █?█ ",
                    "  █  ",
                    " █?█ ",
                    " ▀ ▀ "
                ],
                3: [
                    " ▄ ",
                    "█?█",
                    " ▀ "
                ],
                2: [
                    "??",
                    "▀▀"
                ],
                1: [
                    "?"
                ]
            }
        };
    }

    // 거리와 엔티티 크기에 따른 스케일 레벨 계산
    getScaleLevel(distance, entitySize = null) {
        const size = entitySize || this.defaultEntitySize;
        const sizeMultiplier = size.height || 1.0;

        // 거리에 따른 기본 스케일 (크기 배율 적용)
        const adjustedDist = distance / sizeMultiplier;

        if (adjustedDist < 2) return 5;      // 매우 가까움
        if (adjustedDist < 4) return 4;      // 가까움
        if (adjustedDist < 6) return 3;      // 보통
        if (adjustedDist < 10) return 2;     // 멀리
        return 1;                             // 매우 멀리
    }

    // 엔티티의 ASCII 패턴 가져오기
    getEntityPattern(char, scaleLevel) {
        const patterns = this.asciiScalePatterns[char] || this.asciiScalePatterns['default'];
        return patterns[scaleLevel] || patterns[1];
    }

    // 플레이어 방향 설정
    setPlayerDirection(direction) {
        if (this.directionAngles[direction] !== undefined) {
            this.playerAngle = this.directionAngles[direction];
        }
    }

    // 마지막 이동 방향으로 각도 설정
    setAngleFromMovement(dx, dy) {
        if (dx !== 0 || dy !== 0) {
            this.playerAngle = Math.atan2(dy, dx);
        }
    }

    // 레이캐스팅으로 3D 뷰 렌더링
    render(gameMap, playerX, playerY, entities = []) {
        const buffer = [];
        const depthBuffer = new Array(this.width).fill(this.maxDepth);

        // 각 열에 대해 레이 캐스팅
        for (let x = 0; x < this.width; x++) {
            // 현재 열의 레이 각도 계산
            const rayAngle = (this.playerAngle - this.fov / 2) +
                            (x / this.width) * this.fov;

            // 레이캐스팅으로 벽까지 거리 계산
            const { distance, hitWall, wallType } = this.castRay(
                gameMap, playerX, playerY, rayAngle
            );

            depthBuffer[x] = distance;

            // 어안 렌즈 효과 보정
            const correctedDistance = distance * Math.cos(rayAngle - this.playerAngle);

            // 천장과 바닥 계산
            const ceiling = Math.floor(this.height / 2 - this.height / correctedDistance);
            const floor = this.height - ceiling;

            // 이 열의 각 행 렌더링
            const column = [];
            for (let y = 0; y < this.height; y++) {
                if (y < ceiling) {
                    // 천장
                    column.push({ char: this.ceilingChar, color: '#111' });
                } else if (y >= ceiling && y < floor) {
                    // 벽
                    const shade = this.getWallShade(correctedDistance, wallType);
                    const color = this.getWallColor(correctedDistance, wallType);
                    column.push({ char: shade, color: color });
                } else {
                    // 바닥
                    const floorShade = this.getFloorShade(y, this.height);
                    column.push({ char: floorShade, color: '#333' });
                }
            }
            buffer.push(column);
        }

        // 엔티티 렌더링 (스프라이트)
        this.renderEntities(buffer, depthBuffer, gameMap, playerX, playerY, entities);

        return this.bufferToString(buffer);
    }

    // 레이 캐스팅
    castRay(gameMap, startX, startY, angle) {
        const rayDirX = Math.cos(angle);
        const rayDirY = Math.sin(angle);

        let rayX = startX + 0.5;
        let rayY = startY + 0.5;

        const stepSize = 0.1;
        let distance = 0;
        let hitWall = false;
        let wallType = 'wall';

        while (!hitWall && distance < this.maxDepth) {
            rayX += rayDirX * stepSize;
            rayY += rayDirY * stepSize;
            distance += stepSize;

            const mapX = Math.floor(rayX);
            const mapY = Math.floor(rayY);

            // 맵 범위 체크
            if (mapX < 0 || mapX >= gameMap[0].length ||
                mapY < 0 || mapY >= gameMap.length) {
                hitWall = true;
                wallType = 'boundary';
            } else {
                const tile = gameMap[mapY][mapX];
                if (tile === '#' || tile === '+') {
                    hitWall = true;
                    wallType = tile === '+' ? 'door' : 'wall';
                }
            }
        }

        return { distance, hitWall, wallType };
    }

    // 거리에 따른 벽 문자 선택
    getWallShade(distance, wallType) {
        const shadeIndex = Math.min(
            Math.floor(distance / this.maxDepth * this.wallShades.length),
            this.wallShades.length - 1
        );
        return this.wallShades[shadeIndex];
    }

    // 거리에 따른 벽 색상
    getWallColor(distance, wallType) {
        const brightness = Math.max(0, 1 - distance / this.maxDepth);

        let baseColor;
        switch (wallType) {
            case 'door':
                baseColor = { r: 139, g: 90, b: 43 };  // 갈색 문
                break;
            case 'boundary':
                baseColor = { r: 50, g: 50, b: 70 };   // 어두운 경계
                break;
            default:
                baseColor = { r: 100, g: 100, b: 120 }; // 회색 벽
        }

        const r = Math.floor(baseColor.r * brightness);
        const g = Math.floor(baseColor.g * brightness);
        const b = Math.floor(baseColor.b * brightness);

        return `rgb(${r},${g},${b})`;
    }

    // 바닥 셰이딩
    getFloorShade(y, height) {
        const distanceFromCenter = (y - height / 2) / (height / 2);
        if (distanceFromCenter > 0.8) return '░';
        if (distanceFromCenter > 0.6) return '·';
        return '.';
    }

    // 엔티티(몬스터, NPC, 아이템) 렌더링 - 확대된 ASCII 아트 사용
    renderEntities(buffer, depthBuffer, gameMap, playerX, playerY, entities) {
        // 플레이어로부터의 거리로 정렬 (먼 것부터)
        const sortedEntities = entities
            .map(e => ({
                ...e,
                dist: Math.sqrt(
                    Math.pow(e.x - playerX, 2) +
                    Math.pow(e.y - playerY, 2)
                )
            }))
            .filter(e => e.dist > 0.5 && e.dist < this.maxDepth)
            .sort((a, b) => b.dist - a.dist);

        for (const entity of sortedEntities) {
            // 엔티티 방향 계산
            const dx = entity.x - playerX;
            const dy = entity.y - playerY;
            const entityAngle = Math.atan2(dy, dx);

            // 플레이어 시야 내에 있는지 확인
            let angleDiff = entityAngle - this.playerAngle;

            // 각도 정규화
            while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
            while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;

            // 시야각 내에 있는지 확인
            if (Math.abs(angleDiff) < this.fov / 2) {
                // 화면 X 좌표 계산
                const screenX = Math.floor(
                    (angleDiff / this.fov + 0.5) * this.width
                );

                if (screenX >= 0 && screenX < this.width) {
                    // 깊이 버퍼 체크 (벽 뒤에 있으면 그리지 않음)
                    if (entity.dist < depthBuffer[screenX]) {
                        // 엔티티 크기 정보 가져오기 (있으면 사용, 없으면 기본값)
                        const entitySize = entity.size || this.defaultEntitySize;

                        // 스케일 레벨 계산
                        const scaleLevel = this.getScaleLevel(entity.dist, entitySize);

                        // 엔티티의 원본 ASCII 문자 가져오기
                        const entityChar = entity.char || '?';

                        // 확대된 ASCII 패턴 가져오기
                        const pattern = this.getEntityPattern(entityChar, scaleLevel);

                        // 패턴 크기
                        const patternHeight = pattern.length;
                        const patternWidth = pattern[0].length;

                        // 화면 중앙에 패턴 배치
                        const centerY = Math.floor(this.height / 2);
                        const startY = centerY - Math.floor(patternHeight / 2);
                        const startX = screenX - Math.floor(patternWidth / 2);

                        // 너비 배율 적용
                        const widthMultiplier = entitySize.width || 1.0;
                        const adjustedPatternWidth = Math.floor(patternWidth * widthMultiplier);

                        // 패턴을 버퍼에 그리기
                        for (let py = 0; py < patternHeight; py++) {
                            const bufferY = startY + py;
                            if (bufferY < 0 || bufferY >= this.height) continue;

                            for (let px = 0; px < patternWidth; px++) {
                                // 너비 배율에 따른 X 위치 조정
                                const bufferX = startX + Math.floor(px * widthMultiplier);
                                if (bufferX < 0 || bufferX >= this.width) continue;

                                // 깊이 버퍼 확인 (벽 뒤에 있으면 그리지 않음)
                                if (entity.dist >= depthBuffer[bufferX]) continue;

                                const char = pattern[py][px];
                                if (char && char !== ' ') {
                                    // 색상 결정 (거리에 따라 어두워짐)
                                    const brightness = Math.max(0.3, 1 - entity.dist / this.maxDepth);
                                    const baseColor = entity.color || '#ff0000';
                                    const dimmedColor = this.dimColor(baseColor, brightness);

                                    buffer[bufferX][bufferY] = {
                                        char: char,
                                        color: dimmedColor
                                    };

                                    // 너비 배율이 1보다 크면 추가 열도 채우기
                                    if (widthMultiplier > 1) {
                                        for (let wx = 1; wx < widthMultiplier; wx++) {
                                            const extraX = bufferX + wx;
                                            if (extraX >= 0 && extraX < this.width &&
                                                entity.dist < depthBuffer[extraX]) {
                                                buffer[extraX][bufferY] = {
                                                    char: char,
                                                    color: dimmedColor
                                                };
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 색상을 어둡게 조절
    dimColor(color, brightness) {
        // hex 색상을 RGB로 변환
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
        } else if (color.startsWith('rgb')) {
            const match = color.match(/\d+/g);
            if (match) {
                [r, g, b] = match.map(Number);
            } else {
                return color;
            }
        } else {
            return color;
        }

        // 밝기 적용
        r = Math.floor(r * brightness);
        g = Math.floor(g * brightness);
        b = Math.floor(b * brightness);

        return `rgb(${r},${g},${b})`;
    }

    // 버퍼를 문자열로 변환
    bufferToString(buffer) {
        const lines = [];
        for (let y = 0; y < this.height; y++) {
            let line = '';
            let coloredLine = [];
            for (let x = 0; x < this.width; x++) {
                const cell = buffer[x][y];
                coloredLine.push(cell);
            }
            lines.push(coloredLine);
        }
        return lines;
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

    // 미니맵 생성 (플레이어 시야 방향 표시)
    renderMinimap(gameMap, playerX, playerY, radius = 5) {
        const lines = [];
        const dirChars = {
            'up': '▲',
            'down': '▼',
            'left': '◀',
            'right': '▶'
        };

        // 각도로부터 방향 결정
        let direction;
        const angle = this.playerAngle;
        if (angle > -Math.PI/4 && angle <= Math.PI/4) direction = '▶';
        else if (angle > Math.PI/4 && angle <= 3*Math.PI/4) direction = '▼';
        else if (angle > -3*Math.PI/4 && angle <= -Math.PI/4) direction = '▲';
        else direction = '◀';

        for (let dy = -radius; dy <= radius; dy++) {
            let line = '';
            for (let dx = -radius; dx <= radius; dx++) {
                const mapX = Math.floor(playerX) + dx;
                const mapY = Math.floor(playerY) + dy;

                if (dx === 0 && dy === 0) {
                    line += direction;  // 플레이어 위치와 방향
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
}

// 컴퍼스 (나침반) 렌더링
class Compass {
    constructor() {
        this.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    }

    render(angle) {
        // 각도를 8방향 인덱스로 변환
        let normalized = angle + Math.PI / 2;  // 북쪽이 0이 되도록 조정
        while (normalized < 0) normalized += 2 * Math.PI;
        while (normalized >= 2 * Math.PI) normalized -= 2 * Math.PI;

        const index = Math.round(normalized / (Math.PI / 4)) % 8;
        const facing = this.directions[index];

        return `
    N
  W + E  [${facing}]
    S
        `.trim();
    }
}

// 전역으로 내보내기
window.ASCII3DRenderer = ASCII3DRenderer;
window.Compass = Compass;
