"""
Entity 컴포넌트
게임의 모든 객체(플레이어, 몬스터, 아이템)의 기본 클래스
"""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.survival import Survival
    from components.npc import NPCComponent
    from systems.quest import QuestLog
    from systems.religion import Religion


class Entity:
    """
    게임 내 모든 객체의 기본 클래스

    Attributes:
        x, y: 맵에서의 위치
        char: 화면에 표시될 ASCII 문자
        color: 표시 색상 (R, G, B)
        name: 엔티티 이름
        blocks_movement: 이동을 막는지 여부
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def move(self, dx: int, dy: int) -> None:
        """엔티티를 상대적으로 이동"""
        self.x += dx
        self.y += dy

    def distance_to(self, other: Entity) -> float:
        """다른 엔티티까지의 거리 계산"""
        dx = other.x - self.x
        dy = other.y - self.y
        return (dx ** 2 + dy ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, char='{self.char}', name='{self.name}')"


class Actor(Entity):
    """
    행동할 수 있는 엔티티 (플레이어, 몬스터)

    추가 속성:
        ai: AI 컴포넌트 (몬스터용)
        fighter: 전투 컴포넌트
        inventory: 인벤토리 컴포넌트
        survival: 생존 컴포넌트 (플레이어용)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai: Optional[BaseAI] = None,
        fighter: Optional[Fighter] = None,
        inventory: Optional[Inventory] = None,
        survival: Optional[Survival] = None,
        npc: Optional[NPCComponent] = None,
        gold: int = 0,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,  # Actor는 항상 이동을 막음
        )
        self.ai = ai
        if self.ai:
            self.ai.entity = self

        self.fighter = fighter
        if self.fighter:
            self.fighter.entity = self

        self.inventory = inventory
        if self.inventory:
            self.inventory.entity = self

        self.survival = survival
        if self.survival:
            self.survival.entity = self

        # NPC 컴포넌트
        self.npc = npc
        if self.npc:
            self.npc.entity = self

        # 경제 시스템
        self.gold = gold

        # 퀘스트/종교 (플레이어 전용, 나중에 설정)
        self.quest_log: Optional[QuestLog] = None
        self.religion: Optional[Religion] = None

    @property
    def is_alive(self) -> bool:
        """살아있는지 확인"""
        if self.fighter:
            return self.fighter.hp > 0
        return False


class Item(Entity):
    """
    아이템 엔티티

    추가 속성:
        consumable: 소비 가능 여부
        equippable: 장착 가능 여부
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: bool = False,
        nutrition: int = 0,      # 음식일 경우 포만감
        hydration: int = 0,      # 음료일 경우 수분
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,  # 아이템은 이동을 막지 않음
        )
        self.consumable = consumable
        self.nutrition = nutrition
        self.hydration = hydration
