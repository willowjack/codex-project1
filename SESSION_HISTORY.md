# 세션 히스토리 - Claude Code 작업 기록

> **목적**: 새 세션에서 컨텍스트를 빠르게 파악하기 위한 문서

---

## 프로젝트 개요

**ASCII 로그라이크 생존 게임** - Nethack, Stone Soup, Unreal World 스타일
- **GitHub**: `willowjack/codex-project1`
- **배포 URL**: `https://willowjack.github.io/codex-project1/`
- **에디터 URL**:
  - 몬스터: `https://willowjack.github.io/codex-project1/pattern_editor.html`
  - 아이템: `https://willowjack.github.io/codex-project1/item_editor.html`
  - 퀘스트: `https://willowjack.github.io/codex-project1/quest_editor.html`

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
├── auto-create-pr.yml  # PR 생성 + 머지 + 충돌 자동 해결
└── deploy-pages.yml    # workflow_run으로 자동 배포
```

---

## 🚀 GitHub 자동화 (완전 해결됨)

### 자동화 흐름 (2025-12-21 최종)
```
claude/* 브랜치에 푸시
        ↓
[Auto Merge Logic] (auto-create-pr.yml)
  1. 체크아웃
  2. main과 충돌 자동 해결 (-X ours)
  3. PR 생성
  4. PR 머지 (squash)
        ↓ (workflow_run 트리거)
[Deploy to Pages] (deploy-pages.yml)
  - main 브랜치에서 GitHub Pages 배포
```

### ⚠️ 필수 GitHub 설정

| 설정 위치 | 설정 항목 | 필요 값 |
|-----------|-----------|---------|
| Settings → Actions → General | Workflow permissions | **Read and write permissions** |
| Settings → Actions → General | Allow GitHub Actions to create and approve pull requests | ✅ **체크** |
| Settings → Pages → Source | Build and deployment | **GitHub Actions** |

### 핵심 해결책 (중요!)

**문제 1: GITHUB_TOKEN이 다른 워크플로우 트리거 안 함**
- 원인: GitHub 보안 정책 (의도된 동작)
- 해결: `workflow_run` 트리거 사용
  - `workflow_run`은 GITHUB_TOKEN 제한을 받지 않는 시스템 이벤트
  - `workflow_run`은 main 브랜치 컨텍스트에서 실행 → 환경 보호 규칙 통과

**문제 2: 환경 보호 규칙 (Branch protection)**
- 원인: `github-pages` 환경이 main 브랜치에서만 배포 허용
- 해결: `workflow_run`은 main 컨텍스트에서 실행되므로 자동 통과

**문제 3: 머지 충돌**
- 원인: 브랜치가 main에서 분기된 후 main이 변경됨
- 해결: PR 생성 전에 `git merge origin/main -X ours`로 자동 해결
  - `-X ours`: 충돌 시 현재 브랜치(claude) 우선

### 워크플로우 파일

**auto-create-pr.yml** (핵심):
```yaml
name: Auto Merge Logic  # 이 이름이 deploy-pages.yml의 workflow_run과 일치해야 함

on:
  push:
    branches:
      - 'claude/**'

jobs:
  create-and-merge:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # 충돌 자동 해결
      - name: Resolve Conflicts (Force Ours)
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git fetch origin main
          git merge origin/main -X ours --no-edit || true
          git push origin HEAD:${{ github.ref_name }}

      - name: Create PR
        run: |
          gh pr create --title "$(git log -1 --pretty=%s)" --body "Auto PR" --base main --head "${{ github.ref_name }}" || true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Merge PR
        run: |
          sleep 3
          gh pr merge --squash --delete-branch
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**deploy-pages.yml**:
```yaml
name: Deploy to Pages

on:
  workflow_run:
    workflows: ["Auto Merge Logic"]  # auto-create-pr.yml의 name과 정확히 일치
    types:
      - completed
  workflow_dispatch:

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages

    steps:
      - uses: actions/checkout@v4
        with:
          ref: main  # 반드시 main 체크아웃

      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: './web'
      - uses: actions/deploy-pages@v4
```

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
  - 네비게이션 바 (에디터 간 이동)
  - localStorage 저장
  - 전체 내보내기 (클립보드)
- [x] 아이템 에디터 (item_editor.html)
  - ASCII 아트 편집
  - 아이템 데이터 편집 (가격, 무게, 효과 등)
  - 코드 가져오기/내보내기 기능
- [x] 퀘스트 에디터 (quest_editor.html)

### 모바일 UI
- [x] 반응형 레이아웃
- [x] 9방향 터치 키패드
- [x] 상태창/메시지 통합 영역

---

## 다음 작업 TODO

1. [x] ~~GitHub 자동화 완성~~ ✅
2. [x] ~~몬스터 에디터에 네비게이션 바 추가~~ ✅
3. [x] ~~item_patterns.js 스크립트 로딩 추가~~ ✅
4. [ ] monster_patterns.js에 monsterData 추가 (game.js와 연동)
5. [ ] 모바일에서 기능 테스트
6. [ ] 더 많은 몬스터 ASCII 아트 추가
7. [ ] 야외 맵 (숲, 눈 지형) 구현

---

## 주의사항

### Git 브랜치 규칙
- 개발: `claude/xxx` 브랜치 사용
- 푸시하면 자동으로 PR 생성 → 머지 → 배포
- main 직접 푸시 불필요

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

## 유용한 커밋 해시

| 커밋 | 설명 |
|------|------|
| `d122552` | 충돌 자동 해결 + workflow_run 완성 |
| `0589721` | 아이템 에디터/패턴 완성 버전 |
| `788c2a2` | 아이템 에디터에 모든 데이터 추가 |
| `ea3f787` | 몬스터 패턴 에디터 최초 추가 |
| `3f4c08d` | 층별 몬스터 출현 시스템 |

---

*마지막 업데이트: 2025-12-21*
