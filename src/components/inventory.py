"""
Inventory 컴포넌트
인벤토리 및 아이템 관리 시스템
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from components.entity import Actor, Item


class Inventory:
    """
    인벤토리 컴포넌트

    Attributes:
        capacity: 최대 소지 가능 아이템 수
        items: 소지 중인 아이템 리스트
    """

    def __init__(self, capacity: int = 26):  # a-z까지 26개
        self.capacity = capacity
        self.items: List[Item] = []
        self.entity: Actor = None  # type: ignore

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def add(self, item: Item) -> bool:
        """
        아이템 추가

        Args:
            item: 추가할 아이템

        Returns:
            성공 여부
        """
        if self.is_full:
            return False
        self.items.append(item)
        return True

    def remove(self, item: Item) -> bool:
        """
        아이템 제거

        Args:
            item: 제거할 아이템

        Returns:
            성공 여부
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def get_item_at(self, index: int) -> Optional[Item]:
        """인덱스로 아이템 가져오기"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def get_item_by_char(self, char: str) -> Optional[Item]:
        """
        문자로 아이템 가져오기 (a=0, b=1, ...)

        Args:
            char: 'a'부터 'z'까지의 문자

        Returns:
            해당 아이템 또는 None
        """
        index = ord(char.lower()) - ord('a')
        return self.get_item_at(index)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)
