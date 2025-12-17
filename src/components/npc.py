"""
NPC 컴포넌트
대화 가능한 NPC, 상인, 사제 등
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Callable
from enum import Enum, auto
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from components.entity import Actor, Item


class NPCRole(Enum):
    """NPC 역할"""
    VILLAGER = auto()      # 일반 마을 주민
    MERCHANT = auto()      # 상인
    PRIEST = auto()        # 사제
    BLACKSMITH = auto()    # 대장장이
    INNKEEPER = auto()     # 여관주인
    QUEST_GIVER = auto()   # 퀘스트 제공자
    GUARD = auto()         # 경비병
    HERMIT = auto()        # 은둔자


@dataclass
class DialogueOption:
    """대화 선택지"""
    text: str                              # 선택지 텍스트
    response: str                          # NPC 응답
    action: Optional[str] = None           # 실행할 액션 (예: "trade", "quest", "pray")
    condition: Optional[str] = None        # 조건 (예: "has_gold:100")
    next_dialogue: Optional[str] = None    # 다음 대화 ID


@dataclass
class Dialogue:
    """대화 노드"""
    id: str
    npc_text: str                          # NPC가 하는 말
    options: List[DialogueOption] = field(default_factory=list)


class NPCComponent:
    """
    NPC 컴포넌트

    대화, 상거래, 퀘스트 제공 등의 기능
    """

    def __init__(
        self,
        role: NPCRole = NPCRole.VILLAGER,
        dialogues: Optional[Dict[str, Dialogue]] = None,
        shop_inventory: Optional[List[Item]] = None,
        gold: int = 100,
        faction: str = "neutral",
    ):
        self.role = role
        self.dialogues = dialogues or {}
        self.shop_inventory: List[Item] = shop_inventory or []
        self.gold = gold
        self.faction = faction

        # 현재 대화 상태
        self.current_dialogue_id = "greeting"
        self.disposition = 50  # 0-100, 호감도

        # 연결된 엔티티
        self.entity: Actor = None  # type: ignore

    @property
    def is_friendly(self) -> bool:
        return self.disposition >= 30

    @property
    def is_hostile(self) -> bool:
        return self.disposition < 10

    def get_greeting(self) -> str:
        """인사말 반환"""
        if self.disposition >= 70:
            greetings = {
                NPCRole.MERCHANT: "어서 오게, 친구! 좋은 물건이 많이 있다네.",
                NPCRole.PRIEST: "신의 축복이 함께 하길. 무엇을 도와줄까?",
                NPCRole.BLACKSMITH: "오, 자네군! 오늘은 뭘 만들어줄까?",
                NPCRole.INNKEEPER: "어서 와! 방이 필요한가?",
                NPCRole.VILLAGER: "안녕하신가, 친구!",
                NPCRole.GUARD: "오늘도 무사하길.",
                NPCRole.HERMIT: "...오랜만에 방문객이군.",
            }
        elif self.disposition >= 30:
            greetings = {
                NPCRole.MERCHANT: "어서 오게. 뭘 찾나?",
                NPCRole.PRIEST: "신의 가호가 있기를. 무슨 일인가?",
                NPCRole.BLACKSMITH: "뭐, 필요한 게 있나?",
                NPCRole.INNKEEPER: "뭘 원하나?",
                NPCRole.VILLAGER: "무슨 일이지?",
                NPCRole.GUARD: "마을에 무슨 일로?",
                NPCRole.HERMIT: "...뭘 원하나?",
            }
        else:
            greetings = {
                NPCRole.MERCHANT: "흥, 또 왔군.",
                NPCRole.PRIEST: "...그대의 영혼이 걱정되는군.",
                NPCRole.BLACKSMITH: "뭐야?",
                NPCRole.INNKEEPER: "자네 같은 건 손님으로 안 받아.",
                NPCRole.VILLAGER: "저리 가!",
                NPCRole.GUARD: "수상한 놈이군. 조심해라.",
                NPCRole.HERMIT: "꺼져.",
            }

        return greetings.get(self.role, "...")

    def get_current_dialogue(self) -> Optional[Dialogue]:
        """현재 대화 가져오기"""
        return self.dialogues.get(self.current_dialogue_id)

    def change_disposition(self, amount: int) -> str:
        """호감도 변경"""
        old = self.disposition
        self.disposition = max(0, min(100, self.disposition + amount))

        if self.disposition > old:
            if self.disposition >= 70 and old < 70:
                return f"{self.entity.name}이(가) 당신을 친구로 여기게 되었다!"
            return f"{self.entity.name}의 호감도가 올랐다."
        elif self.disposition < old:
            if self.disposition < 30 and old >= 30:
                return f"{self.entity.name}이(가) 당신을 싫어하게 되었다."
            return f"{self.entity.name}의 호감도가 내려갔다."
        return ""

    def add_to_shop(self, item: Item) -> None:
        """상점에 아이템 추가"""
        self.shop_inventory.append(item)

    def remove_from_shop(self, item: Item) -> bool:
        """상점에서 아이템 제거"""
        if item in self.shop_inventory:
            self.shop_inventory.remove(item)
            return True
        return False


def create_merchant_dialogues() -> Dict[str, Dialogue]:
    """상인 대화 생성"""
    return {
        "greeting": Dialogue(
            id="greeting",
            npc_text="어서 오게. 뭘 찾나?",
            options=[
                DialogueOption(
                    text="물건을 보고 싶네.",
                    response="좋아, 구경해 보게.",
                    action="trade",
                ),
                DialogueOption(
                    text="이 마을에 대해 알려주게.",
                    response="여긴 조용한 마을이지. 던전에서 모험가들이 가끔 온다네.",
                    next_dialogue="village_info",
                ),
                DialogueOption(
                    text="안녕히.",
                    response="다음에 또 오게.",
                ),
            ],
        ),
        "village_info": Dialogue(
            id="village_info",
            npc_text="더 알고 싶은 게 있나?",
            options=[
                DialogueOption(
                    text="던전은 어디 있지?",
                    response="마을 북쪽에 있네. 조심하게, 위험하다네.",
                ),
                DialogueOption(
                    text="다른 건?",
                    response="사제님이 신전에 계시네. 축복을 받고 싶다면 찾아가 보게.",
                ),
                DialogueOption(
                    text="고맙네.",
                    response="천만에.",
                    next_dialogue="greeting",
                ),
            ],
        ),
    }


def create_priest_dialogues() -> Dict[str, Dialogue]:
    """사제 대화 생성"""
    return {
        "greeting": Dialogue(
            id="greeting",
            npc_text="신의 가호가 있기를. 무엇을 도와줄까?",
            options=[
                DialogueOption(
                    text="축복을 받고 싶습니다.",
                    response="신에게 기도를 올리겠네.",
                    action="bless",
                    condition="has_gold:50",
                ),
                DialogueOption(
                    text="신앙에 대해 알려주십시오.",
                    response="우리는 빛의 신을 섬기네. 정의와 자비의 신이시지.",
                    next_dialogue="faith_info",
                ),
                DialogueOption(
                    text="치료를 부탁드립니다.",
                    response="신의 손길로 치유하겠네.",
                    action="heal",
                    condition="has_gold:30",
                ),
                DialogueOption(
                    text="감사합니다.",
                    response="신의 가호가 함께 하길.",
                ),
            ],
        ),
        "faith_info": Dialogue(
            id="faith_info",
            npc_text="신앙의 길을 걷고 싶은가?",
            options=[
                DialogueOption(
                    text="신도가 되고 싶습니다.",
                    response="좋네. 신을 섬기겠다는 맹세를 하게.",
                    action="join_religion",
                ),
                DialogueOption(
                    text="생각해 보겠습니다.",
                    response="천천히 생각해 보게.",
                    next_dialogue="greeting",
                ),
            ],
        ),
    }


def create_blacksmith_dialogues() -> Dict[str, Dialogue]:
    """대장장이 대화 생성"""
    return {
        "greeting": Dialogue(
            id="greeting",
            npc_text="뭐, 필요한 게 있나?",
            options=[
                DialogueOption(
                    text="무기를 보고 싶네.",
                    response="좋아, 보여주지.",
                    action="trade",
                ),
                DialogueOption(
                    text="장비 수리를 부탁하네.",
                    response="어디 보자...",
                    action="repair",
                    condition="has_gold:20",
                ),
                DialogueOption(
                    text="됐네.",
                    response="그래.",
                ),
            ],
        ),
    }


def create_innkeeper_dialogues() -> Dict[str, Dialogue]:
    """여관주인 대화 생성"""
    return {
        "greeting": Dialogue(
            id="greeting",
            npc_text="뭘 원하나?",
            options=[
                DialogueOption(
                    text="방을 빌리고 싶네.",
                    response="하룻밤에 20골드야.",
                    action="rest",
                    condition="has_gold:20",
                ),
                DialogueOption(
                    text="음식을 사고 싶네.",
                    response="좋아, 뭘 원하나?",
                    action="trade",
                ),
                DialogueOption(
                    text="소문 좀 들려주게.",
                    response="동쪽 숲에서 늑대가 자주 나타난다더군.",
                    next_dialogue="rumors",
                ),
                DialogueOption(
                    text="됐네.",
                    response="그래.",
                ),
            ],
        ),
        "rumors": Dialogue(
            id="rumors",
            npc_text="다른 소문도 들을 텐가?",
            options=[
                DialogueOption(
                    text="더 알려주게.",
                    response="던전 깊은 곳에 보물이 있다는 소문이 있어.",
                ),
                DialogueOption(
                    text="고맙네.",
                    response="뭐, 별 거 아니야.",
                    next_dialogue="greeting",
                ),
            ],
        ),
    }
