"""
절차적 맵 생성기 (Procedural Generation)
로그라이크의 핵심: 매번 다른 던전/맵 생성
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple, Iterator
import random

from systems.game_map import GameMap
from systems import tile_types

if TYPE_CHECKING:
    from components.entity import Actor, Item


class RectangularRoom:
    """
    사각형 방 클래스

    던전의 기본 구성요소
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        """방의 중심점"""
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """방 내부 영역 (벽 제외)"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """다른 방과 겹치는지 확인"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """
    두 점 사이에 L자형 터널 생성

    Args:
        start: 시작점
        end: 끝점

    Yields:
        터널을 구성하는 좌표들
    """
    x1, y1 = start
    x2, y2 = end

    # 50% 확률로 먼저 수평/수직 이동 결정
    if random.random() < 0.5:
        # 먼저 수평 이동, 그 다음 수직
        corner_x, corner_y = x2, y1
    else:
        # 먼저 수직 이동, 그 다음 수평
        corner_x, corner_y = x1, y2

    # 시작점에서 코너까지
    for x in range(min(x1, corner_x), max(x1, corner_x) + 1):
        yield x, y1

    # 코너에서 끝점까지
    for y in range(min(y1, corner_y), max(y1, corner_y) + 1):
        yield corner_x, y

    # 코너에서 끝점까지 (나머지)
    for x in range(min(corner_x, x2), max(corner_x, x2) + 1):
        yield x, corner_y

    for y in range(min(corner_y, y2), max(corner_y, y2) + 1):
        yield x2, y


def generate_dungeon(
    map_width: int,
    map_height: int,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    player: Actor,
    max_monsters_per_room: int = 2,
    max_items_per_room: int = 2,
) -> GameMap:
    """
    절차적 던전 생성

    BSP(Binary Space Partitioning) 대신 간단한
    랜덤 방 배치 알고리즘 사용 (초보자 친화적)

    Args:
        map_width, map_height: 맵 크기
        max_rooms: 최대 방 개수
        room_min_size, room_max_size: 방 크기 범위
        player: 플레이어 엔티티
        max_monsters_per_room: 방당 최대 몬스터 수
        max_items_per_room: 방당 최대 아이템 수

    Returns:
        생성된 GameMap
    """
    dungeon = GameMap(map_width, map_height)
    rooms: List[RectangularRoom] = []

    for _ in range(max_rooms):
        # 랜덤 방 크기
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        # 랜덤 위치 (맵 경계 안에)
        x = random.randint(0, map_width - room_width - 1)
        y = random.randint(0, map_height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        # 다른 방과 겹치는지 확인
        if any(new_room.intersects(other) for other in rooms):
            continue  # 겹치면 스킵

        # 방 파기 (벽을 바닥으로)
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # 첫 번째 방: 플레이어 배치
            player.x, player.y = new_room.center
        else:
            # 이전 방과 터널로 연결
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

            # 몬스터와 아이템 배치
            place_entities(
                new_room, dungeon, max_monsters_per_room, max_items_per_room
            )

        rooms.append(new_room)

    # 마지막 방에 계단 배치
    if rooms:
        stairs_x, stairs_y = rooms[-1].center
        dungeon.tiles[stairs_x, stairs_y] = tile_types.stairs_down

    # 플레이어 추가
    dungeon.add_entity(player)

    return dungeon


def place_entities(
    room: RectangularRoom,
    dungeon: GameMap,
    max_monsters: int,
    max_items: int,
) -> None:
    """
    방에 몬스터와 아이템 배치

    Args:
        room: 방 객체
        dungeon: 게임 맵
        max_monsters: 최대 몬스터 수
        max_items: 최대 아이템 수
    """
    from components.entity import Actor, Item
    from components.fighter import Fighter
    from components.ai import HostileAI
    from config import Colors, Symbols

    # 몬스터 배치
    num_monsters = random.randint(0, max_monsters)

    for _ in range(num_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        # 해당 위치에 이미 엔티티가 있으면 스킵
        if any(e.x == x and e.y == y for e in dungeon.entities):
            continue

        # 80% 고블린, 20% 오크
        if random.random() < 0.8:
            monster = Actor(
                x=x,
                y=y,
                char=Symbols.GOBLIN,
                color=(63, 127, 63),
                name="고블린",
                ai=HostileAI(detection_range=6),
                fighter=Fighter(hp=10, defense=0, power=3),
            )
        else:
            monster = Actor(
                x=x,
                y=y,
                char=Symbols.ORC,
                color=(0, 127, 0),
                name="오크",
                ai=HostileAI(detection_range=8),
                fighter=Fighter(hp=16, defense=1, power=4),
            )

        dungeon.add_entity(monster)

    # 아이템 배치
    num_items = random.randint(0, max_items)

    for _ in range(num_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        # 해당 위치에 이미 아이템이 있으면 스킵
        if any(i.x == x and i.y == y for i in dungeon.items):
            continue

        # 랜덤 아이템
        roll = random.random()
        if roll < 0.5:
            # 음식
            item = Item(
                x=x,
                y=y,
                char=Symbols.FOOD,
                color=(0, 200, 0),
                name="마른 고기",
                consumable=True,
                nutrition=200,
                hydration=0,
            )
        elif roll < 0.8:
            # 물병
            item = Item(
                x=x,
                y=y,
                char='!',
                color=(0, 150, 255),
                name="물병",
                consumable=True,
                nutrition=0,
                hydration=300,
            )
        else:
            # 체력 물약
            item = Item(
                x=x,
                y=y,
                char=Symbols.POTION,
                color=(255, 0, 0),
                name="치료 물약",
                consumable=True,
                nutrition=0,
                hydration=0,
            )

        dungeon.add_item(item)


# =============================================================================
# 야외 맵 생성 (Unreal World 스타일)
# =============================================================================

def generate_wilderness(
    map_width: int,
    map_height: int,
    player: Actor,
    biome: str = "forest",
) -> GameMap:
    """
    야외 맵 생성

    Args:
        map_width, map_height: 맵 크기
        player: 플레이어 엔티티
        biome: 바이옴 타입 (forest, plains, snow)

    Returns:
        생성된 GameMap
    """
    from components.entity import Actor, Item
    from components.fighter import Fighter
    from components.ai import PassiveAI
    from config import Symbols

    world = GameMap(map_width, map_height)

    # 기본 타일로 채우기
    if biome == "forest":
        base_tile = tile_types.grass
    elif biome == "snow":
        base_tile = tile_types.snow
    else:
        base_tile = tile_types.grass

    world.tiles[:] = base_tile

    # 노이즈 기반 지형 생성 (간단한 버전)
    for x in range(map_width):
        for y in range(map_height):
            roll = random.random()

            if biome == "forest":
                if roll < 0.15:
                    world.tiles[x, y] = tile_types.tree
                elif roll < 0.20:
                    world.tiles[x, y] = tile_types.tall_grass
                elif roll < 0.22:
                    world.tiles[x, y] = tile_types.water_shallow
            elif biome == "snow":
                if roll < 0.05:
                    world.tiles[x, y] = tile_types.tree
                elif roll < 0.08:
                    world.tiles[x, y] = tile_types.rock

    # 플레이어 시작 위치 찾기 (이동 가능한 곳)
    while True:
        x = random.randint(5, map_width - 5)
        y = random.randint(5, map_height - 5)
        if world.tiles["walkable"][x, y]:
            player.x, player.y = x, y
            break

    world.add_entity(player)

    # 동물 배치
    num_animals = random.randint(3, 8)
    for _ in range(num_animals):
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)

        if not world.tiles["walkable"][x, y]:
            continue

        # 토끼, 사슴, 늑대 등
        roll = random.random()
        if roll < 0.5:
            animal = Actor(
                x=x,
                y=y,
                char='r',
                color=(150, 100, 50),
                name="토끼",
                ai=PassiveAI(flee_hp_percent=0.5),
                fighter=Fighter(hp=5, defense=0, power=0),
            )
        elif roll < 0.8:
            animal = Actor(
                x=x,
                y=y,
                char='d',
                color=(139, 90, 43),
                name="사슴",
                ai=PassiveAI(flee_hp_percent=0.3),
                fighter=Fighter(hp=15, defense=0, power=2),
            )
        else:
            animal = Actor(
                x=x,
                y=y,
                char=Symbols.WOLF,
                color=(128, 128, 128),
                name="늑대",
                ai=PassiveAI(flee_hp_percent=0.2),
                fighter=Fighter(hp=20, defense=1, power=5),
            )
            animal.ai.is_hostile = True  # 늑대는 적대적

        world.add_entity(animal)

    # 자원 배치 (베리, 약초 등)
    num_resources = random.randint(5, 15)
    for _ in range(num_resources):
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)

        if not world.tiles["walkable"][x, y]:
            continue

        if random.random() < 0.6:
            item = Item(
                x=x,
                y=y,
                char=Symbols.HERB,
                color=(100, 200, 100),
                name="야생 베리",
                consumable=True,
                nutrition=50,
                hydration=30,
            )
        else:
            item = Item(
                x=x,
                y=y,
                char=Symbols.HERB,
                color=(0, 150, 0),
                name="약초",
                consumable=True,
                nutrition=10,
                hydration=0,
            )

        world.add_item(item)

    return world
