"""
경제/상거래 시스템
화폐, 구매, 판매, 가격 시스템
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

if TYPE_CHECKING:
    from components.entity import Actor, Item
    from components.npc import NPCComponent


class ItemRarity(Enum):
    """아이템 희귀도"""
    COMMON = auto()        # 흔함
    UNCOMMON = auto()      # 약간 희귀
    RARE = auto()          # 희귀
    EPIC = auto()          # 에픽
    LEGENDARY = auto()     # 전설


@dataclass
class ItemValue:
    """아이템 가치 정보"""
    base_price: int                    # 기본 가격
    rarity: ItemRarity = ItemRarity.COMMON
    condition: float = 1.0             # 상태 (0.0 ~ 1.0)
    is_identified: bool = True         # 감정 여부

    @property
    def sell_price(self) -> int:
        """판매 가격 (기본 가격의 절반)"""
        return int(self.base_price * 0.5 * self.condition)

    @property
    def buy_price(self) -> int:
        """구매 가격"""
        rarity_multiplier = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.5,
            ItemRarity.RARE: 2.0,
            ItemRarity.EPIC: 3.0,
            ItemRarity.LEGENDARY: 5.0,
        }
        multiplier = rarity_multiplier.get(self.rarity, 1.0)
        return int(self.base_price * multiplier)


# 아이템 기본 가격 테이블
ITEM_PRICES: Dict[str, ItemValue] = {
    # 음식
    "마른 고기": ItemValue(base_price=10),
    "빵": ItemValue(base_price=5),
    "치즈": ItemValue(base_price=8),
    "사과": ItemValue(base_price=3),
    "야생 베리": ItemValue(base_price=2),
    "훈제 생선": ItemValue(base_price=15),

    # 음료
    "물병": ItemValue(base_price=5),
    "포도주": ItemValue(base_price=20),
    "에일": ItemValue(base_price=8),

    # 물약
    "치료 물약": ItemValue(base_price=50, rarity=ItemRarity.UNCOMMON),
    "마나 물약": ItemValue(base_price=60, rarity=ItemRarity.UNCOMMON),
    "해독 물약": ItemValue(base_price=40, rarity=ItemRarity.UNCOMMON),
    "힘의 물약": ItemValue(base_price=100, rarity=ItemRarity.RARE),

    # 무기
    "단검": ItemValue(base_price=30),
    "숏소드": ItemValue(base_price=60),
    "롱소드": ItemValue(base_price=100, rarity=ItemRarity.UNCOMMON),
    "강철 검": ItemValue(base_price=200, rarity=ItemRarity.RARE),
    "도끼": ItemValue(base_price=80),
    "활": ItemValue(base_price=70),
    "화살 (20개)": ItemValue(base_price=20),

    # 방어구
    "가죽 갑옷": ItemValue(base_price=50),
    "사슬 갑옷": ItemValue(base_price=150, rarity=ItemRarity.UNCOMMON),
    "판금 갑옷": ItemValue(base_price=400, rarity=ItemRarity.RARE),
    "나무 방패": ItemValue(base_price=30),
    "철제 방패": ItemValue(base_price=100, rarity=ItemRarity.UNCOMMON),

    # 도구
    "횃불": ItemValue(base_price=5),
    "밧줄": ItemValue(base_price=10),
    "곡괭이": ItemValue(base_price=40),
    "낚싯대": ItemValue(base_price=25),
    "텐트": ItemValue(base_price=80),

    # 재료
    "약초": ItemValue(base_price=15),
    "철광석": ItemValue(base_price=20),
    "가죽": ItemValue(base_price=12),
    "뼈": ItemValue(base_price=5),
    "몬스터 핵": ItemValue(base_price=50, rarity=ItemRarity.UNCOMMON),

    # 특수
    "신성한 성배": ItemValue(base_price=1000, rarity=ItemRarity.LEGENDARY),
    "마법 스크롤": ItemValue(base_price=80, rarity=ItemRarity.RARE),
}


class Wallet:
    """
    지갑 (화폐 관리)

    여러 종류의 화폐 지원 가능
    """

    def __init__(self, gold: int = 0, silver: int = 0, copper: int = 0):
        self._gold = gold
        self._silver = silver
        self._copper = copper

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def silver(self) -> int:
        return self._silver

    @property
    def copper(self) -> int:
        return self._copper

    @property
    def total_in_copper(self) -> int:
        """모든 화폐를 구리로 환산"""
        return self._gold * 100 + self._silver * 10 + self._copper

    @property
    def total_in_gold(self) -> int:
        """모든 화폐를 금으로 환산 (편의용)"""
        return self.total_in_copper // 100

    def add(self, gold: int = 0, silver: int = 0, copper: int = 0) -> None:
        """화폐 추가"""
        self._gold += gold
        self._silver += silver
        self._copper += copper
        self._normalize()

    def remove(self, gold: int = 0, silver: int = 0, copper: int = 0) -> bool:
        """
        화폐 제거

        Returns:
            성공 여부
        """
        total_remove = gold * 100 + silver * 10 + copper
        if self.total_in_copper < total_remove:
            return False

        # 단순히 총액에서 빼기
        total = self.total_in_copper - total_remove
        self._gold = total // 100
        total %= 100
        self._silver = total // 10
        self._copper = total % 10
        return True

    def _normalize(self) -> None:
        """화폐 정규화 (구리 10개 = 은 1개, 은 10개 = 금 1개)"""
        total = self.total_in_copper
        self._gold = total // 100
        total %= 100
        self._silver = total // 10
        self._copper = total % 10

    def __str__(self) -> str:
        parts = []
        if self._gold > 0:
            parts.append(f"{self._gold}G")
        if self._silver > 0:
            parts.append(f"{self._silver}S")
        if self._copper > 0 or not parts:
            parts.append(f"{self._copper}C")
        return " ".join(parts)

    def can_afford(self, gold: int = 0, silver: int = 0, copper: int = 0) -> bool:
        """지불 가능 여부"""
        total_cost = gold * 100 + silver * 10 + copper
        return self.total_in_copper >= total_cost


class Shop:
    """
    상점 시스템

    NPC 상인과의 거래 관리
    """

    def __init__(
        self,
        name: str = "상점",
        buy_multiplier: float = 1.0,    # 구매 가격 배율
        sell_multiplier: float = 0.5,   # 판매 가격 배율
    ):
        self.name = name
        self.buy_multiplier = buy_multiplier
        self.sell_multiplier = sell_multiplier
        self.inventory: List[Tuple[Item, int]] = []  # (아이템, 수량)
        self.gold: int = 500  # 상점 소지금

    def add_item(self, item: Item, quantity: int = 1) -> None:
        """상점에 아이템 추가"""
        # 기존 아이템이면 수량만 증가
        for i, (existing_item, qty) in enumerate(self.inventory):
            if existing_item.name == item.name:
                self.inventory[i] = (existing_item, qty + quantity)
                return
        self.inventory.append((item, quantity))

    def remove_item(self, item_name: str, quantity: int = 1) -> Optional[Item]:
        """상점에서 아이템 제거"""
        for i, (item, qty) in enumerate(self.inventory):
            if item.name == item_name:
                if qty > quantity:
                    self.inventory[i] = (item, qty - quantity)
                else:
                    self.inventory.pop(i)
                return item
        return None

    def get_buy_price(self, item_name: str) -> int:
        """아이템 구매 가격 (플레이어가 사는 가격)"""
        item_value = ITEM_PRICES.get(item_name)
        if item_value:
            return int(item_value.buy_price * self.buy_multiplier)
        return 10  # 기본 가격

    def get_sell_price(self, item_name: str) -> int:
        """아이템 판매 가격 (플레이어가 파는 가격)"""
        item_value = ITEM_PRICES.get(item_name)
        if item_value:
            return int(item_value.sell_price * self.sell_multiplier)
        return 5  # 기본 가격

    def buy_from_shop(
        self,
        item_name: str,
        buyer_wallet: Wallet,
        quantity: int = 1,
    ) -> Tuple[bool, str, Optional[Item]]:
        """
        상점에서 구매

        Args:
            item_name: 아이템 이름
            buyer_wallet: 구매자 지갑
            quantity: 수량

        Returns:
            (성공 여부, 메시지, 아이템)
        """
        # 아이템 찾기
        found_item = None
        found_qty = 0
        for item, qty in self.inventory:
            if item.name == item_name:
                found_item = item
                found_qty = qty
                break

        if not found_item:
            return False, "그 물건은 없네.", None

        if found_qty < quantity:
            return False, f"재고가 부족하네. ({found_qty}개 남음)", None

        # 가격 계산
        total_price = self.get_buy_price(item_name) * quantity

        if not buyer_wallet.can_afford(gold=total_price):
            return False, f"돈이 부족하네. ({total_price}G 필요)", None

        # 거래 실행
        buyer_wallet.remove(gold=total_price)
        self.gold += total_price
        item = self.remove_item(item_name, quantity)

        return True, f"{item_name}을(를) {total_price}G에 구매했다.", item

    def sell_to_shop(
        self,
        item: Item,
        seller_wallet: Wallet,
        quantity: int = 1,
    ) -> Tuple[bool, str]:
        """
        상점에 판매

        Args:
            item: 판매할 아이템
            seller_wallet: 판매자 지갑
            quantity: 수량

        Returns:
            (성공 여부, 메시지)
        """
        # 가격 계산
        total_price = self.get_sell_price(item.name) * quantity

        if self.gold < total_price:
            return False, "상점에 돈이 부족하군."

        # 거래 실행
        seller_wallet.add(gold=total_price)
        self.gold -= total_price
        self.add_item(item, quantity)

        return True, f"{item.name}을(를) {total_price}G에 판매했다."


class TradeSession:
    """
    거래 세션

    플레이어와 NPC 간의 거래 관리
    """

    def __init__(
        self,
        player: Actor,
        merchant: Actor,
        shop: Shop,
    ):
        self.player = player
        self.merchant = merchant
        self.shop = shop
        self.is_active = True

        # 거래 내역
        self.purchases: List[Tuple[str, int, int]] = []  # (아이템, 수량, 가격)
        self.sales: List[Tuple[str, int, int]] = []

    def get_shop_items(self) -> List[Tuple[Item, int, int]]:
        """상점 아이템 목록 (아이템, 수량, 가격)"""
        result = []
        for item, qty in self.shop.inventory:
            price = self.shop.get_buy_price(item.name)
            result.append((item, qty, price))
        return result

    def get_player_sellable_items(self) -> List[Tuple[Item, int]]:
        """플레이어가 팔 수 있는 아이템 목록 (아이템, 가격)"""
        if not self.player.inventory:
            return []

        result = []
        for item in self.player.inventory:
            price = self.shop.get_sell_price(item.name)
            result.append((item, price))
        return result

    def buy(self, item_name: str, quantity: int = 1) -> Tuple[bool, str]:
        """구매"""
        if not self.player.inventory:
            return False, "인벤토리가 없다."

        # 지갑 가져오기 (플레이어 gold 속성 사용)
        player_wallet = Wallet(gold=getattr(self.player, 'gold', 0))

        success, msg, item = self.shop.buy_from_shop(
            item_name, player_wallet, quantity
        )

        if success and item:
            # 플레이어 gold 업데이트
            self.player.gold = player_wallet.total_in_gold
            # 인벤토리에 추가
            self.player.inventory.add(item)
            self.purchases.append((item_name, quantity, self.shop.get_buy_price(item_name) * quantity))

        return success, msg

    def sell(self, item_index: int) -> Tuple[bool, str]:
        """판매"""
        if not self.player.inventory:
            return False, "인벤토리가 없다."

        item = self.player.inventory.get_item_at(item_index)
        if not item:
            return False, "그 아이템이 없다."

        player_wallet = Wallet(gold=getattr(self.player, 'gold', 0))

        success, msg = self.shop.sell_to_shop(item, player_wallet)

        if success:
            self.player.gold = player_wallet.total_in_gold
            self.player.inventory.remove(item)
            self.sales.append((item.name, 1, self.shop.get_sell_price(item.name)))

        return success, msg

    def end_session(self) -> str:
        """거래 종료"""
        self.is_active = False

        total_spent = sum(price for _, _, price in self.purchases)
        total_earned = sum(price for _, _, price in self.sales)

        if total_spent == 0 and total_earned == 0:
            return "거래 없이 종료했다."

        msg = []
        if total_spent > 0:
            msg.append(f"구매: {total_spent}G")
        if total_earned > 0:
            msg.append(f"판매: {total_earned}G")

        return "거래 완료. " + ", ".join(msg)


# =============================================================================
# 상점 프리셋
# =============================================================================

def create_general_store() -> Shop:
    """잡화점 생성"""
    from components.entity import Item
    from config import Symbols

    shop = Shop(name="잡화점", buy_multiplier=1.0, sell_multiplier=0.4)

    items = [
        Item(char=Symbols.FOOD, color=(0, 200, 0), name="마른 고기", consumable=True, nutrition=200),
        Item(char=Symbols.FOOD, color=(200, 150, 50), name="빵", consumable=True, nutrition=150),
        Item(char='!', color=(0, 150, 255), name="물병", consumable=True, hydration=300),
        Item(char='(', color=(139, 90, 43), name="횃불"),
        Item(char='(', color=(139, 90, 43), name="밧줄"),
    ]

    for item in items:
        shop.add_item(item, quantity=5)

    return shop


def create_weapon_shop() -> Shop:
    """무기점 생성"""
    from components.entity import Item
    from config import Symbols

    shop = Shop(name="무기점", buy_multiplier=1.2, sell_multiplier=0.5)

    items = [
        Item(char=Symbols.WEAPON, color=(192, 192, 192), name="단검"),
        Item(char=Symbols.WEAPON, color=(192, 192, 192), name="숏소드"),
        Item(char=Symbols.WEAPON, color=(200, 200, 200), name="롱소드"),
        Item(char=Symbols.WEAPON, color=(150, 150, 150), name="도끼"),
        Item(char=Symbols.WEAPON, color=(139, 90, 43), name="활"),
        Item(char='|', color=(139, 90, 43), name="화살 (20개)"),
    ]

    for item in items:
        shop.add_item(item, quantity=3)

    return shop


def create_armor_shop() -> Shop:
    """방어구점 생성"""
    from components.entity import Item
    from config import Symbols

    shop = Shop(name="방어구점", buy_multiplier=1.2, sell_multiplier=0.5)

    items = [
        Item(char=Symbols.ARMOR, color=(139, 90, 43), name="가죽 갑옷"),
        Item(char=Symbols.ARMOR, color=(192, 192, 192), name="사슬 갑옷"),
        Item(char=Symbols.ARMOR, color=(139, 90, 43), name="나무 방패"),
        Item(char=Symbols.ARMOR, color=(150, 150, 150), name="철제 방패"),
    ]

    for item in items:
        shop.add_item(item, quantity=2)

    return shop


def create_potion_shop() -> Shop:
    """물약점 생성"""
    from components.entity import Item
    from config import Symbols

    shop = Shop(name="물약점", buy_multiplier=1.5, sell_multiplier=0.6)

    items = [
        Item(char=Symbols.POTION, color=(255, 0, 0), name="치료 물약", consumable=True),
        Item(char=Symbols.POTION, color=(0, 0, 255), name="마나 물약", consumable=True),
        Item(char=Symbols.POTION, color=(0, 255, 0), name="해독 물약", consumable=True),
        Item(char=Symbols.HERB, color=(0, 150, 0), name="약초", consumable=True, nutrition=10),
    ]

    for item in items:
        shop.add_item(item, quantity=5)

    return shop
