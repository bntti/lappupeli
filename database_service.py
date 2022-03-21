from typing import Optional
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


# rooms
def get_room_id(room_name: str) -> Optional[int]:
    sql = "SELECT id FROM rooms WHERE name = :room_name"
    result = database.session.execute(sql, {"room_name": room_name}).fetchone()
    return result[0] if result else None


def get_rooms() -> list[dict]:
    sql = "SELECT name, player_count FROM rooms"
    result = database.session.execute(sql).fetchall()
    return [{"name": row[0], "player_count": row[1]} for row in result]


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
    sql = "SELECT suggester_username, current_word, previous_word, player_count, admin_username FROM rooms WHERE id = :room_id"
    row = database.session.execute(sql, {"room_id": room_id}).fetchone()
    return {
        "suggester_username": row[0],
        "current_word": row[1],
        "previous_word": row[2],
        "player_count": row[3],
        "admin_username": row[4]
    }


def next_word(room_id: int, next_word: str, suggester_username: str) -> None:
    sql = "UPDATE rooms SET previous_word = current_word, " \
          "suggester_username = :suggester_username, current_word = :next_word " \
          "WHERE id = :room_id"
    database.session.execute(
        sql,
        {
            "room_id": room_id,
            "next_word": next_word,
            "suggester_username": suggester_username
        }
    )
    database.session.commit()


def set_player_count(room_id: int, player_count: int) -> None:
    sql = "UPDATE rooms SET player_count = :player_count WHERE id = :room_id"
    database.session.execute(
        sql, {"room_id": room_id, "player_count": player_count}
    )
    database.session.commit()


def set_admin(room_id: int, admin_username: str) -> None:
    sql = "UPDATE rooms SET admin_username = :admin_username WHERE id = :room_id"
    database.session.execute(
        sql, {"room_id": room_id, "admin_username": admin_username}
    )
    database.session.commit()


# words
def get_words(room_id: int) -> list:
    sql = "SELECT word FROM words WHERE room_id = :room_id"
    result = database.session.execute(sql, {"room_id": room_id}).fetchall()
    return [a[0] for a in result] if result else []


def add_word(room_id: int, word: str, suggester_username: str) -> None:
    try:
        sql = "INSERT INTO words (room_id, word, suggester_username) VALUES (:room_id, :word, :suggester_username)"
        database.session.execute(
            sql,
            {
                "room_id": room_id,
                "word": word,
                "suggester_username": suggester_username
            }
        )
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def pop_word(room_id: int) -> tuple[str, str]:
    sql = "DELETE FROM words WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM words WHERE room_id = :room_id ORDER BY random() LIMIT 1) RETURNING word, suggester_username"
    result = database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
    return result.fetchone()


# player_words
def add_to_player_list(room_id: int, word: str) -> None:
    sql = "INSERT INTO player_words (room_id, word) VALUES (:room_id, :word)"
    database.session.execute(sql, {"room_id": room_id, "word": word})
    database.session.commit()


def add_suggester_to_player_list(room_id: int, word: str, suggester_username: str) -> None:
    sql = "INSERT INTO player_words (room_id, word, assigned_to) VALUES (:room_id, :word, :suggester_username)"
    database.session.execute(
        sql,
        {"room_id": room_id, "word": word, "suggester_username": suggester_username}
    )
    database.session.commit()


def get_seen_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id AND assigned_to IS NOT NULL"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def get_player_list_size(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def has_word(room_id: int, username: str) -> bool:
    sql = "SELECT COUNT(*) FROM player_words WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql, {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0] > 0


def give_word(room_id: int, username: str) -> None:
    sql = "UPDATE player_words SET assigned_to = :username "\
          "WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM player_words WHERE room_id = :room_id AND assigned_to IS NULL ORDER BY random() LIMIT 1)"
    database.session.execute(sql, {"room_id": room_id, "username": username})
    database.session.commit()


def get_word(room_id: int, username: str) -> str:
    sql = "SELECT word FROM player_words WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql,
        {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0]


# clear
def clear_player_words(room_id: int) -> None:
    sql = "DELETE FROM player_words WHERE room_id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()


def reset_room(room_id: int) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id;"\
          "DELETE FROM player_words WHERE room_id = :room_id;"\
          "UPDATE rooms SET previous_word = NULL, current_word = NULL, " \
          "suggester_username = NULL WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
