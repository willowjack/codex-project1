"""
종교 시스템
Nethack 스타일의 신앙, 기도, 은총 시스템
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
import random

if TYPE_CHECKING:
    from components.entity import Actor


class DeityDomain(Enum):
    """신의 영역"""
    LIGHT = auto()         # 빛/치유
    WAR = auto()           # 전쟁/힘
    NATURE = auto()        # 자연/생존
    DEATH = auto()         # 죽음/언데드
    KNOWLEDGE = auto()     # 지식/마법
    TRICKERY = auto()      # 속임/행운


class FavorLevel(Enum):
    """신의 은총 레벨"""
    WRATHFUL = -2          # 분노 (저주)
    DISPLEASED = -1        # 불쾌
    NEUTRAL = 0            # 중립
    PLEASED = 1            # 기쁨
    BLESSED = 2            # 축복
    EXALTED = 3            # 찬양


@dataclass
class DivineAbility:
    """신성 능력"""
    name: str
    description: str
    faith_cost: int        # 필요 신앙 포인트
    favor_required: FavorLevel  # 필요 은총 레벨
    cooldown: int = 0      # 쿨다운 (턴)
    effect: str = ""       # 효과 종류


@dataclass
class Deity:
    """
    신 클래스

    각 신은 고유한 영역, 축복, 저주를 가짐
    """
    id: str
    name: str
    title: str              # 칭호 (예: "빛의 신")
    domain: DeityDomain
    description: str

    # 선호/비선호 행동
    liked_actions: List[str] = field(default_factory=list)    # 좋아하는 행동
    disliked_actions: List[str] = field(default_factory=list) # 싫어하는 행동

    # 신성 능력
    abilities: List[DivineAbility] = field(default_factory=list)

    # 축복 효과
    blessing_effects: Dict[str, int] = field(default_factory=dict)

    # 저주 효과
    curse_effects: Dict[str, int] = field(default_factory=dict)


class Religion:
    """
    종교 컴포넌트

    플레이어의 신앙 상태 관리
    """

    def __init__(self):
        self.deity: Optional[Deity] = None  # 섬기는 신
        self.faith_points: int = 0          # 신앙 포인트
        self.favor: int = 0                 # 은총 수치 (-100 ~ 100)
        self.prayer_timeout: int = 0        # 기도 쿨다운
        self.sins: int = 0                  # 죄 (신이 싫어하는 행동)
        self.devotion_acts: int = 0         # 헌신 행위 (신이 좋아하는 행동)

        # 활성 축복/저주
        self.active_blessings: Dict[str, int] = {}  # 효과: 남은 턴
        self.active_curses: Dict[str, int] = {}

        # 능력 쿨다운
        self.ability_cooldowns: Dict[str, int] = {}

    @property
    def favor_level(self) -> FavorLevel:
        """현재 은총 레벨"""
        if self.favor <= -50:
            return FavorLevel.WRATHFUL
        elif self.favor < 0:
            return FavorLevel.DISPLEASED
        elif self.favor < 25:
            return FavorLevel.NEUTRAL
        elif self.favor < 50:
            return FavorLevel.PLEASED
        elif self.favor < 80:
            return FavorLevel.BLESSED
        else:
            return FavorLevel.EXALTED

    @property
    def favor_string(self) -> str:
        """은총 레벨 문자열"""
        level_names = {
            FavorLevel.WRATHFUL: "분노",
            FavorLevel.DISPLEASED: "불쾌",
            FavorLevel.NEUTRAL: "중립",
            FavorLevel.PLEASED: "기쁨",
            FavorLevel.BLESSED: "축복",
            FavorLevel.EXALTED: "찬양",
        }
        return level_names.get(self.favor_level, "알 수 없음")

    def convert(self, deity: Deity) -> str:
        """
        신앙 귀의

        Args:
            deity: 섬길 신

        Returns:
            결과 메시지
        """
        old_deity = self.deity

        if old_deity:
            # 배교 페널티
            self.favor = -30
            self.sins += 10
            msg = f"{old_deity.name}을(를) 버리고 {deity.name}에게 귀의했다. "
            msg += f"{old_deity.name}의 분노를 느낀다..."
        else:
            self.favor = 10
            msg = f"{deity.name}에게 귀의했다. 신의 관심을 느낀다."

        self.deity = deity
        self.faith_points = 0
        self.active_blessings.clear()
        self.active_curses.clear()

        return msg

    def pray(self) -> tuple[bool, str]:
        """
        기도

        Returns:
            (성공 여부, 결과 메시지)
        """
        if not self.deity:
            return False, "섬기는 신이 없다."

        if self.prayer_timeout > 0:
            return False, f"아직 기도할 수 없다. ({self.prayer_timeout}턴 대기)"

        # 기도 쿨다운 설정
        self.prayer_timeout = 500  # 약 8분

        # 은총 레벨에 따른 결과
        level = self.favor_level

        if level == FavorLevel.WRATHFUL:
            # 분노한 신은 저주를 내림
            self._apply_curse()
            return False, f"{self.deity.name}의 분노가 내려온다!"

        elif level == FavorLevel.DISPLEASED:
            # 불쾌한 신은 무시함
            return False, f"{self.deity.name}은(는) 응답하지 않는다."

        elif level == FavorLevel.NEUTRAL:
            # 중립적인 신은 가끔 응답
            if random.random() < 0.3:
                self._apply_minor_blessing()
                return True, f"{self.deity.name}이(가) 작은 은총을 내린다."
            return False, f"{self.deity.name}은(는) 침묵한다."

        elif level == FavorLevel.PLEASED:
            # 기쁜 신은 자주 응답
            if random.random() < 0.6:
                self._apply_minor_blessing()
                return True, f"{self.deity.name}이(가) 은총을 내린다!"
            return True, f"{self.deity.name}이(가) 지켜보고 있음을 느낀다."

        elif level == FavorLevel.BLESSED:
            # 축복받은 신은 대부분 응답
            self._apply_blessing()
            return True, f"{self.deity.name}의 강력한 은총이 내린다!"

        else:  # EXALTED
            # 찬양받는 자에게는 특별한 축복
            self._apply_major_blessing()
            return True, f"{self.deity.name}이(가) 강림하여 축복한다!"

    def _apply_minor_blessing(self) -> None:
        """작은 축복 적용"""
        blessings = ["minor_heal", "minor_satiate", "minor_protection"]
        blessing = random.choice(blessings)
        self.active_blessings[blessing] = 100  # 100턴 지속

    def _apply_blessing(self) -> None:
        """축복 적용"""
        if self.deity:
            for effect, duration in self.deity.blessing_effects.items():
                self.active_blessings[effect] = duration

    def _apply_major_blessing(self) -> None:
        """강력한 축복 적용"""
        # 모든 축복 + 보너스
        self._apply_blessing()
        self.active_blessings["divine_protection"] = 500
        self.active_blessings["full_restore"] = 1

    def _apply_curse(self) -> None:
        """저주 적용"""
        if self.deity:
            for effect, duration in self.deity.curse_effects.items():
                self.active_curses[effect] = duration
        else:
            self.active_curses["weakness"] = 200

    def sacrifice(self, item_value: int) -> str:
        """
        제물 바치기

        Args:
            item_value: 제물 가치

        Returns:
            결과 메시지
        """
        if not self.deity:
            return "섬기는 신이 없다."

        # 은총 증가
        favor_gain = item_value // 10
        self.favor = min(100, self.favor + favor_gain)
        self.faith_points += item_value // 5
        self.devotion_acts += 1

        if favor_gain >= 10:
            return f"{self.deity.name}이(가) 제물에 크게 기뻐한다!"
        elif favor_gain >= 5:
            return f"{self.deity.name}이(가) 제물을 받아들인다."
        else:
            return f"{self.deity.name}이(가) 제물에 별 관심이 없다."

    def commit_sin(self, severity: int = 1) -> str:
        """
        죄를 저지름 (신이 싫어하는 행동)

        Args:
            severity: 죄의 심각도

        Returns:
            결과 메시지
        """
        if not self.deity:
            return ""

        self.sins += severity
        self.favor = max(-100, self.favor - severity * 5)

        if self.favor <= -50:
            return f"{self.deity.name}의 분노를 느낀다!"
        elif self.favor < 0:
            return f"{self.deity.name}이(가) 불쾌해한다."
        return ""

    def act_devout(self, significance: int = 1) -> str:
        """
        헌신적 행동 (신이 좋아하는 행동)

        Args:
            significance: 행동의 중요도

        Returns:
            결과 메시지
        """
        if not self.deity:
            return ""

        self.devotion_acts += significance
        self.favor = min(100, self.favor + significance * 3)
        self.faith_points += significance

        if self.favor >= 80:
            return f"{self.deity.name}이(가) 찬양한다!"
        elif self.favor >= 50:
            return f"{self.deity.name}이(가) 기뻐한다."
        return ""

    def use_ability(self, ability_name: str) -> tuple[bool, str]:
        """
        신성 능력 사용

        Args:
            ability_name: 능력 이름

        Returns:
            (성공 여부, 결과 메시지)
        """
        if not self.deity:
            return False, "섬기는 신이 없다."

        # 능력 찾기
        ability = None
        for a in self.deity.abilities:
            if a.name == ability_name:
                ability = a
                break

        if not ability:
            return False, "그런 능력은 없다."

        # 쿨다운 체크
        if self.ability_cooldowns.get(ability_name, 0) > 0:
            return False, f"아직 사용할 수 없다. ({self.ability_cooldowns[ability_name]}턴 대기)"

        # 은총 레벨 체크
        if self.favor_level.value < ability.favor_required.value:
            return False, "신의 은총이 부족하다."

        # 신앙 포인트 체크
        if self.faith_points < ability.faith_cost:
            return False, "신앙 포인트가 부족하다."

        # 능력 사용
        self.faith_points -= ability.faith_cost
        self.ability_cooldowns[ability_name] = ability.cooldown

        return True, f"{ability.name}을(를) 발동했다! {ability.description}"

    def process_turn(self) -> List[str]:
        """턴 처리"""
        messages = []

        # 기도 쿨다운 감소
        if self.prayer_timeout > 0:
            self.prayer_timeout -= 1

        # 능력 쿨다운 감소
        for ability in list(self.ability_cooldowns.keys()):
            self.ability_cooldowns[ability] -= 1
            if self.ability_cooldowns[ability] <= 0:
                del self.ability_cooldowns[ability]

        # 축복 지속시간 감소
        for blessing in list(self.active_blessings.keys()):
            self.active_blessings[blessing] -= 1
            if self.active_blessings[blessing] <= 0:
                del self.active_blessings[blessing]
                messages.append(f"{blessing} 축복이 사라졌다.")

        # 저주 지속시간 감소
        for curse in list(self.active_curses.keys()):
            self.active_curses[curse] -= 1
            if self.active_curses[curse] <= 0:
                del self.active_curses[curse]
                messages.append(f"{curse} 저주가 풀렸다.")

        return messages


# =============================================================================
# 미리 정의된 신들
# =============================================================================

def create_deities() -> Dict[str, Deity]:
    """게임의 신들 생성"""
    return {
        "solarius": Deity(
            id="solarius",
            name="솔라리우스",
            title="빛의 신",
            domain=DeityDomain.LIGHT,
            description="치유와 정의의 신. 언데드를 물리치고 약자를 돕는 자를 축복한다.",
            liked_actions=["heal_other", "kill_undead", "donate", "protect_innocent"],
            disliked_actions=["kill_innocent", "steal", "use_dark_magic"],
            abilities=[
                DivineAbility(
                    name="신성한 빛",
                    description="주변의 적을 밝은 빛으로 눈부시게 한다.",
                    faith_cost=20,
                    favor_required=FavorLevel.PLEASED,
                    cooldown=50,
                    effect="blind_enemies",
                ),
                DivineAbility(
                    name="치유의 손길",
                    description="체력을 대폭 회복한다.",
                    faith_cost=30,
                    favor_required=FavorLevel.BLESSED,
                    cooldown=100,
                    effect="major_heal",
                ),
            ],
            blessing_effects={
                "light_aura": 300,
                "undead_bane": 300,
                "heal_boost": 300,
            },
            curse_effects={
                "blindness": 100,
                "weakness": 200,
            },
        ),
        "grommash": Deity(
            id="grommash",
            name="그롬마쉬",
            title="전쟁의 신",
            domain=DeityDomain.WAR,
            description="힘과 전투의 신. 용감한 전사와 명예로운 결투를 축복한다.",
            liked_actions=["kill_monster", "win_combat", "honorable_duel"],
            disliked_actions=["flee_combat", "attack_unarmed", "poison"],
            abilities=[
                DivineAbility(
                    name="전사의 분노",
                    description="일시적으로 공격력이 크게 증가한다.",
                    faith_cost=25,
                    favor_required=FavorLevel.PLEASED,
                    cooldown=80,
                    effect="rage",
                ),
                DivineAbility(
                    name="불굴의 의지",
                    description="일시적으로 무적 상태가 된다.",
                    faith_cost=50,
                    favor_required=FavorLevel.EXALTED,
                    cooldown=200,
                    effect="invincible",
                ),
            ],
            blessing_effects={
                "strength_boost": 300,
                "battle_fury": 200,
            },
            curse_effects={
                "cowardice": 150,
                "weakness": 200,
            },
        ),
        "sylvana": Deity(
            id="sylvana",
            name="실바나",
            title="자연의 여신",
            domain=DeityDomain.NATURE,
            description="숲과 생명의 여신. 자연을 보호하고 동물을 아끼는 자를 축복한다.",
            liked_actions=["plant_tree", "protect_animal", "forage", "heal_nature"],
            disliked_actions=["kill_animal", "destroy_nature", "waste_food"],
            abilities=[
                DivineAbility(
                    name="자연의 치유",
                    description="배고픔과 갈증을 완전히 해소한다.",
                    faith_cost=20,
                    favor_required=FavorLevel.PLEASED,
                    cooldown=100,
                    effect="satiate",
                ),
                DivineAbility(
                    name="동물의 친구",
                    description="주변 동물이 우호적이 된다.",
                    faith_cost=15,
                    favor_required=FavorLevel.NEUTRAL,
                    cooldown=50,
                    effect="charm_animals",
                ),
            ],
            blessing_effects={
                "nature_sustenance": 500,
                "animal_friend": 300,
                "poison_immunity": 300,
            },
            curse_effects={
                "hunger": 200,
                "thirst": 200,
                "animal_hostility": 300,
            },
        ),
        "mortis": Deity(
            id="mortis",
            name="모르티스",
            title="죽음의 신",
            domain=DeityDomain.DEATH,
            description="죽음과 영혼의 신. 언데드를 다루고 죽음을 두려워하지 않는 자를 축복한다.",
            liked_actions=["kill", "raise_undead", "visit_grave", "death_ritual"],
            disliked_actions=["resurrect", "flee_death", "heal_enemy"],
            abilities=[
                DivineAbility(
                    name="죽음의 손길",
                    description="적에게 직접적인 피해를 준다.",
                    faith_cost=30,
                    favor_required=FavorLevel.PLEASED,
                    cooldown=60,
                    effect="death_touch",
                ),
                DivineAbility(
                    name="영혼 흡수",
                    description="적을 죽이면 체력을 흡수한다.",
                    faith_cost=40,
                    favor_required=FavorLevel.BLESSED,
                    cooldown=150,
                    effect="life_drain",
                ),
            ],
            blessing_effects={
                "death_ward": 300,
                "soul_sight": 200,
            },
            curse_effects={
                "life_drain": 150,
                "haunted": 200,
            },
        ),
    }
