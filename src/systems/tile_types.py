"""
타일 타입 정의
각 타일의 속성과 렌더링 정보
"""
from typing import Tuple
import numpy as np

# 타일 데이터 타입 정의
# (walkable, transparent, char, fg_color_light, fg_color_dark, bg_color_light, bg_color_dark)
tile_dt = np.dtype([
    ("walkable", bool),        # 이동 가능 여부
    ("transparent", bool),     # 시야 통과 여부
    ("char", "U1"),           # 표시 문자 (1 유니코드 문자)
    ("fg_light", "3B"),       # 밝은 곳 전경색 (RGB)
    ("fg_dark", "3B"),        # 어두운 곳 전경색 (RGB)
    ("bg_light", "3B"),       # 밝은 곳 배경색 (RGB)
    ("bg_dark", "3B"),        # 어두운 곳 배경색 (RGB)
])


def new_tile(
    walkable: bool,
    transparent: bool,
    char: str,
    fg_light: Tuple[int, int, int],
    fg_dark: Tuple[int, int, int],
    bg_light: Tuple[int, int, int] = (0, 0, 0),
    bg_dark: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """새로운 타일 생성 헬퍼 함수"""
    return np.array(
        (walkable, transparent, char, fg_light, fg_dark, bg_light, bg_dark),
        dtype=tile_dt,
    )


# =============================================================================
# 기본 지형 타일
# =============================================================================

# SHROUD: 아직 탐험하지 않은 영역 (완전히 검은색)
SHROUD = np.array(
    (False, False, " ", (255, 255, 255), (255, 255, 255), (0, 0, 0), (0, 0, 0)),
    dtype=tile_dt,
)

# 던전 타일
floor = new_tile(
    walkable=True,
    transparent=True,
    char=".",
    fg_light=(200, 180, 50),    # 밝은 바닥
    fg_dark=(50, 50, 150),      # 어두운 바닥
)

wall = new_tile(
    walkable=False,
    transparent=False,
    char="#",
    fg_light=(130, 110, 50),    # 밝은 벽
    fg_dark=(0, 0, 100),        # 어두운 벽
)

# 문
door_closed = new_tile(
    walkable=False,
    transparent=False,
    char="+",
    fg_light=(139, 90, 43),     # 갈색 문
    fg_dark=(69, 45, 21),
)

door_open = new_tile(
    walkable=True,
    transparent=True,
    char="-",
    fg_light=(139, 90, 43),
    fg_dark=(69, 45, 21),
)

# 계단
stairs_down = new_tile(
    walkable=True,
    transparent=True,
    char=">",
    fg_light=(255, 255, 255),
    fg_dark=(100, 100, 100),
)

stairs_up = new_tile(
    walkable=True,
    transparent=True,
    char="<",
    fg_light=(255, 255, 255),
    fg_dark=(100, 100, 100),
)

# =============================================================================
# 야외 타일 (Unreal World 스타일)
# =============================================================================

grass = new_tile(
    walkable=True,
    transparent=True,
    char='"',
    fg_light=(34, 139, 34),     # 초록 풀
    fg_dark=(0, 50, 0),
)

tall_grass = new_tile(
    walkable=True,
    transparent=False,  # 키 큰 풀은 시야 차단
    char='"',
    fg_light=(0, 100, 0),
    fg_dark=(0, 30, 0),
)

tree = new_tile(
    walkable=False,
    transparent=False,
    char="T",
    fg_light=(34, 100, 34),
    fg_dark=(0, 40, 0),
)

water_shallow = new_tile(
    walkable=True,  # 얕은 물은 이동 가능
    transparent=True,
    char="~",
    fg_light=(30, 144, 255),    # 파란 물
    fg_dark=(0, 50, 100),
)

water_deep = new_tile(
    walkable=False,  # 깊은 물은 이동 불가
    transparent=True,
    char="~",
    fg_light=(0, 0, 139),
    fg_dark=(0, 0, 50),
)

# 산/바위
rock = new_tile(
    walkable=False,
    transparent=False,
    char="^",
    fg_light=(128, 128, 128),
    fg_dark=(50, 50, 50),
)

# 모래
sand = new_tile(
    walkable=True,
    transparent=True,
    char=".",
    fg_light=(238, 214, 175),
    fg_dark=(100, 90, 70),
)

# 눈
snow = new_tile(
    walkable=True,
    transparent=True,
    char=".",
    fg_light=(255, 250, 250),
    fg_dark=(150, 150, 160),
)

# =============================================================================
# 특수 타일
# =============================================================================

# 모닥불
campfire = new_tile(
    walkable=False,
    transparent=True,
    char="*",
    fg_light=(255, 100, 0),     # 주황색 불
    fg_dark=(100, 30, 0),
)

# 함정
trap = new_tile(
    walkable=True,
    transparent=True,
    char="^",
    fg_light=(255, 0, 0),       # 빨간 함정 (발견 시)
    fg_dark=(100, 0, 0),
)

# 길/도로
road = new_tile(
    walkable=True,
    transparent=True,
    char=".",
    fg_light=(139, 119, 101),
    fg_dark=(69, 59, 50),
)
