from typing import Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


# rooms
def get_room_id(room_name: str) -> Optional[int]:
    sql = "SELECT id FROM rooms WHERE name = :room_name"
    result = database.session.execute(sql, {"room_name": room_name}).fetchone()
    return result[0] if result else None


def get_rooms() -> list[dict]:
    sql = "SELECT name, players FROM rooms"
    result = database.session.execute(sql).fetchall()
    return [{"name": row[0], "players": row[1]} for row in result]


def add_room(room_name: str) -> None:
    try:
        sql = "INSERT INTO rooms (name) VALUES (:room_name)"
        database.session.execute(sql, {"room_name": room_name})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def delete_room(room_id: int) -> None:
    sql = "DELETE FROM rooms WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()


def get_config(room_id: int) -> dict:
    sql = "SELECT suggester_uuid, current_word, previous_word, players, admin_uuid FROM rooms WHERE id = :room_id"
    row = database.session.execute(sql, {"room_id": room_id}).fetchone()
    return {
        "suggester_uuid": row[0],
        "current_word": row[1],
        "previous_word": row[2],
        "players": row[3],
        "admin_uuid": row[4]
    }


def next_word(room_id: int, next_word: str, suggester_uuid: UUID) -> None:
    sql = "UPDATE rooms SET previous_word = current_word, " \
          "suggester_uuid = :suggester_uuid, current_word = :next_word " \
          "WHERE id = :room_id"
    database.session.execute(
        sql,
        {
            "room_id": room_id,
            "next_word": next_word,
            "suggester_uuid": suggester_uuid
        }
    )
    database.session.commit()


def set_players(room_id: int, players: int) -> None:
    sql = "UPDATE rooms SET players = :players WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id, "players": players})
    database.session.commit()


def set_admin_uuid(room_id: int, admin_uuid: UUID) -> None:
    sql = "UPDATE rooms SET admin_uuid = :admin_uuid WHERE id = :room_id"
    database.session.execute(
        sql, {"room_id": room_id, "admin_uuid": admin_uuid}
    )
    database.session.commit()


# words
def get_words(room_id: int) -> list:
    sql = "SELECT word FROM words WHERE room_id = :room_id"
    result = database.session.execute(sql, {"room_id": room_id}).fetchall()
    return [a[0] for a in result] if result else []


def add_word(room_id: int, word: str, suggester_uuid: UUID) -> None:
    try:
        sql = "INSERT INTO words (room_id, word, suggester_uuid) VALUES (:room_id, :word, :suggester_uuid)"
        database.session.execute(
            sql,
            {"room_id": room_id, "word": word, "suggester_uuid": suggester_uuid}
        )
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def pop_word(room_id: int) -> tuple[str, UUID]:
    sql = "DELETE FROM words WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM words WHERE room_id = :room_id ORDER BY random() LIMIT 1) RETURNING word, suggester_uuid"
    result = database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
    return result.fetchone()


# player_words
def add_to_player_list(room_id: int, word: str) -> None:
    sql = "INSERT INTO player_words (room_id, word) VALUES (:room_id, :word)"
    database.session.execute(sql, {"room_id": room_id, "word": word})
    database.session.commit()


def add_suggester_to_player_list(room_id: int, word: str, suggester_uuid: UUID) -> None:
    sql = "INSERT INTO player_words (room_id, word, uuid) VALUES (:room_id, :word, :suggester_uuid)"
    database.session.execute(
        sql,
        {"room_id": room_id, "word": word, "suggester_uuid": suggester_uuid}
    )
    database.session.commit()


def get_seen_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id AND uuid IS NOT NULL"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def get_player_list_size(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def has_word(room_id: int, uuid: UUID) -> bool:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id AND uuid = :uuid"
    result = database.session.execute(sql, {"room_id": room_id, "uuid": uuid})
    return result.fetchone()[0] > 0


def give_word(room_id: int, uuid: UUID) -> None:
    sql = "UPDATE player_words SET uuid = :uuid "\
          "WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM player_words WHERE room_id = :room_id AND uuid IS NULL ORDER BY random() LIMIT 1)"
    database.session.execute(sql, {"room_id": room_id, "uuid": uuid})
    database.session.commit()


def get_word(room_id: int, uuid: UUID) -> str:
    sql = "SELECT word FROM player_words WHERE room_id = :room_id AND uuid = :uuid"
    result = database.session.execute(sql, {"room_id": room_id, "uuid": uuid})
    return result.fetchone()[0]


# clear
def clear_player_words(room_id: int) -> None:
    sql = "DELETE FROM player_words WHERE room_id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()


def clear_tables(room_id: int) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id;"\
          "DELETE FROM player_words WHERE room_id = :room_id;"\
          "UPDATE rooms SET previous_word = NULL, current_word = NULL, " \
          "suggester_uuid = NULL WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
