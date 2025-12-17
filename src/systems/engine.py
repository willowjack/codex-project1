"""
게임 엔진
메인 게임 루프, 상태 관리, 턴 처리
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from enum import Enum, auto

if TYPE_CHECKING:
    from components.entity import Actor
    from systems.game_map import GameMap


class GameState(Enum):
    """게임 상태"""
    MAIN_MENU = auto()
    PLAYING = auto()
    PLAYER_DEAD = auto()
    INVENTORY = auto()
    TARGETING = auto()
    LOOK = auto()


class MessageLog:
    """
    게임 메시지 로그
    Nethack 스타일의 메시지 표시
    """

    def __init__(self, max_messages: int = 100):
        self.messages: List[tuple[str, tuple[int, int, int]]] = []
        self.max_messages = max_messages

    def add(self, text: str, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        """메시지 추가"""
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_recent(self, count: int = 5) -> List[tuple[str, tuple[int, int, int]]]:
        """최근 메시지 가져오기"""
        return self.messages[-count:]

    def clear(self) -> None:
        """모든 메시지 삭제"""
        self.messages.clear()


class Engine:
    """
    게임 엔진 클래스

    모든 게임 시스템을 조율하고 관리합니다.

    Attributes:
        player: 플레이어 Actor
        game_map: 현재 게임 맵
        message_log: 메시지 로그
        game_state: 현재 게임 상태
        turn_count: 경과 턴 수
    """

    def __init__(
        self,
        player: Actor,
        game_map: Optional[GameMap] = None,
    ):
        self.player = player
        self.game_map = game_map
        self.message_log = MessageLog()
        self.game_state = GameState.PLAYING
        self.turn_count = 0

        # 시간 시스템
        self.hour = 8  # 오전 8시 시작
        self.day = 1
        self.environment_temp = 20.0  # 기본 환경 온도

    def handle_player_turn(self, dx: int, dy: int) -> bool:
        """
        플레이어 턴 처리

        Args:
            dx, dy: 이동 방향

        Returns:
            턴이 소비되었는지 여부
        """
        if self.game_state != GameState.PLAYING:
            return False

        if not self.game_map:
            return False

        # 새 위치 계산
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # 맵 범위 체크
        if not self.game_map.in_bounds(new_x, new_y):
            self.message_log.add("그쪽으로는 갈 수 없다.", (128, 128, 128))
            return False

        # 이동 가능 체크
        if not self.game_map.tiles["walkable"][new_x, new_y]:
            self.message_log.add("벽이 막고 있다.", (128, 128, 128))
            return False

        # 다른 Actor 체크 (전투 또는 상호작용)
        target = self.game_map.get_actor_at(new_x, new_y)
        if target and target != self.player:
            # 전투!
            return self._handle_melee_attack(target)

        # 이동 실행
        self.player.move(dx, dy)

        # 아이템 체크
        items_here = self.game_map.get_items_at(self.player.x, self.player.y)
        if items_here:
            item_names = ", ".join(item.name for item in items_here)
            self.message_log.add(f"여기에 {item_names}이(가) 있다.")

        return True

    def _handle_melee_attack(self, target: Actor) -> bool:
        """근접 공격 처리"""
        if not self.player.fighter or not target.fighter:
            return False

        damage, is_dead = self.player.fighter.attack(target)

        if damage > 0:
            self.message_log.add(
                f"{target.name}에게 {damage} 데미지를 입혔다!",
                (255, 200, 200),
            )
        else:
            self.message_log.add(
                f"{target.name}을(를) 공격했지만 데미지가 없다.",
                (128, 128, 128),
            )

        if is_dead:
            self.message_log.add(
                f"{target.name}을(를) 처치했다!",
                (255, 255, 0),
            )
            self._kill_entity(target)

        return True

    def _kill_entity(self, entity: Actor) -> None:
        """엔티티 사망 처리"""
        from components.entity import Item
        from config import Symbols

        if entity == self.player:
            self.message_log.add("당신은 죽었다...", (255, 0, 0))
            self.game_state = GameState.PLAYER_DEAD
            entity.char = '%'
            entity.color = (191, 0, 0)
        else:
            # 시체 생성
            corpse = Item(
                x=entity.x,
                y=entity.y,
                char=Symbols.CORPSE,
                color=(128, 0, 0),
                name=f"{entity.name}의 시체",
                consumable=True,
                nutrition=100,  # 시체는 먹을 수 있음 (Nethack 스타일!)
                hydration=20,
            )
            self.game_map.add_item(corpse)
            self.game_map.remove_entity(entity)

    def handle_enemy_turn(self) -> None:
        """적 턴 처리"""
        if not self.game_map:
            return

        for actor in list(self.game_map.actors):
            if actor == self.player:
                continue

            if not actor.ai:
                continue

            # AI 행동 결정
            action = actor.ai.perform(self.game_map, self.player)

            if action is None:
                continue

            dx, dy = action
            new_x = actor.x + dx
            new_y = actor.y + dy

            # 플레이어에게 공격?
            if new_x == self.player.x and new_y == self.player.y:
                self._handle_enemy_attack(actor)
            elif self.game_map.is_walkable(new_x, new_y):
                actor.move(dx, dy)

    def _handle_enemy_attack(self, attacker: Actor) -> None:
        """적의 공격 처리"""
        if not attacker.fighter or not self.player.fighter:
            return

        damage, is_dead = attacker.fighter.attack(self.player)

        if damage > 0:
            self.message_log.add(
                f"{attacker.name}이(가) 당신에게 {damage} 데미지를 입혔다!",
                (255, 100, 100),
            )
        else:
            self.message_log.add(
                f"{attacker.name}이(가) 당신을 공격했지만 막아냈다.",
                (200, 200, 200),
            )

        if is_dead:
            self._kill_entity(self.player)

    def process_turn(self) -> None:
        """
        턴 종료 처리
        생존 시스템, 시간 경과 등
        """
        self.turn_count += 1

        # 시간 경과
        if self.turn_count % 60 == 0:  # 60턴 = 1시간
            self.hour += 1
            if self.hour >= 24:
                self.hour = 0
                self.day += 1
                self.message_log.add(f"Day {self.day}이 밝았다.", (255, 255, 200))

        # 낮/밤에 따른 환경 온도 변화
        if 6 <= self.hour < 20:  # 낮
            self.environment_temp = 22.0
        else:  # 밤
            self.environment_temp = 15.0

        # 플레이어 생존 시스템 처리
        if self.player.survival:
            messages = self.player.survival.process_turn(self.environment_temp)
            for msg in messages:
                self.message_log.add(msg, (255, 200, 0))

            # 굶주림/탈수로 사망
            if self.player.survival.is_starving or self.player.survival.is_dehydrated:
                if self.player.fighter:
                    self.player.fighter.hp -= 1
                    if self.player.fighter.hp <= 0:
                        self._kill_entity(self.player)

    def pickup_item(self) -> bool:
        """아이템 줍기"""
        if not self.game_map or not self.player.inventory:
            return False

        items = self.game_map.get_items_at(self.player.x, self.player.y)

        if not items:
            self.message_log.add("여기에는 아무것도 없다.")
            return False

        item = items[0]  # 첫 번째 아이템만 줍기

        if self.player.inventory.is_full:
            self.message_log.add("인벤토리가 가득 찼다!")
            return False

        self.game_map.remove_item(item)
        self.player.inventory.add(item)
        self.message_log.add(f"{item.name}을(를) 주웠다.", (200, 200, 255))

        return True

    def use_item(self, index: int) -> bool:
        """아이템 사용"""
        if not self.player.inventory:
            return False

        item = self.player.inventory.get_item_at(index)
        if not item:
            return False

        if not item.consumable:
            self.message_log.add(f"{item.name}은(는) 사용할 수 없다.")
            return False

        # 음식/음료 소비
        if item.nutrition > 0 and self.player.survival:
            msg = self.player.survival.eat(item.nutrition)
            self.message_log.add(msg, (0, 255, 0))

        if item.hydration > 0 and self.player.survival:
            msg = self.player.survival.drink(item.hydration)
            self.message_log.add(msg, (0, 200, 255))

        # 치료 물약 (특별 처리)
        if item.name == "치료 물약" and self.player.fighter:
            heal_amount = self.player.fighter.heal(20)
            self.message_log.add(
                f"체력이 {heal_amount} 회복되었다!",
                (0, 255, 0),
            )

        self.player.inventory.remove(item)
        self.message_log.add(f"{item.name}을(를) 사용했다.")

        return True

    def drop_item(self, index: int) -> bool:
        """아이템 버리기"""
        if not self.player.inventory or not self.game_map:
            return False

        item = self.player.inventory.get_item_at(index)
        if not item:
            return False

        self.player.inventory.remove(item)
        item.x = self.player.x
        item.y = self.player.y
        self.game_map.add_item(item)
        self.message_log.add(f"{item.name}을(를) 버렸다.")

        return True

    def update_fov(self) -> None:
        """시야 업데이트"""
        if self.game_map:
            self.game_map.compute_fov(
                self.player.x,
                self.player.y,
                radius=10,
            )

    def get_time_string(self) -> str:
        """현재 시간 문자열"""
        return f"Day {self.day}, {self.hour:02d}:00"

    def get_time_period(self) -> str:
        """시간대 문자열"""
        if 6 <= self.hour < 12:
            return "아침"
        elif 12 <= self.hour < 18:
            return "낮"
        elif 18 <= self.hour < 21:
            return "저녁"
        else:
            return "밤"
