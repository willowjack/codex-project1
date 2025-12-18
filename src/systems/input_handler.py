"""
입력 핸들러
키보드 입력 처리 및 액션 매핑
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple, Dict, Any
import tcod.event

if TYPE_CHECKING:
    from systems.engine import Engine


# =============================================================================
# 키 바인딩 (Nethack/Vi 스타일 + 화살표)
# =============================================================================

# 이동 키 매핑
MOVE_KEYS = {
    # Vi 키 (Nethack 스타일)
    tcod.event.KeySym.h: (-1, 0),   # 왼쪽
    tcod.event.KeySym.j: (0, 1),    # 아래
    tcod.event.KeySym.k: (0, -1),   # 위
    tcod.event.KeySym.l: (1, 0),    # 오른쪽
    tcod.event.KeySym.y: (-1, -1),  # 왼쪽 위 (대각선)
    tcod.event.KeySym.u: (1, -1),   # 오른쪽 위
    tcod.event.KeySym.b: (-1, 1),   # 왼쪽 아래
    tcod.event.KeySym.n: (1, 1),    # 오른쪽 아래

    # 화살표 키
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),

    # 넘패드
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
}

# 대기 키 (제자리)
WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,  # .
    tcod.event.KeySym.KP_5,    # 넘패드 5
    tcod.event.KeySym.s,       # s (stay)
}


class Action:
    """액션 기본 클래스"""
    pass


class MoveAction(Action):
    """이동 액션"""
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy


class WaitAction(Action):
    """대기 액션"""
    pass


class PickupAction(Action):
    """아이템 줍기 액션"""
    pass


class InventoryAction(Action):
    """인벤토리 열기 액션"""
    pass


class UseItemAction(Action):
    """아이템 사용 액션"""
    def __init__(self, index: int):
        self.index = index


class DropItemAction(Action):
    """아이템 버리기 액션"""
    def __init__(self, index: int):
        self.index = index


class LookAction(Action):
    """둘러보기 모드"""
    pass


class QuitAction(Action):
    """게임 종료 액션"""
    pass


class EscapeAction(Action):
    """ESC (메뉴 닫기 등)"""
    pass


class RestAction(Action):
    """휴식 액션"""
    pass


def handle_main_game_input(event: tcod.event.KeyDown) -> Optional[Action]:
    """
    메인 게임 입력 처리

    Args:
        event: 키보드 이벤트

    Returns:
        액션 또는 None
    """
    key = event.sym
    mod = event.mod

    # 이동 키
    if key in MOVE_KEYS:
        dx, dy = MOVE_KEYS[key]
        return MoveAction(dx, dy)

    # 대기
    if key in WAIT_KEYS:
        return WaitAction()

    # 아이템 줍기
    if key == tcod.event.KeySym.g or key == tcod.event.KeySym.COMMA:
        return PickupAction()

    # 인벤토리
    if key == tcod.event.KeySym.i:
        return InventoryAction()

    # 둘러보기
    if key == tcod.event.KeySym.x:
        return LookAction()

    # 휴식
    if key == tcod.event.KeySym.r:
        return RestAction()

    # ESC
    if key == tcod.event.KeySym.ESCAPE:
        return EscapeAction()

    # 종료 (Ctrl+Q)
    if key == tcod.event.KeySym.q and mod & tcod.event.KMOD_CTRL:
        return QuitAction()

    return None


def handle_inventory_input(event: tcod.event.KeyDown) -> Optional[Action]:
    """
    인벤토리 화면 입력 처리

    Args:
        event: 키보드 이벤트

    Returns:
        액션 또는 None
    """
    key = event.sym
    mod = event.mod

    # ESC로 닫기
    if key == tcod.event.KeySym.ESCAPE:
        return EscapeAction()

    # a-z로 아이템 선택
    index = key - tcod.event.KeySym.a
    if 0 <= index <= 25:
        if mod & tcod.event.KMOD_SHIFT:
            # Shift+문자 = 버리기
            return DropItemAction(index)
        else:
            # 그냥 문자 = 사용
            return UseItemAction(index)

    return None


def handle_dead_input(event: tcod.event.KeyDown) -> Optional[Action]:
    """사망 시 입력 처리"""
    key = event.sym

    if key == tcod.event.KeySym.ESCAPE or key == tcod.event.KeySym.q:
        return QuitAction()

    return None


def handle_look_input(event: tcod.event.KeyDown) -> Optional[Action]:
    """둘러보기 모드 입력 처리"""
    key = event.sym

    if key == tcod.event.KeySym.ESCAPE or key == tcod.event.KeySym.x:
        return EscapeAction()

    # 이동 키 (커서 이동용)
    if key in MOVE_KEYS:
        dx, dy = MOVE_KEYS[key]
        return MoveAction(dx, dy)

    return None
