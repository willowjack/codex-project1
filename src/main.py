#!/usr/bin/env python3
"""
ASCII 로그라이크 생존 게임
Nethack + Unreal World 스타일

실행 방법:
    python main.py

조작법:
    방향키/hjkl: 이동
    g: 아이템 줍기
    i: 인벤토리
    x: 둘러보기
    r: 휴식
    .: 대기
    Ctrl+Q: 종료
"""
import sys
import os

# 모듈 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tcod
import tcod.event

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    MAP_WIDTH,
    MAP_HEIGHT,
    ROOM_MIN_SIZE,
    ROOM_MAX_SIZE,
    MAX_ROOMS,
    Colors,
    Symbols,
)
from components.entity import Actor
from components.fighter import Fighter
from components.survival import Survival
from components.inventory import Inventory
from systems.engine import Engine, GameState
from systems.game_map import GameMap
from systems import procgen
from systems import renderer
from systems.input_handler import (
    handle_main_game_input,
    handle_inventory_input,
    handle_dead_input,
    handle_look_input,
    MoveAction,
    WaitAction,
    PickupAction,
    InventoryAction,
    UseItemAction,
    DropItemAction,
    LookAction,
    QuitAction,
    EscapeAction,
    RestAction,
)


def create_player() -> Actor:
    """플레이어 캐릭터 생성"""
    player = Actor(
        x=0,
        y=0,
        char=Symbols.PLAYER,
        color=Colors.PLAYER,
        name="당신",
        fighter=Fighter(hp=30, defense=2, power=5),
        inventory=Inventory(capacity=26),
        survival=Survival(
            max_hunger=1000,
            max_thirst=1000,
            max_stamina=100,
        ),
    )
    return player


def new_game() -> Engine:
    """새 게임 시작"""
    # 플레이어 생성
    player = create_player()

    # 던전 생성
    game_map = procgen.generate_dungeon(
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        player=player,
        max_monsters_per_room=2,
        max_items_per_room=2,
    )

    # 엔진 생성
    engine = Engine(player=player, game_map=game_map)

    # 초기 메시지
    engine.message_log.add(
        "던전에 입장했다. 살아남아야 한다!",
        Colors.YELLOW,
    )
    engine.message_log.add(
        "[?]를 누르면 도움말을 볼 수 있다.",
        (150, 150, 150),
    )

    # 초기 FOV 계산
    engine.update_fov()

    return engine


def main() -> None:
    """메인 함수"""
    # 폰트 설정 (기본 tcod 폰트 사용)
    # 더 나은 한글 지원을 위해서는 한글 폰트가 필요합니다
    tileset = tcod.tileset.load_tilesheet(
        path=tcod.tileset.CHARMAP_CP437,
        columns=16,
        rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
    )

    # 게임 초기화
    engine = new_game()

    # 둘러보기 모드 커서
    look_cursor_x = engine.player.x
    look_cursor_y = engine.player.y
    show_help = False

    # tcod 컨텍스트 생성
    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title="ASCII Roguelike Survival",
        vsync=True,
    ) as context:

        # 루트 콘솔 생성
        root_console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

        # 메인 게임 루프
        while True:
            # 화면 클리어
            root_console.clear()

            # 렌더링
            if engine.game_map:
                renderer.render_map(root_console, engine.game_map)

            renderer.render_ui(root_console, engine)

            # 상태별 추가 렌더링
            if engine.game_state == GameState.PLAYER_DEAD:
                renderer.render_game_over(root_console)
            elif engine.game_state == GameState.INVENTORY:
                renderer.render_inventory(root_console, engine)
            elif engine.game_state == GameState.LOOK:
                renderer.render_look_mode(
                    root_console, engine, look_cursor_x, look_cursor_y
                )

            if show_help:
                renderer.render_help(root_console)

            # 화면 표시
            context.present(root_console)

            # 이벤트 처리
            for event in tcod.event.wait():
                # 창 닫기
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()

                # 키보드 입력
                if not isinstance(event, tcod.event.KeyDown):
                    continue

                # 도움말 토글
                if event.sym == tcod.event.KeySym.QUESTION or (
                    event.sym == tcod.event.KeySym.SLASH
                    and event.mod & tcod.event.KMOD_SHIFT
                ):
                    show_help = not show_help
                    continue

                if show_help:
                    if event.sym == tcod.event.KeySym.ESCAPE:
                        show_help = False
                    continue

                # 상태별 입력 처리
                action = None

                if engine.game_state == GameState.PLAYING:
                    action = handle_main_game_input(event)
                elif engine.game_state == GameState.INVENTORY:
                    action = handle_inventory_input(event)
                elif engine.game_state == GameState.PLAYER_DEAD:
                    action = handle_dead_input(event)
                elif engine.game_state == GameState.LOOK:
                    action = handle_look_input(event)

                if action is None:
                    continue

                # 액션 처리
                turn_consumed = False

                if isinstance(action, QuitAction):
                    raise SystemExit()

                elif isinstance(action, EscapeAction):
                    if engine.game_state == GameState.INVENTORY:
                        engine.game_state = GameState.PLAYING
                    elif engine.game_state == GameState.LOOK:
                        engine.game_state = GameState.PLAYING
                    else:
                        raise SystemExit()

                elif isinstance(action, MoveAction):
                    if engine.game_state == GameState.LOOK:
                        # 둘러보기 모드: 커서 이동
                        new_x = look_cursor_x + action.dx
                        new_y = look_cursor_y + action.dy
                        if engine.game_map and engine.game_map.in_bounds(new_x, new_y):
                            look_cursor_x = new_x
                            look_cursor_y = new_y
                    else:
                        # 일반 모드: 플레이어 이동
                        turn_consumed = engine.handle_player_turn(action.dx, action.dy)

                elif isinstance(action, WaitAction):
                    turn_consumed = True

                elif isinstance(action, PickupAction):
                    turn_consumed = engine.pickup_item()

                elif isinstance(action, InventoryAction):
                    engine.game_state = GameState.INVENTORY

                elif isinstance(action, UseItemAction):
                    turn_consumed = engine.use_item(action.index)
                    if turn_consumed:
                        engine.game_state = GameState.PLAYING

                elif isinstance(action, DropItemAction):
                    turn_consumed = engine.drop_item(action.index)
                    if turn_consumed:
                        engine.game_state = GameState.PLAYING

                elif isinstance(action, LookAction):
                    engine.game_state = GameState.LOOK
                    look_cursor_x = engine.player.x
                    look_cursor_y = engine.player.y

                elif isinstance(action, RestAction):
                    if engine.player.survival:
                        if engine.player.survival.is_resting:
                            msg = engine.player.survival.stop_rest()
                        else:
                            msg = engine.player.survival.rest()
                        engine.message_log.add(msg)
                    turn_consumed = True

                # 턴 처리
                if turn_consumed and engine.game_state == GameState.PLAYING:
                    # 적 턴
                    engine.handle_enemy_turn()

                    # 턴 종료 처리 (생존 시스템 등)
                    engine.process_turn()

                    # FOV 업데이트
                    engine.update_fov()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
