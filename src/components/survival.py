"""
Survival 컴포넌트
Unreal World 스타일의 생존 시스템
배고픔, 갈증, 체온, 피로 관리
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from enum import Enum, auto

if TYPE_CHECKING:
    from components.entity import Actor


class SurvivalStatus(Enum):
    """생존 상태"""
    NORMAL = auto()      # 정상
    WARNING = auto()     # 경고
    CRITICAL = auto()    # 위험
    DYING = auto()       # 사망 직전


class Survival:
    """
    생존 시스템 컴포넌트

    Unreal World에서 영감을 받은 생존 시뮬레이션:
    - 배고픔: 음식을 먹지 않으면 점점 증가
    - 갈증: 물을 마시지 않으면 빠르게 증가
    - 체온: 환경과 장비에 따라 변화
    - 피로: 행동하면 증가, 휴식하면 감소
    """

    def __init__(
        self,
        max_hunger: int = 1000,
        max_thirst: int = 1000,
        max_stamina: int = 100,
    ):
        self.max_hunger = max_hunger
        self.max_thirst = max_thirst
        self.max_stamina = max_stamina

        # 현재 수치 (높을수록 좋음)
        self._hunger = max_hunger      # 포만감 (0 = 굶주림)
        self._thirst = max_thirst      # 수분 (0 = 탈수)
        self._stamina = max_stamina    # 체력 (0 = 탈진)
        self._body_temp = 37.0         # 체온 (정상: 36-38도)

        # 상태 플래그
        self.is_resting = False
        self.is_starving = False
        self.is_dehydrated = False

        self.entity: Actor = None  # type: ignore

    # =========================================================================
    # 속성 접근자
    # =========================================================================
    @property
    def hunger(self) -> int:
        return self._hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        self._hunger = max(0, min(value, self.max_hunger))
        self.is_starving = self._hunger <= 0

    @property
    def thirst(self) -> int:
        return self._thirst

    @thirst.setter
    def thirst(self, value: int) -> None:
        self._thirst = max(0, min(value, self.max_thirst))
        self.is_dehydrated = self._thirst <= 0

    @property
    def stamina(self) -> int:
        return self._stamina

    @stamina.setter
    def stamina(self, value: int) -> None:
        self._stamina = max(0, min(value, self.max_stamina))

    @property
    def body_temp(self) -> float:
        return self._body_temp

    @body_temp.setter
    def body_temp(self, value: float) -> None:
        self._body_temp = max(30.0, min(value, 42.0))

    # =========================================================================
    # 상태 확인
    # =========================================================================
    @property
    def hunger_status(self) -> SurvivalStatus:
        """배고픔 상태 확인"""
        if self.hunger <= 0:
            return SurvivalStatus.DYING
        elif self.hunger < 50:
            return SurvivalStatus.CRITICAL
        elif self.hunger < 200:
            return SurvivalStatus.WARNING
        return SurvivalStatus.NORMAL

    @property
    def thirst_status(self) -> SurvivalStatus:
        """갈증 상태 확인"""
        if self.thirst <= 0:
            return SurvivalStatus.DYING
        elif self.thirst < 50:
            return SurvivalStatus.CRITICAL
        elif self.thirst < 200:
            return SurvivalStatus.WARNING
        return SurvivalStatus.NORMAL

    @property
    def temp_status(self) -> SurvivalStatus:
        """체온 상태 확인"""
        if self.body_temp < 32.0 or self.body_temp > 41.0:
            return SurvivalStatus.DYING
        elif self.body_temp < 35.0 or self.body_temp > 39.0:
            return SurvivalStatus.CRITICAL
        elif self.body_temp < 36.0 or self.body_temp > 38.0:
            return SurvivalStatus.WARNING
        return SurvivalStatus.NORMAL

    @property
    def hunger_percent(self) -> float:
        """포만감 퍼센트"""
        return (self.hunger / self.max_hunger) * 100

    @property
    def thirst_percent(self) -> float:
        """수분 퍼센트"""
        return (self.thirst / self.max_thirst) * 100

    @property
    def stamina_percent(self) -> float:
        """체력 퍼센트"""
        return (self.stamina / self.max_stamina) * 100

    # =========================================================================
    # 턴 처리
    # =========================================================================
    def process_turn(self, environment_temp: float = 20.0) -> List[str]:
        """
        매 턴마다 생존 수치 업데이트

        Args:
            environment_temp: 주변 환경 온도 (섭씨)

        Returns:
            발생한 상태 메시지 리스트
        """
        messages = []

        # 배고픔 증가 (포만감 감소)
        old_hunger_status = self.hunger_status
        self.hunger -= 1

        if self.hunger_status != old_hunger_status:
            if self.hunger_status == SurvivalStatus.WARNING:
                messages.append("배가 고파지기 시작한다.")
            elif self.hunger_status == SurvivalStatus.CRITICAL:
                messages.append("심하게 배가 고프다!")
            elif self.hunger_status == SurvivalStatus.DYING:
                messages.append("굶주림으로 죽어가고 있다!")

        # 갈증 증가 (수분 감소) - 더 빠르게 감소
        old_thirst_status = self.thirst_status
        self.thirst -= 2

        if self.thirst_status != old_thirst_status:
            if self.thirst_status == SurvivalStatus.WARNING:
                messages.append("목이 마르기 시작한다.")
            elif self.thirst_status == SurvivalStatus.CRITICAL:
                messages.append("심하게 목이 마르다!")
            elif self.thirst_status == SurvivalStatus.DYING:
                messages.append("탈수로 죽어가고 있다!")

        # 체온 조절 (환경에 따라)
        self._regulate_temperature(environment_temp)

        # 피로 회복/증가
        if self.is_resting:
            self.stamina += 5
        else:
            self.stamina += 1  # 천천히 회복

        return messages

    def _regulate_temperature(self, environment_temp: float) -> None:
        """체온 조절"""
        # 이상적인 환경 온도: 20-25도
        comfortable_temp = 22.0
        diff = environment_temp - comfortable_temp

        # 체온 변화 (서서히)
        if diff > 10:  # 더운 환경
            self.body_temp += 0.1
        elif diff < -10:  # 추운 환경
            self.body_temp -= 0.1
        else:
            # 정상 체온으로 서서히 회복
            if self.body_temp > 37.0:
                self.body_temp -= 0.05
            elif self.body_temp < 37.0:
                self.body_temp += 0.05

    # =========================================================================
    # 행동
    # =========================================================================
    def eat(self, nutrition: int) -> str:
        """
        음식 섭취

        Args:
            nutrition: 영양가

        Returns:
            결과 메시지
        """
        old_hunger = self.hunger
        self.hunger += nutrition

        gained = self.hunger - old_hunger
        if gained > 0:
            if self.hunger >= self.max_hunger * 0.8:
                return "배가 부르다."
            elif self.hunger >= self.max_hunger * 0.5:
                return "적당히 먹었다."
            else:
                return "조금 먹었다."
        return "더 이상 먹을 수 없다."

    def drink(self, hydration: int) -> str:
        """
        물 섭취

        Args:
            hydration: 수분량

        Returns:
            결과 메시지
        """
        old_thirst = self.thirst
        self.thirst += hydration

        gained = self.thirst - old_thirst
        if gained > 0:
            if self.thirst >= self.max_thirst * 0.8:
                return "갈증이 해소되었다."
            elif self.thirst >= self.max_thirst * 0.5:
                return "적당히 마셨다."
            else:
                return "조금 마셨다."
        return "더 이상 마실 수 없다."

    def rest(self) -> str:
        """휴식 시작"""
        self.is_resting = True
        return "휴식을 시작한다..."

    def stop_rest(self) -> str:
        """휴식 종료"""
        self.is_resting = False
        return "휴식을 멈춘다."

    def get_status_string(self) -> str:
        """상태 문자열 반환"""
        status_parts = []

        # 배고픔 상태
        if self.hunger_status == SurvivalStatus.DYING:
            status_parts.append("굶주림")
        elif self.hunger_status == SurvivalStatus.CRITICAL:
            status_parts.append("매우 배고픔")
        elif self.hunger_status == SurvivalStatus.WARNING:
            status_parts.append("배고픔")

        # 갈증 상태
        if self.thirst_status == SurvivalStatus.DYING:
            status_parts.append("탈수")
        elif self.thirst_status == SurvivalStatus.CRITICAL:
            status_parts.append("매우 목마름")
        elif self.thirst_status == SurvivalStatus.WARNING:
            status_parts.append("목마름")

        # 체온 상태
        if self.body_temp < 35.0:
            status_parts.append("저체온")
        elif self.body_temp > 39.0:
            status_parts.append("고열")

        if not status_parts:
            return "정상"
        return ", ".join(status_parts)
