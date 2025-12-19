# Claude Code 프로젝트 가이드

## 자동 커밋/푸시 정책

> **중요**: 이 프로젝트에서는 모든 코드 변경 시 자동으로 커밋과 푸시를 수행합니다.

### 커밋 규칙
- 의미 있는 변경이 완료되면 즉시 커밋
- 커밋 메시지는 한글로 작성 (feat:, fix:, style:, docs:, refactor: 접두사 사용)
- 커밋 후 자동으로 푸시 수행

### 푸시 규칙
- 브랜치명: `claude/` 접두사 사용
- 푸시 실패 시 최대 4회 재시도 (2s, 4s, 8s, 16s 지수 백오프)
- 명령어: `git push -u origin <branch-name>`

---

## 프로젝트 개요

**ASCII 로그라이크 생존 게임** - Nethack, Stone Soup, Unreal World에서 영감을 받은 ASCII 기반 턴제 생존 게임

### 기술 스택
| 구분 | 기술 |
|------|------|
| Python 백엔드 | Python 3 + tcod (터미널 버전) |
| 웹 프론트엔드 | 순수 JavaScript + HTML5 + CSS3 |
| 그래픽 | ASCII 문자 기반, 3D 던전 뷰 |

---

## 디렉토리 구조

```
codex-project1/
├── src/                          # Python 백엔드 (터미널 버전)
│   ├── main.py                   # 게임 진입점
│   ├── config.py                 # 설정 (화면크기, 색상, 심볼)
│   ├── components/               # ECS 컴포넌트
│   │   ├── entity.py             # Entity, Actor, Item 클래스
│   │   ├── fighter.py            # 전투 시스템
│   │   ├── survival.py           # 생존 시스템 (배고픔, 갈증)
│   │   ├── inventory.py          # 인벤토리
│   │   ├── ai.py                 # 몬스터 AI
│   │   ├── npc.py                # NPC 컴포넌트
│   │   └── equipment.py          # 장비 시스템
│   ├── systems/                  # 게임 시스템
│   │   ├── engine.py             # 게임 엔진 (턴 처리, 상태 관리)
│   │   ├── game_map.py           # 맵 관리
│   │   ├── procgen.py            # 절차적 맵 생성
│   │   ├── renderer.py           # 렌더링
│   │   ├── input_handler.py      # 입력 처리
│   │   ├── quest.py              # 퀘스트 시스템
│   │   ├── religion.py           # 종교 시스템
│   │   ├── economy.py            # 경제 시스템
│   │   └── save_load.py          # 저장/불러오기
│   └── data/
│       └── weapons.py            # 무기 데이터
│
├── web/                          # 웹 프론트엔드 버전
│   ├── index.html                # 메인 HTML (게임 UI)
│   ├── game.js                   # 게임 로직 (약 1550줄)
│   ├── view3d.js                 # 3D 던전 뷰 렌더러 (Eye of the Beholder 스타일)
│   ├── monster_patterns.js       # 몬스터 ASCII 아트 패턴 (약 1850줄, 50+ 몬스터)
│   ├── weapons.js                # 무기 데이터 정의
│   ├── pattern_editor.html       # 몬스터 ASCII 아트 에디터 도구
│   └── style.css                 # 스타일시트
│
├── CLAUDE.md                     # 이 파일 - Claude Code 가이드
├── README.md                     # 프로젝트 문서
├── requirements.txt              # Python 의존성
└── LICENSE                       # MIT 라이선스
```

---

## 핵심 시스템 상세

### 1. 게임 엔진 (`src/systems/engine.py`, `web/game.js`)
- **GameState**: PLAYING, INVENTORY, PLAYER_DEAD, LOOK, MAIN_MENU
- **턴 처리**: 플레이어 행동 → 적 행동 → 생존 시스템 → FOV 업데이트
- **MessageLog**: Nethack 스타일 메시지 로그

### 2. 절차적 생성 (`src/systems/procgen.py`)
- **던전 생성**: 랜덤 방 배치 + L자 터널 연결
- **야외 맵 생성**: 바이옴별 지형 (forest, snow)
- **엔티티 배치**: 방당 최대 몬스터/아이템 수 제한

### 3. 3D ASCII 렌더러 (`web/view3d.js`)
- **ASCII3DRenderer 클래스**: Eye of the Beholder 스타일 1인칭 뷰
- **깊이별 뷰포트**: maxDepth=4, 거리에 따른 원근감
- **벽 렌더링**: 정면(밝음) vs 측면(어두움) 대비로 입체감
- **엔티티 스케일링**: 거리별 5단계 패턴 (가까움→멀리)

### 4. 몬스터 패턴 (`web/monster_patterns.js`)
50개 이상의 몬스터 ASCII 아트 정의:
- **인간형**: g(고블린), o(오크), T(트롤), V(뱀파이어), L(리치), K(기사), M(마법사)
- **야수**: r(쥐), b(박쥐), w(늑대), B(곰), S(뱀), x(거미)
- **신화 생물**: D(드래곤), U(유니콘), P(페가수스), F(불사조), G(그리폰)
- **정령**: h(유령), R(레이스), e(불 정령), E(물 정령)
- **슬라임**: j(슬라임), J(젤리)
- **언데드**: s(해골), Z(좀비), Y(미라), u(구울)
- **곤충**: a(거대 개미), z(벌)
- **특수**: @(NPC), $(상인), ?(미믹), I(비홀더), c(젤라틴 큐브)

### 5. 무기 시스템 (`web/weapons.js`)
- **근접 무기**: dagger, short_sword, long_sword, steel_sword, battle_axe, mace, spear
- **원거리 무기**: short_bow, long_bow, crossbow, throwing_knife
- **마법 무기**: apprentice_staff, fire_staff, ice_staff, lightning_staff, enchanted_sword, holy_sword
- **특수 효과**: undead_bane, armor_pierce, stun, reach, burn, freeze, chain, holy

### 6. 패턴 에디터 (`web/pattern_editor.html`)
몬스터 ASCII 아트를 시각적으로 편집하는 도구:
- **그리드 편집**: 크기별(1-5단계) 패턴 편집
- **도구**: 그리기, 지우기, 채우기, 좌우 반전
- **팔레트**: 블록(█▓▒░), 반블록(▄▀▌▐), 삼각형(▲▼◀▶), 눈(◕◔●○), 도형(◈◇★☆) 등
- **내보내기**: 개별 몬스터 코드 복사 / 전체 코드 내보내기
- **저장**: localStorage에 패턴 저장

### 7. 생존 시스템
- **포만감**: 턴당 1 감소, 0이 되면 체력 감소
- **수분**: 턴당 2 감소 (물이 더 급함), 0이 되면 체력 감소
- **체온**: 환경 온도에 따라 변화 (낮 22도, 밤 15도)

### 8. 경제/상점 시스템
- **골드**: 플레이어 자원
- **상점**: NPC 상인과 거래 (구매/판매)
- **아이템 가격**: ITEM_PRICES 객체에 정의

### 9. 퀘스트 시스템
- **Quest 클래스**: id, name, description, objectives, rewards, status
- **QuestLog**: active/completed 퀘스트 관리
- **목표 타입**: kill (처치 퀘스트)

### 10. 종교 시스템
- **4개의 신**: 솔라리우스(빛), 그롬마쉬(전쟁), 실바나(자연), 모르티스(죽음)
- **은총(favor)**: -100 ~ 100, 레벨에 따라 기도 성공률 변화
- **기도**: 300턴 쿨다운, 성공 시 체력 회복

---

## 조작법

```
이동: 방향키, hjkl (Vi 스타일), yubn (대각선), 넘패드
줍기: g 또는 ,
인벤토리: i
대기: . 또는 5
휴식: r
NPC 대화: t
기도: p
퀘스트: q
저장: S
불러오기: L
뷰 전환: v
도움말: ?
종료: ESC 또는 Ctrl+Q
```

---

## 개발 시 참고사항

### 코드 스타일
- Python: PEP 8 준수
- JavaScript: 클래스 기반 OOP, ES6+ 문법
- 한글 주석 및 문자열 사용

### 아키텍처 패턴
- **ECS (Entity-Component-System)**: Entity, Actor, Item + 컴포넌트 분리
- **게임 루프**: 턴 기반, 이벤트 드리븐
- **상태 머신**: GameState enum으로 게임 상태 관리

### 테스트
- Python: `cd src && python main.py`
- Web: `index.html`을 브라우저에서 열기
- 에디터: `pattern_editor.html`을 브라우저에서 열기

---

## 향후 계획
- [ ] 야외 맵 (숲, 눈 지형)
- [ ] 크래프팅 시스템
- [ ] 날씨 시스템
- [ ] 더 많은 몬스터와 아이템
- [ ] 스킬 시스템
