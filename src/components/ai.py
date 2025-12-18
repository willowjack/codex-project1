"""
AI 컴포넌트
몬스터와 NPC의 인공지능 행동 시스템
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple, Optional
import random

if TYPE_CHECKING:
    from components.entity import Actor
    from systems.game_map import GameMap


class BaseAI:
    """AI 기본 클래스"""

    def __init__(self):
        self.entity: Actor = None  # type: ignore

    def perform(self, game_map: GameMap, target: Actor) -> Optional[Tuple[int, int]]:
        """
        AI 행동 수행

        Args:
            game_map: 현재 게임 맵
            target: 추적 대상 (보통 플레이어)

        Returns:
            이동할 방향 (dx, dy) 또는 None
        """
        raise NotImplementedError()


class HostileAI(BaseAI):
    """
    적대적 AI
    플레이어를 감지하면 추적하고 공격
    """

    def __init__(self, detection_range: int = 8):
        super().__init__()
        self.detection_range = detection_range
        self.path: List[Tuple[int, int]] = []

    def perform(self, game_map: GameMap, target: Actor) -> Optional[Tuple[int, int]]:
        """적대적 행동 수행"""
        if not self.entity or not target:
            return None

        # 대상과의 거리 계산
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # 체비셰프 거리

        # 감지 범위 밖이면 아무것도 안 함
        if distance > self.detection_range:
            return self._wander(game_map)

        # 시야 내에 있는지 확인 (간단한 체크)
        if not game_map.visible[self.entity.x, self.entity.y]:
            # 플레이어가 이 몬스터를 볼 수 없으면, 랜덤 이동
            return self._wander(game_map)

        # 인접해 있으면 공격
        if distance <= 1:
            return (dx, dy)  # 공격 방향

        # 추적 이동 (간단한 직선 추적)
        return self._move_towards(target.x, target.y, game_map)

    def _move_towards(
        self, target_x: int, target_y: int, game_map: GameMap
    ) -> Optional[Tuple[int, int]]:
        """대상을 향해 이동"""
        dx = target_x - self.entity.x
        dy = target_y - self.entity.y

        # 정규화 (-1, 0, 1)
        dx = 0 if dx == 0 else (1 if dx > 0 else -1)
        dy = 0 if dy == 0 else (1 if dy > 0 else -1)

        # 대각선 이동 시도
        new_x = self.entity.x + dx
        new_y = self.entity.y + dy

        if game_map.is_walkable(new_x, new_y):
            return (dx, dy)

        # 대각선이 막혔으면 수평/수직 이동 시도
        if dx != 0 and game_map.is_walkable(self.entity.x + dx, self.entity.y):
            return (dx, 0)
        if dy != 0 and game_map.is_walkable(self.entity.x, self.entity.y + dy):
            return (0, dy)

        return None

    def _wander(self, game_map: GameMap) -> Optional[Tuple[int, int]]:
        """배회 (랜덤 이동)"""
        # 25% 확률로 이동
        if random.random() > 0.25:
            return None

        # 랜덤 방향
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = self.entity.x + dx
            new_y = self.entity.y + dy
            if game_map.is_walkable(new_x, new_y):
                return (dx, dy)

        return None


class PassiveAI(BaseAI):
    """
    수동적 AI
    공격받기 전까지는 공격하지 않음 (동물, 중립 NPC)
    """

    def __init__(self, flee_hp_percent: float = 0.3):
        super().__init__()
        self.is_hostile = False
        self.flee_hp_percent = flee_hp_percent

    def perform(self, game_map: GameMap, target: Actor) -> Optional[Tuple[int, int]]:
        """수동적 행동 수행"""
        if not self.entity:
            return None

        # 체력이 낮으면 도망
        if self.entity.fighter:
            hp_percent = self.entity.fighter.hp / self.entity.fighter.max_hp
            if hp_percent < self.flee_hp_percent:
                return self._flee_from(target, game_map)

        # 적대적 상태가 되면 추적
        if self.is_hostile:
            return self._chase(target, game_map)

        # 평화로운 배회
        return self._peaceful_wander(game_map)

    def _flee_from(
        self, target: Actor, game_map: GameMap
    ) -> Optional[Tuple[int, int]]:
        """대상으로부터 도망"""
        if not target:
            return None

        dx = self.entity.x - target.x
        dy = self.entity.y - target.y

        # 정규화
        dx = 0 if dx == 0 else (1 if dx > 0 else -1)
        dy = 0 if dy == 0 else (1 if dy > 0 else -1)

        new_x = self.entity.x + dx
        new_y = self.entity.y + dy

        if game_map.is_walkable(new_x, new_y):
            return (dx, dy)

        return self._peaceful_wander(game_map)

    def _chase(self, target: Actor, game_map: GameMap) -> Optional[Tuple[int, int]]:
        """대상 추적"""
        if not target:
            return None

        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))

        if distance <= 1:
            return (dx, dy)  # 공격

        # 정규화
        dx = 0 if dx == 0 else (1 if dx > 0 else -1)
        dy = 0 if dy == 0 else (1 if dy > 0 else -1)

        new_x = self.entity.x + dx
        new_y = self.entity.y + dy

        if game_map.is_walkable(new_x, new_y):
            return (dx, dy)

        return None

    def _peaceful_wander(self, game_map: GameMap) -> Optional[Tuple[int, int]]:
        """평화로운 배회"""
        # 10% 확률로 이동
        if random.random() > 0.1:
            return None

        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = self.entity.x + dx
            new_y = self.entity.y + dy
            if game_map.is_walkable(new_x, new_y):
                return (dx, dy)

        return None

    def become_hostile(self) -> None:
        """적대적 상태로 전환"""
        self.is_hostile = True
