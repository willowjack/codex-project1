# 세션 히스토리 - Claude Code 작업 기록

> **목적**: 새 세션에서 컨텍스트를 빠르게 파악하기 위한 문서

---

## 프로젝트 개요

**ASCII 로그라이크 생존 게임** - Nethack, Stone Soup, Unreal World 스타일
- **GitHub**: `willowjack/codex-project1`
- **배포 URL**: `https://willowjack.github.io/codex-project1/`

### 기술 스택
- Python 백엔드: `src/` (터미널 버전)
- 웹 프론트엔드: `web/` (JavaScript + HTML5)
- 3D 뷰: Eye of the Beholder 스타일 ASCII 렌더링

---

## 핵심 파일 구조

```
web/
├── index.html          # 메인 게임
├── game.js             # 게임 로직 (~1600줄)
├── view3d.js           # 3D ASCII 렌더러
├── style.css           # 스타일시트
├── monster_patterns.js # 몬스터 ASCII 아트 + 기본 정보
├── item_patterns.js    # 아이템 ASCII 아트 + 상세 데이터
├── weapons.js          # 무기 데이터
├── pattern_editor.html # 몬스터 에디터
├── item_editor.html    # 아이템 에디터
└── quest_editor.html   # 퀘스트 에디터

.github/workflows/
├── auto-create-pr.yml  # claude/ 브랜치 푸시 → 자동 PR 생성
├── auto-merge.yml      # claude/ PR 자동 머지
└── deploy-pages.yml    # main 푸시 → GitHub Pages 배포
```

---

## 자동화 워크플로우

### 완전 자동화 흐름 (목표)
```
claude/xxx 브랜치에 푸시
        ↓
[자동] PR 생성 (auto-create-pr.yml)
        ↓
[자동] PR 머지 (auto-merge.yml)
        ↓
[자동] GitHub Pages 배포 (deploy-pages.yml)
```

### 현재 이슈
- GitHub Pages 배포가 자동 트리거 안됨
- **해결법**: Repository Settings → Pages → Source를 "GitHub Actions"로 설정 필요
- 또는 Actions 탭에서 "Deploy to GitHub Pages" 수동 실행

---

## 구현된 기능

### 게임 기능
- [x] 턴제 로그라이크 시스템
- [x] 9방향 이동 (대각선 포함)
- [x] 플레이어 방향 화살표 표시 (▲▼◀▶◤◥◣◢)
- [x] 3D 던전 뷰 (Eye of the Beholder 스타일)
- [x] 층별 몬스터 출현 시스템
- [x] NPC, 퀘스트, 종교, 경제 시스템
- [x] 생존 시스템 (배고픔, 갈증, 체온)
- [x] 저장/불러오기

### 에디터 기능
- [x] 몬스터 패턴 에디터 (pattern_editor.html)
  - 5단계 크기별 ASCII 아트 편집
  - localStorage 저장
  - 전체 내보내기 (클립보드)
- [x] 아이템 에디터 (item_editor.html)
  - ASCII 아트 편집
  - 아이템 데이터 편집 (가격, 무게, 효과 등)
  - **코드 가져오기/내보내기 기능**
- [x] 퀘스트 에디터 (quest_editor.html)

### 모바일 UI
- [x] 반응형 레이아웃
- [x] 9방향 터치 키패드
- [x] 상태창/메시지 통합 영역

---

## 미완성/누락된 기능

### 몬스터 에디터 (pattern_editor.html)
- [ ] 코드 가져오기 기능 (item_editor처럼)
- [ ] 몬스터 스탯 편집 (HP, 공격력, 방어력, 경험치)
- [ ] 드롭 아이템 설정
- [ ] 특수 능력 설정

### 몬스터 데이터 (monster_patterns.js)
현재 구조:
```javascript
'g': {
    name: '고블린',
    color: '#3f7f3f',
    size: { height: 1.0, width: 1.0, weight: 1.0 },
    patterns: { ... }
}
```

필요한 구조 (item_patterns.js 참고):
```javascript
'g': {
    name: '고블린',
    color: '#3f7f3f',
    size: { height: 1.0, width: 1.0, weight: 1.0 },
    monsterData: {
        hp: 10,
        attack: 3,
        defense: 1,
        exp: 5,
        drops: ['%', '!'],  // 음식, 음료
        abilities: []
    },
    patterns: { ... }
}
```

---

## 최근 작업 내역

### 2024-12-21
1. 삭제된 파일 복구:
   - `web/item_editor.html`
   - `web/item_patterns.js`
   - `web/quest_editor.html`

2. 플레이어 방향 화살표 구현 (`web/game.js:1458-1472`)

3. 3D 뷰 CSS 수정 (`web/style.css`):
   - `scaleY(1.1)` 추가
   - `letter-spacing: 0.5px` 추가

4. GitHub Actions 워크플로우:
   - `auto-create-pr.yml` 추가 (자동 PR 생성)

---

## 주의사항

### Git 브랜치 규칙
- 개발: `claude/xxx` 브랜치 사용
- main 직접 푸시 불가 (branch protection)
- PR 생성 후 자동 머지됨

### CSS 주의점
- 모바일: `@media (max-width: 900px)`
- 3D 뷰 비율: `scaleY(1.1)` 필요 (ASCII 문자 비율 보정)

### 파일 복구 방법
```bash
# 삭제된 파일 복구
git checkout <commit-hash> -- <file-path>

# 예: 아이템 에디터 복구
git checkout 0589721 -- web/item_editor.html
```

---

## 다음 작업 TODO

1. [ ] 몬스터 에디터에 코드 가져오기 기능 추가
2. [ ] monster_patterns.js에 monsterData 추가
3. [ ] GitHub Pages 배포 확인 (Settings → Pages)
4. [ ] 모바일에서 기능 테스트

---

## 유용한 커밋 해시

| 커밋 | 설명 |
|------|------|
| `0589721` | 아이템 에디터/패턴 완성 버전 |
| `788c2a2` | 아이템 에디터에 모든 데이터 추가 |
| `ea3f787` | 몬스터 패턴 에디터 최초 추가 |
| `3f4c08d` | 층별 몬스터 출현 시스템 |

---

*마지막 업데이트: 2024-12-21*
