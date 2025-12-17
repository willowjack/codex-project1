"""
렌더러
게임 화면 렌더링 담당
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import tcod

from systems import tile_types
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_HEIGHT, Colors

if TYPE_CHECKING:
    from systems.engine import Engine
    from systems.game_map import GameMap


def render_map(
    console: tcod.console.Console,
    game_map: GameMap,
) -> None:
    """
    맵 렌더링

    Args:
        console: tcod 콘솔
        game_map: 게임 맵
    """
    # 타일 렌더링
    # visible: 밝은 색, explored but not visible: 어두운 색, unexplored: SHROUD
    light = np.select(
        condlist=[game_map.visible, game_map.explored],
        choicelist=[game_map.tiles["fg_light"], game_map.tiles["fg_dark"]],
        default=tile_types.SHROUD["fg_light"],
    )

    # 문자 렌더링
    chars = np.select(
        condlist=[game_map.visible, game_map.explored],
        choicelist=[game_map.tiles["char"], game_map.tiles["char"]],
        default=tile_types.SHROUD["char"],
    )

    # numpy 배열을 콘솔에 직접 그리기
    console.rgb["ch"][:game_map.width, :game_map.height] = np.char.encode(chars, 'utf-8')[:, :, 0]
    console.rgb["fg"][:game_map.width, :game_map.height] = light

    # 아이템 렌더링 (보이는 곳만)
    for item in game_map.items:
        if game_map.visible[item.x, item.y]:
            console.print(
                x=item.x,
                y=item.y,
                string=item.char,
                fg=item.color,
            )

    # 엔티티 렌더링 (보이는 곳만)
    for entity in sorted(game_map.entities, key=lambda e: e.blocks_movement):
        if game_map.visible[entity.x, entity.y]:
            console.print(
                x=entity.x,
                y=entity.y,
                string=entity.char,
                fg=entity.color,
            )


def render_ui(
    console: tcod.console.Console,
    engine: Engine,
) -> None:
    """
    UI 렌더링 (하단 상태바)

    Args:
        console: tcod 콘솔
        engine: 게임 엔진
    """
    # UI 영역 배경
    console.draw_rect(
        x=0,
        y=MAP_HEIGHT,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT - MAP_HEIGHT,
        ch=ord(" "),
        bg=Colors.UI_BG,
    )

    # 구분선
    console.print(
        x=0,
        y=MAP_HEIGHT,
        string="─" * SCREEN_WIDTH,
        fg=(100, 100, 100),
    )

    player = engine.player

    # =========================================================================
    # 1행: 체력바
    # =========================================================================
    y = MAP_HEIGHT + 1

    if player.fighter:
        hp_ratio = player.fighter.hp / player.fighter.max_hp
        bar_width = 20

        # HP 바 배경
        console.draw_rect(
            x=1, y=y, width=bar_width, height=1,
            ch=ord(" "), bg=(50, 0, 0),
        )
        # HP 바 (현재)
        console.draw_rect(
            x=1, y=y, width=int(bar_width * hp_ratio), height=1,
            ch=ord(" "), bg=Colors.HEALTH_BAR,
        )
        console.print(
            x=1, y=y,
            string=f"HP: {player.fighter.hp}/{player.fighter.max_hp}",
            fg=Colors.WHITE,
        )

    # =========================================================================
    # 2행: 생존 상태 (배고픔, 갈증)
    # =========================================================================
    y = MAP_HEIGHT + 2

    if player.survival:
        # 배고픔 바
        hunger_ratio = player.survival.hunger / player.survival.max_hunger
        console.print(
            x=1, y=y,
            string=f"포만: {int(player.survival.hunger_percent):3d}%",
            fg=_get_status_color(hunger_ratio),
        )

        # 갈증 바
        thirst_ratio = player.survival.thirst / player.survival.max_thirst
        console.print(
            x=16, y=y,
            string=f"수분: {int(player.survival.thirst_percent):3d}%",
            fg=_get_status_color(thirst_ratio),
        )

        # 체온
        temp_color = Colors.SAFE
        if player.survival.body_temp < 35 or player.survival.body_temp > 39:
            temp_color = Colors.DANGER
        elif player.survival.body_temp < 36 or player.survival.body_temp > 38:
            temp_color = Colors.WARNING
        console.print(
            x=31, y=y,
            string=f"체온: {player.survival.body_temp:.1f}°C",
            fg=temp_color,
        )

    # =========================================================================
    # 3행: 시간 및 상태
    # =========================================================================
    y = MAP_HEIGHT + 3

    console.print(
        x=1, y=y,
        string=f"{engine.get_time_string()} ({engine.get_time_period()})",
        fg=(200, 200, 100),
    )

    # 턴 카운터
    console.print(
        x=30, y=y,
        string=f"Turn: {engine.turn_count}",
        fg=(150, 150, 150),
    )

    # 위치
    console.print(
        x=50, y=y,
        string=f"({player.x}, {player.y})",
        fg=(150, 150, 150),
    )

    # =========================================================================
    # 4-5행: 메시지 로그
    # =========================================================================
    y = MAP_HEIGHT + 4

    for i, (msg, color) in enumerate(engine.message_log.get_recent(3)):
        # 최신 메시지일수록 밝게
        fade = 1.0 - (i * 0.2)
        faded_color = tuple(int(c * fade) for c in color)
        console.print(
            x=1, y=y + (2 - i),  # 역순으로 출력 (최신이 아래)
            string=msg[:SCREEN_WIDTH - 2],
            fg=faded_color,
        )


def _get_status_color(ratio: float) -> tuple[int, int, int]:
    """비율에 따른 상태 색상"""
    if ratio > 0.5:
        return Colors.SAFE
    elif ratio > 0.2:
        return Colors.WARNING
    else:
        return Colors.DANGER


def render_inventory(
    console: tcod.console.Console,
    engine: Engine,
) -> None:
    """
    인벤토리 화면 렌더링

    Args:
        console: tcod 콘솔
        engine: 게임 엔진
    """
    player = engine.player

    if not player.inventory:
        return

    # 인벤토리 창 크기
    width = 40
    height = len(player.inventory) + 4
    x = SCREEN_WIDTH // 2 - width // 2
    y = SCREEN_HEIGHT // 2 - height // 2

    # 배경
    console.draw_frame(
        x=x, y=y, width=width, height=height,
        title="인벤토리",
        clear=True,
        fg=(255, 255, 255),
        bg=(20, 20, 30),
    )

    # 안내
    console.print(
        x=x + 1, y=y + 1,
        string="[a-z] 사용  [Shift+a-z] 버리기  [ESC] 닫기",
        fg=(150, 150, 150),
    )

    # 아이템 목록
    if len(player.inventory) == 0:
        console.print(
            x=x + 1, y=y + 3,
            string="(비어 있음)",
            fg=(128, 128, 128),
        )
    else:
        for i, item in enumerate(player.inventory):
            key = chr(ord('a') + i)
            console.print(
                x=x + 1, y=y + 3 + i,
                string=f"{key}) ",
                fg=(200, 200, 200),
            )
            console.print(
                x=x + 4, y=y + 3 + i,
                string=item.char,
                fg=item.color,
            )
            console.print(
                x=x + 6, y=y + 3 + i,
                string=item.name,
                fg=(255, 255, 255),
            )


def render_game_over(
    console: tcod.console.Console,
) -> None:
    """
    게임 오버 화면 렌더링
    """
    console.print(
        x=SCREEN_WIDTH // 2 - 10,
        y=SCREEN_HEIGHT // 2,
        string="*** 당신은 죽었다 ***",
        fg=(255, 0, 0),
    )
    console.print(
        x=SCREEN_WIDTH // 2 - 12,
        y=SCREEN_HEIGHT // 2 + 2,
        string="[ESC] 또는 [Q]를 눌러 종료",
        fg=(200, 200, 200),
    )


def render_look_mode(
    console: tcod.console.Console,
    engine: Engine,
    cursor_x: int,
    cursor_y: int,
) -> None:
    """
    둘러보기 모드 렌더링

    Args:
        console: tcod 콘솔
        engine: 게임 엔진
        cursor_x, cursor_y: 커서 위치
    """
    game_map = engine.game_map

    if not game_map:
        return

    # 커서 표시
    console.print(
        x=cursor_x,
        y=cursor_y,
        string="X",
        fg=(255, 255, 0),
    )

    # 해당 위치 정보 표시
    info_y = MAP_HEIGHT + 1

    if game_map.in_bounds(cursor_x, cursor_y):
        if game_map.visible[cursor_x, cursor_y]:
            # 타일 정보
            tile_char = str(game_map.tiles["char"][cursor_x, cursor_y])

            # 엔티티 확인
            actor = game_map.get_actor_at(cursor_x, cursor_y)
            items = game_map.get_items_at(cursor_x, cursor_y)

            console.print(
                x=50, y=info_y,
                string="[둘러보기 모드]",
                fg=(255, 255, 0),
            )

            if actor:
                info = f"{actor.name}"
                if actor.fighter:
                    info += f" (HP: {actor.fighter.hp}/{actor.fighter.max_hp})"
                console.print(x=50, y=info_y + 1, string=info, fg=actor.color)

            if items:
                item_names = ", ".join(item.name for item in items)
                console.print(
                    x=50, y=info_y + 2,
                    string=f"아이템: {item_names}",
                    fg=(200, 200, 255),
                )
        else:
            console.print(
                x=50, y=info_y,
                string="(보이지 않음)",
                fg=(128, 128, 128),
            )


def render_help(console: tcod.console.Console) -> None:
    """도움말 화면 렌더링"""
    help_text = [
        "=== 조작법 ===",
        "",
        "이동: 방향키 / hjkl (Vi키) / 넘패드",
        "대각선: yubn / 넘패드 7,9,1,3",
        "",
        "g, : 아이템 줍기",
        "i   : 인벤토리",
        "x   : 둘러보기",
        "r   : 휴식",
        ".   : 대기",
        "",
        "인벤토리에서:",
        "  a-z       : 아이템 사용",
        "  Shift+a-z : 아이템 버리기",
        "",
        "Ctrl+Q : 게임 종료",
    ]

    width = 40
    height = len(help_text) + 2
    x = SCREEN_WIDTH // 2 - width // 2
    y = SCREEN_HEIGHT // 2 - height // 2

    console.draw_frame(
        x=x, y=y, width=width, height=height,
        title="도움말",
        clear=True,
        fg=(255, 255, 255),
        bg=(20, 20, 30),
    )

    for i, line in enumerate(help_text):
        console.print(
            x=x + 1,
            y=y + 1 + i,
            string=line,
            fg=(200, 200, 200),
        )
