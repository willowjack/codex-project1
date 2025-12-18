"""
게임 저장/불러오기 시스템
JSON 기반 세이브 파일 관리
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, List
import json
import os
import gzip
from datetime import datetime

if TYPE_CHECKING:
    from systems.engine import Engine
    from systems.game_map import GameMap
    from components.entity import Actor, Item


class SaveManager:
    """
    세이브 파일 관리자

    게임 상태를 JSON으로 직렬화/역직렬화
    """

    SAVE_VERSION = "1.0"
    SAVE_DIR = "saves"

    def __init__(self):
        # 저장 디렉토리 생성
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)

    def save_game(self, engine: Engine, slot: int = 0) -> tuple[bool, str]:
        """
        게임 저장

        Args:
            engine: 게임 엔진
            slot: 저장 슬롯 (0-9)

        Returns:
            (성공 여부, 메시지)
        """
        try:
            save_data = self._serialize_engine(engine)

            # 메타데이터 추가
            save_data["meta"] = {
                "version": self.SAVE_VERSION,
                "timestamp": datetime.now().isoformat(),
                "player_name": engine.player.name,
                "turn": engine.turn_count,
                "day": engine.day,
            }

            # 파일 저장 (gzip 압축)
            filename = self._get_save_path(slot)
            with gzip.open(filename, 'wt', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True, f"게임이 슬롯 {slot}에 저장되었습니다."

        except Exception as e:
            return False, f"저장 실패: {str(e)}"

    def load_game(self, slot: int = 0) -> tuple[Optional[Dict], str]:
        """
        게임 불러오기

        Args:
            slot: 저장 슬롯

        Returns:
            (세이브 데이터, 메시지)
        """
        try:
            filename = self._get_save_path(slot)

            if not os.path.exists(filename):
                return None, f"슬롯 {slot}에 저장된 게임이 없습니다."

            with gzip.open(filename, 'rt', encoding='utf-8') as f:
                save_data = json.load(f)

            # 버전 체크
            if save_data.get("meta", {}).get("version") != self.SAVE_VERSION:
                return None, "호환되지 않는 세이브 파일 버전입니다."

            return save_data, "게임을 불러왔습니다."

        except Exception as e:
            return None, f"불러오기 실패: {str(e)}"

    def list_saves(self) -> List[Dict[str, Any]]:
        """저장된 게임 목록"""
        saves = []

        for slot in range(10):
            filename = self._get_save_path(slot)
            if os.path.exists(filename):
                try:
                    with gzip.open(filename, 'rt', encoding='utf-8') as f:
                        data = json.load(f)
                        meta = data.get("meta", {})
                        saves.append({
                            "slot": slot,
                            "player_name": meta.get("player_name", "Unknown"),
                            "turn": meta.get("turn", 0),
                            "day": meta.get("day", 1),
                            "timestamp": meta.get("timestamp", ""),
                        })
                except:
                    pass

        return saves

    def delete_save(self, slot: int) -> tuple[bool, str]:
        """저장 파일 삭제"""
        filename = self._get_save_path(slot)
        if os.path.exists(filename):
            os.remove(filename)
            return True, f"슬롯 {slot} 삭제 완료"
        return False, "저장 파일이 없습니다."

    def _get_save_path(self, slot: int) -> str:
        """저장 파일 경로"""
        return os.path.join(self.SAVE_DIR, f"save_{slot}.json.gz")

    # =========================================================================
    # 직렬화 (게임 상태 → JSON)
    # =========================================================================

    def _serialize_engine(self, engine: Engine) -> Dict[str, Any]:
        """엔진 상태 직렬화"""
        return {
            "turn_count": engine.turn_count,
            "hour": engine.hour,
            "day": engine.day,
            "environment_temp": engine.environment_temp,
            "game_state": engine.game_state.name,
            "player": self._serialize_actor(engine.player),
            "game_map": self._serialize_map(engine.game_map) if engine.game_map else None,
            "message_log": [
                {"text": msg, "color": list(color)}
                for msg, color in engine.message_log.messages[-50:]  # 최근 50개만
            ],
        }

    def _serialize_actor(self, actor: Actor) -> Dict[str, Any]:
        """Actor 직렬화"""
        data = {
            "x": actor.x,
            "y": actor.y,
            "char": actor.char,
            "color": list(actor.color),
            "name": actor.name,
            "gold": actor.gold,
        }

        # Fighter 컴포넌트
        if actor.fighter:
            data["fighter"] = {
                "max_hp": actor.fighter.max_hp,
                "hp": actor.fighter.hp,
                "defense": actor.fighter.defense,
                "power": actor.fighter.power,
            }

        # Survival 컴포넌트
        if actor.survival:
            data["survival"] = {
                "max_hunger": actor.survival.max_hunger,
                "hunger": actor.survival.hunger,
                "max_thirst": actor.survival.max_thirst,
                "thirst": actor.survival.thirst,
                "max_stamina": actor.survival.max_stamina,
                "stamina": actor.survival.stamina,
                "body_temp": actor.survival.body_temp,
                "is_resting": actor.survival.is_resting,
            }

        # Inventory 컴포넌트
        if actor.inventory:
            data["inventory"] = {
                "capacity": actor.inventory.capacity,
                "items": [self._serialize_item(item) for item in actor.inventory.items],
            }

        # Quest Log
        if actor.quest_log:
            data["quest_log"] = self._serialize_quest_log(actor.quest_log)

        # Religion
        if actor.religion:
            data["religion"] = self._serialize_religion(actor.religion)

        return data

    def _serialize_item(self, item: Item) -> Dict[str, Any]:
        """Item 직렬화"""
        return {
            "x": item.x,
            "y": item.y,
            "char": item.char,
            "color": list(item.color),
            "name": item.name,
            "consumable": item.consumable,
            "nutrition": item.nutrition,
            "hydration": item.hydration,
        }

    def _serialize_map(self, game_map: GameMap) -> Dict[str, Any]:
        """GameMap 직렬화"""
        import numpy as np

        # 타일을 간단한 형태로 저장 (walkable, transparent만)
        tiles_data = []
        for x in range(game_map.width):
            col = []
            for y in range(game_map.height):
                tile = game_map.tiles[x, y]
                col.append({
                    "w": bool(tile["walkable"]),
                    "t": bool(tile["transparent"]),
                    "c": str(tile["char"]),
                })
            tiles_data.append(col)

        return {
            "width": game_map.width,
            "height": game_map.height,
            "tiles": tiles_data,
            "explored": game_map.explored.tolist(),
            "entities": [
                self._serialize_actor(e) for e in game_map.entities
                if hasattr(e, 'fighter')  # Actor만
            ],
            "items": [self._serialize_item(i) for i in game_map.items],
        }

    def _serialize_quest_log(self, quest_log) -> Dict[str, Any]:
        """QuestLog 직렬화"""
        def serialize_quest(quest):
            return {
                "id": quest.id,
                "name": quest.name,
                "status": quest.status.name,
                "objectives": [
                    {
                        "type": obj.type.name,
                        "target": obj.target,
                        "required": obj.required_count,
                        "current": obj.current_count,
                    }
                    for obj in quest.objectives
                ],
            }

        return {
            "active": [serialize_quest(q) for q in quest_log.active_quests],
            "completed": [serialize_quest(q) for q in quest_log.completed_quests],
            "failed": [serialize_quest(q) for q in quest_log.failed_quests],
        }

    def _serialize_religion(self, religion) -> Dict[str, Any]:
        """Religion 직렬화"""
        return {
            "deity_id": religion.deity.id if religion.deity else None,
            "faith_points": religion.faith_points,
            "favor": religion.favor,
            "prayer_timeout": religion.prayer_timeout,
            "sins": religion.sins,
            "devotion_acts": religion.devotion_acts,
            "active_blessings": dict(religion.active_blessings),
            "active_curses": dict(religion.active_curses),
        }


def reconstruct_engine(save_data: Dict[str, Any]) -> "Engine":
    """
    저장 데이터에서 엔진 재구성

    Args:
        save_data: 저장된 데이터

    Returns:
        재구성된 Engine
    """
    from components.entity import Actor, Item
    from components.fighter import Fighter
    from components.survival import Survival
    from components.inventory import Inventory
    from systems.engine import Engine, GameState
    from systems.game_map import GameMap
    from systems.quest import QuestLog, Quest, QuestObjective, QuestType, QuestStatus
    from systems.religion import Religion, create_deities
    from systems import tile_types
    import numpy as np

    # 플레이어 재구성
    player_data = save_data["player"]
    player = Actor(
        x=player_data["x"],
        y=player_data["y"],
        char=player_data["char"],
        color=tuple(player_data["color"]),
        name=player_data["name"],
        gold=player_data.get("gold", 0),
    )

    # Fighter 컴포넌트
    if "fighter" in player_data:
        f = player_data["fighter"]
        player.fighter = Fighter(hp=f["max_hp"], defense=f["defense"], power=f["power"])
        player.fighter.hp = f["hp"]
        player.fighter.entity = player

    # Survival 컴포넌트
    if "survival" in player_data:
        s = player_data["survival"]
        player.survival = Survival(
            max_hunger=s["max_hunger"],
            max_thirst=s["max_thirst"],
            max_stamina=s["max_stamina"],
        )
        player.survival.hunger = s["hunger"]
        player.survival.thirst = s["thirst"]
        player.survival.stamina = s["stamina"]
        player.survival.body_temp = s["body_temp"]
        player.survival.is_resting = s["is_resting"]
        player.survival.entity = player

    # Inventory 컴포넌트
    if "inventory" in player_data:
        inv = player_data["inventory"]
        player.inventory = Inventory(capacity=inv["capacity"])
        player.inventory.entity = player
        for item_data in inv["items"]:
            item = Item(
                x=item_data["x"],
                y=item_data["y"],
                char=item_data["char"],
                color=tuple(item_data["color"]),
                name=item_data["name"],
                consumable=item_data["consumable"],
                nutrition=item_data["nutrition"],
                hydration=item_data["hydration"],
            )
            player.inventory.add(item)

    # 맵 재구성
    map_data = save_data.get("game_map")
    game_map = None

    if map_data:
        game_map = GameMap(map_data["width"], map_data["height"])

        # 타일 복원
        for x, col in enumerate(map_data["tiles"]):
            for y, tile_data in enumerate(col):
                if tile_data["w"]:  # walkable
                    game_map.tiles[x, y] = tile_types.floor
                else:
                    game_map.tiles[x, y] = tile_types.wall

        # 탐험 상태 복원
        game_map.explored = np.array(map_data["explored"], dtype=bool)

        # 아이템 복원
        for item_data in map_data.get("items", []):
            item = Item(
                x=item_data["x"],
                y=item_data["y"],
                char=item_data["char"],
                color=tuple(item_data["color"]),
                name=item_data["name"],
                consumable=item_data["consumable"],
                nutrition=item_data["nutrition"],
                hydration=item_data["hydration"],
            )
            game_map.add_item(item)

        # 몬스터 복원 (플레이어 제외)
        from components.ai import HostileAI
        for entity_data in map_data.get("entities", []):
            if entity_data["name"] != player.name:
                monster = Actor(
                    x=entity_data["x"],
                    y=entity_data["y"],
                    char=entity_data["char"],
                    color=tuple(entity_data["color"]),
                    name=entity_data["name"],
                    ai=HostileAI(),
                )
                if "fighter" in entity_data:
                    f = entity_data["fighter"]
                    monster.fighter = Fighter(hp=f["max_hp"], defense=f["defense"], power=f["power"])
                    monster.fighter.hp = f["hp"]
                    monster.fighter.entity = monster
                game_map.add_entity(monster)

        # 플레이어 추가
        game_map.add_entity(player)

    # 엔진 생성
    engine = Engine(player=player, game_map=game_map)
    engine.turn_count = save_data["turn_count"]
    engine.hour = save_data["hour"]
    engine.day = save_data["day"]
    engine.environment_temp = save_data["environment_temp"]
    engine.game_state = GameState[save_data["game_state"]]

    # 메시지 로그 복원
    for msg_data in save_data.get("message_log", []):
        engine.message_log.add(msg_data["text"], tuple(msg_data["color"]))

    # 퀘스트 로그 복원
    if "quest_log" in player_data:
        player.quest_log = QuestLog()
        # 간단화를 위해 퀘스트는 새로 시작

    # 종교 복원
    if "religion" in player_data:
        rel_data = player_data["religion"]
        player.religion = Religion()
        if rel_data["deity_id"]:
            deities = create_deities()
            if rel_data["deity_id"] in deities:
                player.religion.deity = deities[rel_data["deity_id"]]
        player.religion.faith_points = rel_data["faith_points"]
        player.religion.favor = rel_data["favor"]
        player.religion.prayer_timeout = rel_data["prayer_timeout"]

    # FOV 업데이트
    engine.update_fov()

    return engine
