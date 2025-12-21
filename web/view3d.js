// ASCII 3D Dungeon Crawler Renderer
// Eye of the Beholder / Dungeon Master 스타일

class ASCII3DRenderer {
    constructor(width = 50, height = 20) {
        this.width = width;
        this.height = height;
        this.maxDepth = 4;

        this.facing = 'N';
        this.directions = {
            'N': { dx: 0, dy: -1 }, 'S': { dx: 0, dy: 1 },
            'E': { dx: 1, dy: 0 }, 'W': { dx: -1, dy: 0 }
        };
        this.sideVectors = {
            'N': { left: { dx: -1, dy: 0 }, right: { dx: 1, dy: 0 } },
            'S': { left: { dx: 1, dy: 0 }, right: { dx: -1, dy: 0 } },
            'E': { left: { dx: 0, dy: -1 }, right: { dx: 0, dy: 1 } },
            'W': { left: { dx: 0, dy: 1 }, right: { dx: 0, dy: -1 } }
        };

        // 깊이별 뷰포트 영역 정의 (left, right, top, bottom 비율)
        this.viewports = {
            0: { l: 0.0, r: 1.0, t: 0.0, b: 1.0 },
            1: { l: 0.15, r: 0.85, t: 0.15, b: 0.85 },
            2: { l: 0.28, r: 0.72, t: 0.28, b: 0.72 },
            3: { l: 0.38, r: 0.62, t: 0.38, b: 0.62 },
            4: { l: 0.45, r: 0.55, t: 0.45, b: 0.55 }
        };

        this.defaultEntitySize = { height: 1.0, width: 1.0, weight: 1.0 };
        this.asciiScalePatterns = this.initAsciiPatterns();
    }

    setPlayerDirection(direction) {
        const dirMap = { 'up': 'N', 'down': 'S', 'left': 'W', 'right': 'E', 'N': 'N', 'S': 'S', 'E': 'E', 'W': 'W' };
        if (dirMap[direction]) this.facing = dirMap[direction];
    }

    setAngleFromMovement(dx, dy) {
        if (dx > 0) this.facing = 'E';
        else if (dx < 0) this.facing = 'W';
        else if (dy > 0) this.facing = 'S';
        else if (dy < 0) this.facing = 'N';
    }

    // 메인 렌더링
    render(gameMap, playerX, playerY, entities = []) {
        const buffer = this.createBuffer();

        // 1. 배경 (어두운 중앙)
        this.drawBackground(buffer);

        // 2. 뒤에서부터 앞으로 벽 그리기
        for (let depth = this.maxDepth; depth >= 1; depth--) {
            this.drawDepthLayer(buffer, gameMap, playerX, playerY, depth);
        }

        // 3. 엔티티
        this.drawEntities(buffer, gameMap, playerX, playerY, entities);

        return buffer;
    }

    createBuffer() {
        const buffer = [];
        for (let y = 0; y < this.height; y++) {
            buffer[y] = [];
            for (let x = 0; x < this.width; x++) {
                buffer[y][x] = { char: ' ', color: '#111' };
            }
        }
        return buffer;
    }

    // 배경 그리기 (천장/바닥 그라데이션)
    drawBackground(buffer) {
        const midY = this.height / 2;

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const distFromMid = Math.abs(y - midY) / midY;

                if (y < midY) {
                    // 천장 - 위쪽이 밝고 중앙으로 갈수록 어두움
                    const bright = Math.floor(40 + distFromMid * 30);
                    const char = distFromMid > 0.6 ? '░' : (distFromMid > 0.3 ? '·' : ' ');
                    buffer[y][x] = { char, color: `rgb(${bright-10},${bright-5},${bright})` };
                } else {
                    // 바닥 - 아래쪽이 밝고 중앙으로 갈수록 어두움
                    const bright = Math.floor(50 + distFromMid * 40);
                    const char = distFromMid > 0.6 ? '░' : (distFromMid > 0.3 ? '·' : ' ');
                    buffer[y][x] = { char, color: `rgb(${bright},${bright-15},${bright-25})` };
                }
            }
        }
    }

    // 특정 깊이의 레이어 그리기
    drawDepthLayer(buffer, gameMap, playerX, playerY, depth) {
        const dir = this.directions[this.facing];
        const side = this.sideVectors[this.facing];

        const checkX = Math.floor(playerX) + dir.dx * depth;
        const checkY = Math.floor(playerY) + dir.dy * depth;

        const leftX = checkX + side.left.dx;
        const leftY = checkY + side.left.dy;
        const rightX = checkX + side.right.dx;
        const rightY = checkY + side.right.dy;

        const vp = this.viewports[depth];
        const prevVp = this.viewports[depth - 1];

        const hasFront = this.isWall(gameMap, checkX, checkY);
        const hasLeft = this.isWall(gameMap, leftX, leftY);
        const hasRight = this.isWall(gameMap, rightX, rightY);
        const isFrontDoor = this.isDoor(gameMap, checkX, checkY);
        const isLeftDoor = this.isDoor(gameMap, leftX, leftY);
        const isRightDoor = this.isDoor(gameMap, rightX, rightY);

        // 좌측 벽 (대각선)
        if (hasLeft) {
            this.drawLeftWall(buffer, prevVp, vp, depth, isLeftDoor);
        }

        // 우측 벽 (대각선)
        if (hasRight) {
            this.drawRightWall(buffer, prevVp, vp, depth, isRightDoor);
        }

        // 정면 벽
        if (hasFront) {
            this.drawFrontWall(buffer, vp, depth, isFrontDoor);
        }
    }

    // 좌측 대각선 벽 (정면보다 확실히 어둡게)
    drawLeftWall(buffer, prevVp, vp, depth, isDoor) {
        const bright = Math.max(45, 95 - depth * 15);  // 측면은 어둡게
        const wallChar = depth <= 2 ? '▒' : '░';  // 어두운 문자

        const prevL = Math.floor(prevVp.l * this.width);
        const prevT = Math.floor(prevVp.t * this.height);
        const prevB = Math.floor(prevVp.b * this.height);

        const curL = Math.floor(vp.l * this.width);
        const curT = Math.floor(vp.t * this.height);
        const curB = Math.floor(vp.b * this.height);

        // 줄무늬 위치를 현재 뷰포트 기준으로 계산 (정면 벽과 맞춤)
        const stripeTop = curT + 2;
        const stripeBottom = curB - 3;

        // 벽면 채우기 (사다리꼴)
        for (let y = prevT; y < prevB; y++) {
            // Y 위치에 따른 X 범위 (선형 보간)
            const t = (y - prevT) / (prevB - prevT);
            const leftEdge = prevL;
            const rightEdge = Math.floor(prevL + (curL - prevL) * (y < this.height/2 ?
                (this.height/2 - y) / (this.height/2 - prevT) :
                (y - this.height/2) / (prevB - this.height/2)));

            for (let x = leftEdge; x < rightEdge && x < this.width; x++) {
                if (y < 0 || y >= this.height || x < 0) continue;

                // x 위치에 따른 밝기 그라데이션 (안쪽=밝음, 바깥쪽=어두움)
                const xRatio = (x - leftEdge) / Math.max(1, rightEdge - leftEdge);
                const localBright = bright - 25 + (xRatio * 35);  // 바깥쪽 어둡게, 안쪽 밝게

                let char = wallChar;
                let r = localBright - 10, g = localBright - 15, b = localBright;

                // 대각선 가장자리 (밝은 테두리) - 줄무늬 위치 제외
                const isStripeY = (y === stripeTop || y === stripeBottom);
                if (x === rightEdge - 1 && !isStripeY) {
                    char = y < this.height/2 ? '╲' : '╱';
                    r = bright + 45; g = bright + 40; b = bright + 50;
                }

                // 수평 줄무늬 장식 (정면 벽과 높이 맞춤) - 대각선 위치까지 연장
                if (isStripeY) {
                    char = '─';
                    r = 120 + xRatio * 40; g = 105 + xRatio * 35; b = 35;
                }

                // 문
                if (isDoor && x > leftEdge + 1 && x < rightEdge - 2) {
                    const doorTop = curT + 3;
                    const doorBottom = curB - 2;
                    if (y > doorTop && y < doorBottom) {
                        char = '▒';
                        r = Math.floor(bright * 0.5);
                        g = Math.floor(bright * 0.35);
                        b = Math.floor(bright * 0.2);
                    }
                }

                buffer[y][x] = { char, color: `rgb(${r},${g},${b})` };
            }
        }
    }

    // 우측 대각선 벽 (정면보다 확실히 어둡게)
    drawRightWall(buffer, prevVp, vp, depth, isDoor) {
        const bright = Math.max(45, 95 - depth * 15);  // 측면은 어둡게
        const wallChar = depth <= 2 ? '▒' : '░';  // 어두운 문자

        const prevR = Math.floor(prevVp.r * this.width);
        const prevT = Math.floor(prevVp.t * this.height);
        const prevB = Math.floor(prevVp.b * this.height);

        const curR = Math.floor(vp.r * this.width);
        const curT = Math.floor(vp.t * this.height);
        const curB = Math.floor(vp.b * this.height);

        // 줄무늬 위치를 현재 뷰포트 기준으로 계산 (정면 벽과 맞춤)
        const stripeTop = curT + 2;
        const stripeBottom = curB - 3;

        for (let y = prevT; y < prevB; y++) {
            const leftEdge = Math.floor(prevR - (prevR - curR) * (y < this.height/2 ?
                (this.height/2 - y) / (this.height/2 - prevT) :
                (y - this.height/2) / (prevB - this.height/2)));
            const rightEdge = prevR;

            for (let x = leftEdge; x < rightEdge && x < this.width; x++) {
                if (y < 0 || y >= this.height || x < 0) continue;

                // x 위치에 따른 밝기 그라데이션 (안쪽=밝음, 바깥쪽=어두움)
                const xRatio = (rightEdge - x) / Math.max(1, rightEdge - leftEdge);
                const localBright = bright - 25 + (xRatio * 35);  // 바깥쪽 어둡게, 안쪽 밝게

                let char = wallChar;
                let r = localBright - 10, g = localBright - 15, b = localBright;

                // 대각선 가장자리 (밝은 테두리) - 줄무늬 위치 제외
                const isStripeY = (y === stripeTop || y === stripeBottom);
                if (x === leftEdge && !isStripeY) {
                    char = y < this.height/2 ? '╱' : '╲';
                    r = bright + 45; g = bright + 40; b = bright + 50;
                }

                // 수평 줄무늬 장식 (정면 벽과 높이 맞춤) - 대각선 위치까지 연장
                if (isStripeY) {
                    char = '─';
                    r = 120 + xRatio * 40; g = 105 + xRatio * 35; b = 35;
                }

                // 문
                if (isDoor && x > leftEdge + 2 && x < rightEdge - 1) {
                    const doorTop = curT + 3;
                    const doorBottom = curB - 2;
                    if (y > doorTop && y < doorBottom) {
                        char = '▒';
                        r = Math.floor(bright * 0.5);
                        g = Math.floor(bright * 0.35);
                        b = Math.floor(bright * 0.2);
                    }
                }

                buffer[y][x] = { char, color: `rgb(${r},${g},${b})` };
            }
        }
    }

    // 정면 벽 (밝게)
    drawFrontWall(buffer, vp, depth, isDoor) {
        const bright = Math.max(80, 170 - depth * 25);  // 정면은 밝게
        const wallChar = depth <= 1 ? '█' : (depth <= 2 ? '▓' : '▒');

        const left = Math.floor(vp.l * this.width);
        const right = Math.floor(vp.r * this.width);
        const top = Math.floor(vp.t * this.height);
        const bottom = Math.floor(vp.b * this.height);

        for (let y = top; y < bottom && y < this.height; y++) {
            for (let x = left; x < right && x < this.width; x++) {
                if (y < 0 || x < 0) continue;

                let char = wallChar;
                let r = bright, g = bright, b = bright + 15;

                // 테두리
                const isTop = y === top;
                const isBottom = y === bottom - 1;
                const isLeft = x === left;
                const isRight = x === right - 1;

                if (isTop || isBottom) {
                    char = '═';
                    r += 30; g += 30; b += 30;
                } else if (isLeft || isRight) {
                    char = '║';
                    r += 30; g += 30; b += 30;
                }

                // 수평 줄무늬 장식
                if (!isTop && !isBottom && (y === top + 2 || y === bottom - 3)) {
                    char = '─';
                    r = 180; g = 160; b = 50;
                }

                // 문
                if (isDoor && !isTop && !isBottom && !isLeft && !isRight) {
                    const doorWidth = Math.floor((right - left) * 0.5);
                    const doorStart = left + Math.floor((right - left - doorWidth) / 2);
                    const doorEnd = doorStart + doorWidth;
                    const doorTop = top + 2;

                    if (x >= doorStart && x < doorEnd && y > doorTop) {
                        char = depth <= 2 ? '▒' : '░';
                        r = Math.floor(bright * 0.5);
                        g = Math.floor(bright * 0.35);
                        b = Math.floor(bright * 0.2);

                        // 문틀
                        if (x === doorStart || x === doorEnd - 1) {
                            char = '│';
                            r = 100; g = 70; b = 40;
                        }
                        if (y === doorTop + 1) {
                            char = '─';
                            r = 100; g = 70; b = 40;
                        }

                        // 손잡이
                        const handleX = doorEnd - 2;
                        const handleY = Math.floor((top + bottom) / 2);
                        if (x === handleX && y === handleY && depth <= 2) {
                            char = '●';
                            r = 200; g = 180; b = 60;
                        }
                    }
                }

                buffer[y][x] = { char, color: `rgb(${r},${g},${b})` };
            }
        }
    }

    // 벽/문 체크
    isWall(gameMap, x, y) {
        if (y < 0 || y >= gameMap.length || x < 0 || x >= gameMap[0].length) return true;
        const tile = gameMap[y][x];
        return tile === '#' || tile === '+';
    }

    isDoor(gameMap, x, y) {
        if (y < 0 || y >= gameMap.length || x < 0 || x >= gameMap[0].length) return false;
        return gameMap[y][x] === '+';
    }

    // 엔티티 그리기
    drawEntities(buffer, gameMap, playerX, playerY, entities) {
        const dir = this.directions[this.facing];
        const side = this.sideVectors[this.facing];
        const visibleEntities = [];

        for (const entity of entities) {
            const relX = entity.x - playerX;
            const relY = entity.y - playerY;
            const forwardDist = relX * dir.dx + relY * dir.dy;
            const sideDist = relX * side.right.dx + relY * side.right.dy;

            if (forwardDist > 0 && forwardDist <= this.maxDepth) {
                visibleEntities.push({ ...entity, depth: Math.floor(forwardDist), sideDist });
            }
        }

        // 깊이별로 정렬 (뒤에서 앞으로)
        visibleEntities.sort((a, b) => b.depth - a.depth);

        // 같은 위치(depth, sideDist)에 있는 엔티티들을 그룹화
        const positionGroups = new Map();
        for (const entity of visibleEntities) {
            const key = `${entity.depth},${Math.round(entity.sideDist * 10)}`;
            if (!positionGroups.has(key)) {
                positionGroups.set(key, { main: [], floor: [] });
            }
            const group = positionGroups.get(key);
            if (entity.isFloorItem) {
                group.floor.push(entity);
            } else {
                group.main.push(entity);
            }
        }

        // 그룹별로 렌더링 (뒤에서 앞으로)
        const sortedKeys = [...positionGroups.keys()].sort((a, b) => {
            const depthA = parseInt(a.split(',')[0]);
            const depthB = parseInt(b.split(',')[0]);
            return depthB - depthA;
        });

        for (const key of sortedKeys) {
            const group = positionGroups.get(key);

            // 1. 바닥 아이템/시체 먼저 그리기 (좌우로 분산)
            const floorCount = group.floor.length;
            for (let i = 0; i < floorCount; i++) {
                const entity = group.floor[i];
                // 여러 개일 때 좌우로 분산 오프셋
                const spreadOffset = floorCount > 1
                    ? (i - (floorCount - 1) / 2) * 0.2
                    : 0;
                this.drawEntity(buffer, entity, spreadOffset);
            }

            // 2. 메인 엔티티 (몬스터/NPC) 그리기
            for (const entity of group.main) {
                this.drawEntity(buffer, entity, 0);
            }
        }
    }

    drawEntity(buffer, entity, horizontalSpread = 0) {
        const depth = entity.depth;
        const vp = this.viewports[depth];

        const midY = Math.floor(this.height / 2);
        const midX = Math.floor(this.width / 2);

        const viewWidth = (vp.r - vp.l) * this.width;
        const sideOffset = Math.floor(entity.sideDist * viewWidth * 0.4);
        // 좌우 분산 오프셋 적용
        const spreadPixels = Math.floor(horizontalSpread * viewWidth * 0.5);
        const entityCenterX = midX + sideOffset + spreadPixels;

        const scaleLevel = depth <= 1 ? 5 : (depth <= 2 ? 4 : (depth <= 3 ? 3 : 2));

        // 바닥 아이템/시체는 작은 심볼로 표시
        let pattern;
        if (entity.isFloorItem) {
            pattern = this.getFloorItemPattern(entity, scaleLevel);
        } else {
            pattern = this.getEntityPattern(entity.char || '?', scaleLevel);
        }

        if (!pattern) return;

        // Y 위치 오프셋 계산 (비행/지상/아이템 구분)
        // 뷰포트 하단 계산 (바닥선 위치)
        const floorY = Math.floor(vp.b * this.height);

        let yOffset = 0;
        if (entity.isFlying) {
            // 비행 몬스터: 위쪽에 표시 (공중에 떠있음)
            yOffset = -Math.floor(pattern.length * 0.6);
        } else if (entity.isFloorItem) {
            // 바닥 아이템/시체: 화면 하단에 표시
            const bottomArea = Math.floor(this.height * 0.35);
            yOffset = bottomArea;
        } else if (entity.isGrounded) {
            // 지상 몬스터: 바닥에 발이 닿게 표시
            // 몬스터 하단이 바닥선에 오도록 계산
            const monsterBottom = midY + Math.floor(pattern.length / 2);
            const targetBottom = floorY - 1;  // 바닥선 바로 위
            yOffset = targetBottom - monsterBottom;
        }

        const startY = midY - Math.floor(pattern.length / 2) + yOffset;
        const startX = entityCenterX - Math.floor(pattern[0].length / 2);

        const brightness = Math.max(0.4, 1 - depth * 0.2);
        const baseColor = entity.color || '#ff6666';

        for (let py = 0; py < pattern.length; py++) {
            for (let px = 0; px < pattern[py].length; px++) {
                const bufY = startY + py;
                const bufX = startX + px;
                if (bufY < 0 || bufY >= this.height || bufX < 0 || bufX >= this.width) continue;

                const char = pattern[py][px];
                if (char && char !== ' ') {
                    buffer[bufY][bufX] = { char, color: this.dimColor(baseColor, brightness) };
                }
            }
        }
    }

    // 바닥 아이템/시체용 간단한 패턴
    getFloorItemPattern(entity, scaleLevel) {
        const char = entity.char || '?';

        // 시체는 특별한 패턴
        if (entity.isCorpse) {
            if (scaleLevel >= 4) {
                return [
                    "  ___  ",
                    " /%%%\\ ",
                    " \\___/ "
                ];
            } else if (scaleLevel >= 3) {
                return [
                    " _%_ ",
                    " \\%/ "
                ];
            } else {
                return ["%"];
            }
        }

        // 일반 아이템은 작은 크기로 표시
        if (scaleLevel >= 4) {
            return [
                ` [${char}] `
            ];
        } else if (scaleLevel >= 3) {
            return [
                `[${char}]`
            ];
        } else {
            return [char];
        }
    }

    dimColor(color, brightness) {
        if (!color.startsWith('#')) return color;
        const hex = color.slice(1);
        let r, g, b;
        if (hex.length === 3) {
            r = parseInt(hex[0] + hex[0], 16);
            g = parseInt(hex[1] + hex[1], 16);
            b = parseInt(hex[2] + hex[2], 16);
        } else {
            r = parseInt(hex.slice(0, 2), 16);
            g = parseInt(hex.slice(2, 4), 16);
            b = parseInt(hex.slice(4, 6), 16);
        }
        return `rgb(${Math.floor(r * brightness)},${Math.floor(g * brightness)},${Math.floor(b * brightness)})`;
    }

    // HTML 렌더링
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

    // 패턴 관련
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
        return (this.entitySizes && this.entitySizes[char]) || this.defaultEntitySize;
    }

    getEntityColor(char) {
        return (this.entityColors && this.entityColors[char]) || '#ff0000';
    }

    getEntityPattern(char, scaleLevel) {
        const patterns = this.asciiScalePatterns[char] || this.asciiScalePatterns['default'];
        return patterns ? (patterns[scaleLevel] || patterns[1]) : null;
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
                } else if (mapX >= 0 && mapX < gameMap[0].length && mapY >= 0 && mapY < gameMap.length) {
                    line += gameMap[mapY][mapX];
                } else {
                    line += ' ';
                }
            }
            lines.push(line);
        }
        return lines.join('\n');
    }

    get playerAngle() {
        const angles = { 'N': -Math.PI/2, 'S': Math.PI/2, 'E': 0, 'W': Math.PI };
        return angles[this.facing] || 0;
    }
}

class Compass {
    constructor() {
        this.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    }
    render(angle) {
        let normalized = angle + Math.PI / 2;
        while (normalized < 0) normalized += 2 * Math.PI;
        while (normalized >= 2 * Math.PI) normalized -= 2 * Math.PI;
        const index = Math.round(normalized / (Math.PI / 4)) % 8;
        return `    N\n  W + E  [${this.directions[index]}]\n    S`;
    }
}

window.ASCII3DRenderer = ASCII3DRenderer;
window.Compass = Compass;
