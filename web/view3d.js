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

        // 엔티티 표시 문자
        this.entityChars = {
            'monster': ['☠', '◈', '◇', '·'],  // 거리별
            'npc': ['☺', '◎', '○', '·'],
            'item': ['★', '☆', '·', ' '],
        };

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

    // 엔티티(몬스터, NPC, 아이템) 렌더링
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
                        // 엔티티 크기 계산
                        const entityHeight = Math.floor(this.height / entity.dist);
                        const startY = Math.floor((this.height - entityHeight) / 2);
                        const endY = startY + entityHeight;

                        // 엔티티 타입에 따른 문자 선택
                        const entityType = entity.type || 'monster';
                        const chars = this.entityChars[entityType] || this.entityChars['monster'];
                        const charIndex = Math.min(
                            Math.floor(entity.dist / 4),
                            chars.length - 1
                        );
                        const entityChar = chars[charIndex];

                        // 화면에 그리기
                        const centerY = Math.floor(this.height / 2);
                        if (centerY >= 0 && centerY < this.height && entityChar !== ' ') {
                            buffer[screenX][centerY] = {
                                char: entityChar,
                                color: entity.color || '#f00'
                            };
                        }
                    }
                }
            }
        }
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
