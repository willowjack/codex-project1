"""
Fighter 컴포넌트
전투 능력을 가진 엔티티용 컴포넌트
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.entity import Actor


class Fighter:
    """
    전투 능력 컴포넌트

    Attributes:
        max_hp: 최대 체력
        hp: 현재 체력
        defense: 방어력 (받는 데미지 감소)
        power: 공격력 (주는 데미지)
    """

    def __init__(
        self,
        hp: int,
        defense: int,
        power: int,
    ):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power
        self.entity: Actor = None  # type: ignore

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

    def take_damage(self, amount: int) -> int:
        """
        데미지를 받음

        Args:
            amount: 받을 데미지량

        Returns:
            실제로 받은 데미지량
        """
        # 방어력으로 데미지 감소
        actual_damage = max(0, amount - self.defense)
        self.hp -= actual_damage
        return actual_damage

    def heal(self, amount: int) -> int:
        """
        체력 회복

        Args:
            amount: 회복량

        Returns:
            실제 회복량
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def attack(self, target: Actor) -> tuple[int, bool]:
        """
        대상을 공격

        Args:
            target: 공격 대상

        Returns:
            (데미지량, 대상 사망 여부)
        """
        if not target.fighter:
            return 0, False

        damage = self.power
        actual_damage = target.fighter.take_damage(damage)
        is_dead = target.fighter.hp <= 0

        return actual_damage, is_dead
