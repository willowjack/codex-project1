"""
GameMap 클래스
게임 맵과 엔티티 관리
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Iterator, Tuple
import numpy as np

from systems import tile_types

if TYPE_CHECKING:
    from components.entity import Entity, Actor, Item


class GameMap:
    """
    게임 맵 클래스

    맵 데이터와 엔티티를 관리하고, 시야(FOV) 계산을 담당합니다.

    Attributes:
        width, height: 맵 크기
        tiles: 타일 데이터 배열
        visible: 현재 보이는 타일
        explored: 탐험한 타일
        entities: 맵에 있는 모든 엔티티
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # 타일 배열 초기화 (벽으로 채움)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        # 시야 배열
        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")

        # 엔티티 리스트
        self.entities: List[Entity] = []

        # 아이템 리스트 (바닥에 있는 아이템)
        self.items: List[Item] = []

    def in_bounds(self, x: int, y: int) -> bool:
        """좌표가 맵 범위 내인지 확인"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        """해당 위치로 이동 가능한지 확인"""
        if not self.in_bounds(x, y):
            return False

        # 타일이 이동 가능한지
        if not self.tiles["walkable"][x, y]:
            return False

        # 블로킹 엔티티가 있는지
        if self.get_blocking_entity_at(x, y):
            return False

        return True

    def get_blocking_entity_at(self, x: int, y: int) -> Optional[Entity]:
        """해당 위치의 블로킹 엔티티 반환"""
        for entity in self.entities:
            if entity.blocks_movement and entity.x == x and entity.y == y:
                return entity
        return None

    def get_actor_at(self, x: int, y: int) -> Optional[Actor]:
        """해당 위치의 Actor 반환"""
        for entity in self.entities:
            if hasattr(entity, "fighter") and entity.x == x and entity.y == y:
                return entity  # type: ignore
        return None

    def get_items_at(self, x: int, y: int) -> List[Item]:
        """해당 위치의 아이템 리스트 반환"""
        return [item for item in self.items if item.x == x and item.y == y]

    def add_entity(self, entity: Entity) -> None:
        """엔티티 추가"""
        self.entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        """엔티티 제거"""
        if entity in self.entities:
            self.entities.remove(entity)

    def add_item(self, item: Item) -> None:
        """아이템 추가"""
        self.items.append(item)

    def remove_item(self, item: Item) -> None:
        """아이템 제거"""
        if item in self.items:
            self.items.remove(item)

    @property
    def actors(self) -> Iterator[Actor]:
        """모든 살아있는 Actor 반복자"""
        for entity in self.entities:
            if hasattr(entity, "is_alive") and entity.is_alive:
                yield entity  # type: ignore

    @property
    def visible_tiles(self) -> np.ndarray:
        """현재 보이는 타일 배열"""
        return self.tiles[self.visible]

    def compute_fov(
        self,
        x: int,
        y: int,
        radius: int,
        algorithm: int = 0,
        light_walls: bool = True,
    ) -> None:
        """
        시야(FOV) 계산

        간단한 레이캐스팅 알고리즘 사용

        Args:
            x, y: 시야 중심점
            radius: 시야 반경
            algorithm: 알고리즘 (미사용, 호환성용)
            light_walls: 벽도 밝힐지 여부
        """
        # 모든 타일을 안 보이게 설정
        self.visible[:] = False

        # 중심점은 항상 보임
        self.visible[x, y] = True
        self.explored[x, y] = True

        # 원형 시야 계산 (간단한 레이캐스팅)
        for angle in range(360):
            self._cast_ray(x, y, angle, radius, light_walls)

    def _cast_ray(
        self,
        start_x: int,
        start_y: int,
        angle: int,
        radius: int,
        light_walls: bool,
    ) -> None:
        """레이 캐스팅으로 시야 계산"""
        import math

        # 각도를 라디안으로 변환
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = math.sin(rad)

        x = start_x + 0.5
        y = start_y + 0.5

        for _ in range(radius):
            x += dx
            y += dy

            tile_x = int(x)
            tile_y = int(y)

            if not self.in_bounds(tile_x, tile_y):
                break

            # 거리 체크
            dist = ((tile_x - start_x) ** 2 + (tile_y - start_y) ** 2) ** 0.5
            if dist > radius:
                break

            # 이 타일을 볼 수 있음
            self.visible[tile_x, tile_y] = True
            self.explored[tile_x, tile_y] = True

            # 불투명한 타일이면 레이 중단
            if not self.tiles["transparent"][tile_x, tile_y]:
                break

    def get_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """
        두 점 사이의 경로 계산 (간단한 A* 알고리즘)

        Args:
            start: 시작 위치
            goal: 목표 위치

        Returns:
            경로 좌표 리스트
        """
        import heapq

        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        ]

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                # 경로 재구성
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                if not self.in_bounds(neighbor[0], neighbor[1]):
                    continue

                if not self.tiles["walkable"][neighbor[0], neighbor[1]]:
                    continue

                # 대각선 이동 비용은 약간 더 높음
                move_cost = 1.4 if dx != 0 and dy != 0 else 1.0
                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

        return []  # 경로 없음
