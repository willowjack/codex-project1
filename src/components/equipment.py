"""
장비 컴포넌트
무기, 방어구 등의 장착 시스템
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto

if TYPE_CHECKING:
    from components.entity import Actor


class EquipmentSlot(Enum):
    """장비 슬롯"""
    MAIN_HAND = auto()     # 주 무기
    OFF_HAND = auto()      # 보조 손 (방패, 보조 무기)
    HEAD = auto()          # 머리
    BODY = auto()          # 몸통
    HANDS = auto()         # 손
    FEET = auto()          # 발
    RING_L = auto()        # 왼손 반지
    RING_R = auto()        # 오른손 반지
    AMULET = auto()        # 목걸이


@dataclass
class WeaponData:
    """
    무기 데이터 클래스

    weapons.py의 데이터를 기반으로 생성됨
    """
    weapon_id: str
    name: str
    char: str
    color: tuple
    weapon_type: str       # melee, ranged, magic
    damage: int
    range: int
    accuracy: int
    speed: int
    durability: int
    max_durability: int
    mana_cost: int
    effects: List[str]
    element: str = "physical"
    ammo_type: str = "none"
    value: int = 10
    rarity: str = "common"
    description: str = ""

    @classmethod
    def from_dict(cls, weapon_id: str, data: dict) -> "WeaponData":
        """딕셔너리에서 무기 데이터 생성"""
        return cls(
            weapon_id=weapon_id,
            name=data.get("name", "Unknown"),
            char=data.get("char", ")"),
            color=tuple(data.get("color", (255, 255, 255))),
            weapon_type=data.get("weapon_type", "melee"),
            damage=data.get("damage", 1),
            range=data.get("range", 1),
            accuracy=data.get("accuracy", 0),
            speed=data.get("speed", 2),
            durability=data.get("durability", 100),
            max_durability=data.get("durability", 100),
            mana_cost=data.get("mana_cost", 0),
            effects=data.get("effects", []),
            element=data.get("element", "physical"),
            ammo_type=data.get("ammo_type", "none"),
            value=data.get("value", 10),
            rarity=data.get("rarity", "common"),
            description=data.get("description", ""),
        )

    @property
    def is_broken(self) -> bool:
        """무기가 부서졌는지"""
        return self.max_durability > 0 and self.durability <= 0

    def use(self) -> None:
        """무기 사용 (내구도 감소)"""
        if self.max_durability > 0:
            self.durability = max(0, self.durability - 1)

    def repair(self, amount: int = -1) -> None:
        """무기 수리"""
        if amount < 0:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)


class Equipment:
    """
    장비 컴포넌트

    캐릭터의 장착 아이템 관리
    """

    def __init__(self):
        self.slots: Dict[EquipmentSlot, Optional[WeaponData]] = {
            slot: None for slot in EquipmentSlot
        }
        self.entity: Actor = None  # type: ignore

    @property
    def main_weapon(self) -> Optional[WeaponData]:
        """주 무기"""
        return self.slots[EquipmentSlot.MAIN_HAND]

    @property
    def off_hand(self) -> Optional[WeaponData]:
        """보조 손"""
        return self.slots[EquipmentSlot.OFF_HAND]

    def equip(self, slot: EquipmentSlot, item: WeaponData) -> Optional[WeaponData]:
        """
        아이템 장착

        Args:
            slot: 장착할 슬롯
            item: 장착할 아이템

        Returns:
            이전에 장착했던 아이템 (없으면 None)
        """
        old_item = self.slots[slot]
        self.slots[slot] = item
        return old_item

    def unequip(self, slot: EquipmentSlot) -> Optional[WeaponData]:
        """
        아이템 해제

        Args:
            slot: 해제할 슬롯

        Returns:
            해제된 아이템 (없으면 None)
        """
        item = self.slots[slot]
        self.slots[slot] = None
        return item

    def get_total_damage_bonus(self) -> int:
        """장비로 인한 총 데미지 보너스"""
        bonus = 0
        weapon = self.main_weapon
        if weapon and not weapon.is_broken:
            bonus += weapon.damage
        return bonus

    def get_total_defense_bonus(self) -> int:
        """장비로 인한 총 방어력 보너스"""
        # 추후 방어구 구현 시 확장
        return 0

    def get_total_accuracy_bonus(self) -> int:
        """장비로 인한 총 명중률 보너스"""
        bonus = 0
        weapon = self.main_weapon
        if weapon and not weapon.is_broken:
            bonus += weapon.accuracy
        return bonus

    def get_attack_range(self) -> int:
        """현재 공격 사거리"""
        weapon = self.main_weapon
        if weapon and not weapon.is_broken:
            return weapon.range
        return 1  # 맨손

    def get_weapon_speed(self) -> int:
        """현재 무기 속도"""
        weapon = self.main_weapon
        if weapon and not weapon.is_broken:
            return weapon.speed
        return 2  # 맨손 기본 속도

    def get_equipped_list(self) -> List[tuple]:
        """장착 중인 아이템 목록"""
        return [
            (slot, item) for slot, item in self.slots.items()
            if item is not None
        ]


# =============================================================================
# 무기 생성 헬퍼 함수
# =============================================================================

def create_weapon(weapon_id: str) -> Optional[WeaponData]:
    """
    무기 ID로 무기 생성

    Args:
        weapon_id: 무기 ID (weapons.py에 정의된)

    Returns:
        생성된 무기 데이터 또는 None
    """
    from data.weapons import ALL_WEAPONS

    weapon_data = ALL_WEAPONS.get(weapon_id)
    if weapon_data:
        return WeaponData.from_dict(weapon_id, weapon_data)
    return None


def create_random_weapon(
    weapon_type: str = None,
    rarity: str = None,
) -> Optional[WeaponData]:
    """
    랜덤 무기 생성

    Args:
        weapon_type: 무기 타입 필터 (melee, ranged, magic)
        rarity: 희귀도 필터

    Returns:
        랜덤 생성된 무기
    """
    import random
    from data.weapons import ALL_WEAPONS

    candidates = []
    for wid, wdata in ALL_WEAPONS.items():
        if weapon_type and wdata.get("weapon_type") != weapon_type:
            continue
        if rarity and wdata.get("rarity") != rarity:
            continue
        candidates.append((wid, wdata))

    if not candidates:
        return None

    weapon_id, weapon_data = random.choice(candidates)
    return WeaponData.from_dict(weapon_id, weapon_data)


# =============================================================================
# 전투 계산 헬퍼 함수
# =============================================================================

def calculate_weapon_damage(
    attacker: Actor,
    weapon: Optional[WeaponData],
    target: Actor,
) -> tuple[int, List[str]]:
    """
    무기 데미지 계산

    Args:
        attacker: 공격자
        weapon: 사용 무기 (None이면 맨손)
        target: 대상

    Returns:
        (총 데미지, 적용된 효과 리스트)
    """
    import random

    # 기본 데미지
    base_damage = attacker.power if hasattr(attacker, 'power') else 5

    # 무기 데미지
    weapon_damage = 0
    effects_applied = []

    if weapon and not weapon.is_broken:
        weapon_damage = weapon.damage

        # 특수 효과 처리
        if "undead_bane" in weapon.effects:
            # 언데드 체크 (추후 구현)
            pass

        if "armor_pierce" in weapon.effects:
            effects_applied.append("방어 관통")

        if "magic_damage" in weapon.effects:
            effects_applied.append("마법 데미지")
            # 마법 데미지는 방어력 무시

        # 원소 데미지
        if weapon.element != "physical":
            effects_applied.append(f"{weapon.element} 속성")

        # 내구도 감소
        weapon.use()

    total_damage = base_damage + weapon_damage

    # 명중률 계산
    accuracy = 75  # 기본 명중률
    if weapon:
        accuracy += weapon.accuracy

    if random.randint(1, 100) > accuracy:
        return 0, ["빗나감"]

    return total_damage, effects_applied


def can_attack_target(
    attacker: Actor,
    target: Actor,
    weapon: Optional[WeaponData],
) -> tuple[bool, str]:
    """
    대상을 공격할 수 있는지 확인

    Args:
        attacker: 공격자
        target: 대상
        weapon: 사용 무기

    Returns:
        (공격 가능 여부, 불가능 사유)
    """
    # 거리 계산
    distance = max(abs(target.x - attacker.x), abs(target.y - attacker.y))

    # 사거리 확인
    attack_range = 1
    if weapon and not weapon.is_broken:
        attack_range = weapon.range

    if distance > attack_range:
        return False, "사거리 밖입니다."

    # 마나 확인 (마법 무기)
    if weapon and weapon.mana_cost > 0:
        # 마나 시스템 구현 시 확인
        pass

    return True, ""
