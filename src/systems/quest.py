"""
퀘스트 시스템
퀘스트 수락, 진행, 완료 관리
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from enum import Enum, auto
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from components.entity import Actor, Item


class QuestType(Enum):
    """퀘스트 종류"""
    KILL = auto()          # 몬스터 처치
    COLLECT = auto()       # 아이템 수집
    DELIVER = auto()       # 아이템 배달
    EXPLORE = auto()       # 장소 탐험
    TALK = auto()          # NPC와 대화
    ESCORT = auto()        # 호위
    SURVIVE = auto()       # 생존 (특정 턴 동안)


class QuestStatus(Enum):
    """퀘스트 상태"""
    AVAILABLE = auto()     # 수락 가능
    ACTIVE = auto()        # 진행 중
    COMPLETED = auto()     # 완료 (보상 받기 전)
    FINISHED = auto()      # 종료 (보상 받음)
    FAILED = auto()        # 실패


@dataclass
class QuestObjective:
    """퀘스트 목표"""
    type: QuestType
    target: str                # 목표 대상 (몬스터 이름, 아이템 이름, 위치 등)
    required_count: int = 1    # 필요한 수량
    current_count: int = 0     # 현재 진행도
    description: str = ""      # 목표 설명

    @property
    def is_complete(self) -> bool:
        return self.current_count >= self.required_count

    @property
    def progress_string(self) -> str:
        return f"{self.current_count}/{self.required_count}"


@dataclass
class QuestReward:
    """퀘스트 보상"""
    gold: int = 0
    experience: int = 0
    items: List[str] = field(default_factory=list)  # 아이템 이름 리스트
    reputation: int = 0        # 평판 증가
    faith_points: int = 0      # 신앙 포인트


@dataclass
class Quest:
    """
    퀘스트 클래스

    Nethack의 퀘스트와 Unreal World의 임무 시스템에서 영감
    """
    id: str
    name: str
    description: str
    giver: str                 # 퀘스트 의뢰인 이름
    objectives: List[QuestObjective]
    rewards: QuestReward
    status: QuestStatus = QuestStatus.AVAILABLE

    # 선행 조건
    required_level: int = 1
    required_quests: List[str] = field(default_factory=list)  # 선행 퀘스트 ID
    required_reputation: int = 0

    # 제한
    time_limit: int = 0        # 0 = 무제한, 그 외 = 턴 제한
    turns_remaining: int = 0

    # 대화
    accept_dialogue: str = "퀘스트를 수락하시겠습니까?"
    progress_dialogue: str = "아직 끝나지 않았군."
    complete_dialogue: str = "잘 해냈군! 여기 보상이네."
    fail_dialogue: str = "실패했군... 아쉽네."

    @property
    def is_complete(self) -> bool:
        return all(obj.is_complete for obj in self.objectives)

    def update_progress(self, objective_type: QuestType, target: str, amount: int = 1) -> bool:
        """
        퀘스트 진행도 업데이트

        Args:
            objective_type: 목표 타입
            target: 목표 대상
            amount: 증가량

        Returns:
            진행도가 변경되었는지 여부
        """
        if self.status != QuestStatus.ACTIVE:
            return False

        updated = False
        for obj in self.objectives:
            if obj.type == objective_type and obj.target == target:
                if obj.current_count < obj.required_count:
                    obj.current_count = min(obj.current_count + amount, obj.required_count)
                    updated = True

        # 모든 목표 완료 시 상태 변경
        if updated and self.is_complete:
            self.status = QuestStatus.COMPLETED

        return updated

    def accept(self) -> bool:
        """퀘스트 수락"""
        if self.status != QuestStatus.AVAILABLE:
            return False

        self.status = QuestStatus.ACTIVE
        if self.time_limit > 0:
            self.turns_remaining = self.time_limit
        return True

    def fail(self) -> None:
        """퀘스트 실패"""
        self.status = QuestStatus.FAILED

    def finish(self) -> QuestReward:
        """퀘스트 완료 및 보상 수령"""
        if self.status == QuestStatus.COMPLETED:
            self.status = QuestStatus.FINISHED
            return self.rewards
        return QuestReward()

    def process_turn(self) -> bool:
        """
        턴 처리 (시간 제한 퀘스트용)

        Returns:
            시간 초과로 실패했는지 여부
        """
        if self.status != QuestStatus.ACTIVE:
            return False

        if self.time_limit > 0:
            self.turns_remaining -= 1
            if self.turns_remaining <= 0:
                self.fail()
                return True

        return False


class QuestLog:
    """
    퀘스트 로그
    플레이어의 퀘스트 관리
    """

    def __init__(self):
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []
        self.failed_quests: List[Quest] = []

    def add_quest(self, quest: Quest) -> bool:
        """퀘스트 추가"""
        if quest.accept():
            self.active_quests.append(quest)
            return True
        return False

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """ID로 퀘스트 찾기"""
        for quest in self.active_quests:
            if quest.id == quest_id:
                return quest
        return None

    def update_kill_quest(self, monster_name: str) -> List[str]:
        """몬스터 처치 퀘스트 업데이트"""
        messages = []
        for quest in self.active_quests:
            if quest.update_progress(QuestType.KILL, monster_name):
                for obj in quest.objectives:
                    if obj.type == QuestType.KILL and obj.target == monster_name:
                        messages.append(f"[퀘스트] {quest.name}: {obj.target} 처치 ({obj.progress_string})")
                if quest.is_complete:
                    messages.append(f"[퀘스트] '{quest.name}' 완료! 의뢰인에게 돌아가자.")
        return messages

    def update_collect_quest(self, item_name: str) -> List[str]:
        """아이템 수집 퀘스트 업데이트"""
        messages = []
        for quest in self.active_quests:
            if quest.update_progress(QuestType.COLLECT, item_name):
                for obj in quest.objectives:
                    if obj.type == QuestType.COLLECT and obj.target == item_name:
                        messages.append(f"[퀘스트] {quest.name}: {obj.target} 수집 ({obj.progress_string})")
                if quest.is_complete:
                    messages.append(f"[퀘스트] '{quest.name}' 완료! 의뢰인에게 돌아가자.")
        return messages

    def complete_quest(self, quest: Quest) -> Optional[QuestReward]:
        """퀘스트 완료 및 보상 수령"""
        if quest not in self.active_quests:
            return None

        if quest.status == QuestStatus.COMPLETED:
            reward = quest.finish()
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            return reward

        return None

    def process_turn(self) -> List[str]:
        """턴 처리"""
        messages = []
        for quest in self.active_quests[:]:  # 복사본으로 순회
            if quest.process_turn():
                messages.append(f"[퀘스트] '{quest.name}' 시간 초과로 실패!")
                self.active_quests.remove(quest)
                self.failed_quests.append(quest)
            elif quest.time_limit > 0 and quest.turns_remaining <= 100:
                messages.append(f"[퀘스트] '{quest.name}' 남은 시간: {quest.turns_remaining}턴")

        return messages

    @property
    def active_count(self) -> int:
        return len(self.active_quests)

    @property
    def completed_count(self) -> int:
        return len(self.completed_quests)


# =============================================================================
# 미리 정의된 퀘스트들
# =============================================================================

def create_starter_quests() -> List[Quest]:
    """초보자 퀘스트 생성"""
    return [
        Quest(
            id="rat_hunt",
            name="쥐 사냥",
            description="마을 창고에 쥐가 들끓고 있다. 쥐 5마리를 처치하라.",
            giver="여관주인",
            objectives=[
                QuestObjective(
                    type=QuestType.KILL,
                    target="쥐",
                    required_count=5,
                    description="쥐 5마리 처치",
                ),
            ],
            rewards=QuestReward(gold=50, experience=20, reputation=5),
            accept_dialogue="창고에 쥐가 너무 많아. 좀 처리해줄 수 있겠나?",
            complete_dialogue="고맙네! 여기 보상이야.",
        ),
        Quest(
            id="herb_gathering",
            name="약초 채집",
            description="사제님이 약초가 필요하시다. 숲에서 약초 3개를 모아오라.",
            giver="사제",
            objectives=[
                QuestObjective(
                    type=QuestType.COLLECT,
                    target="약초",
                    required_count=3,
                    description="약초 3개 수집",
                ),
            ],
            rewards=QuestReward(gold=30, experience=15, faith_points=10),
            accept_dialogue="치료를 위해 약초가 필요하네. 숲에서 좀 구해올 수 있겠나?",
            complete_dialogue="고맙네. 신의 축복이 함께 하길.",
        ),
        Quest(
            id="goblin_threat",
            name="고블린 위협",
            description="던전 입구 근처에 고블린이 출몰한다. 고블린 3마리를 처치하라.",
            giver="경비병",
            objectives=[
                QuestObjective(
                    type=QuestType.KILL,
                    target="고블린",
                    required_count=3,
                    description="고블린 3마리 처치",
                ),
            ],
            rewards=QuestReward(gold=100, experience=50, reputation=10),
            required_level=2,
            accept_dialogue="던전 근처에 고블린이 자주 나타나. 처리해줄 수 있겠나?",
            complete_dialogue="훌륭해! 마을이 안전해졌군.",
        ),
    ]


def create_advanced_quests() -> List[Quest]:
    """고급 퀘스트 생성"""
    return [
        Quest(
            id="orc_warlord",
            name="오크 대장 처치",
            description="던전 깊은 곳에 오크 대장이 있다. 처치하라.",
            giver="경비병 대장",
            objectives=[
                QuestObjective(
                    type=QuestType.KILL,
                    target="오크 대장",
                    required_count=1,
                    description="오크 대장 처치",
                ),
            ],
            rewards=QuestReward(
                gold=500,
                experience=200,
                items=["강철 검"],
                reputation=30,
            ),
            required_level=5,
            required_quests=["goblin_threat"],
            accept_dialogue="오크들의 대장을 처치해야 해. 위험한 임무지만 할 수 있겠나?",
            complete_dialogue="대단하군! 자네는 진정한 영웅이야.",
        ),
        Quest(
            id="sacred_relic",
            name="성물 회수",
            description="도둑들이 신전의 성물을 훔쳐갔다. 되찾아 오라.",
            giver="대사제",
            objectives=[
                QuestObjective(
                    type=QuestType.COLLECT,
                    target="신성한 성배",
                    required_count=1,
                    description="신성한 성배 회수",
                ),
            ],
            rewards=QuestReward(
                gold=300,
                experience=150,
                faith_points=50,
                reputation=25,
            ),
            required_reputation=20,
            time_limit=3000,  # 시간 제한
            accept_dialogue="신전의 성물이 도난당했네. 되찾아올 수 있겠나?",
            complete_dialogue="신의 은총이 함께 하길! 성물을 되찾아줘서 고맙네.",
            fail_dialogue="시간이 너무 지났군... 성물의 힘이 사라졌어.",
        ),
    ]
