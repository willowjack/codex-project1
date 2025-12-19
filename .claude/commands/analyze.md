# 프로젝트 분석

프로젝트의 구조와 코드를 분석합니다.

## 분석 항목

1. **디렉토리 구조** - 파일 및 폴더 구성
2. **핵심 시스템** - 게임 엔진, 렌더러, 생성기 등
3. **데이터 파일** - 몬스터, 무기, 아이템 정의
4. **설정 파일** - 게임 설정값

## 주요 파일

### Python 백엔드 (src/)
- `main.py` - 게임 진입점
- `config.py` - 설정 상수
- `systems/engine.py` - 게임 엔진
- `systems/procgen.py` - 절차적 생성
- `components/entity.py` - Entity/Actor/Item 클래스

### Web 프론트엔드 (web/)
- `game.js` - 메인 게임 로직
- `view3d.js` - 3D ASCII 렌더러
- `monster_patterns.js` - 몬스터 아트
- `weapons.js` - 무기 데이터
- `pattern_editor.html` - 아트 에디터
