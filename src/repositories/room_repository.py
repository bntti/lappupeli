from typing import Optional

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from database import database


def get_room_id(room_name: str) -> Optional[int]:
    sql = "SELECT id FROM rooms WHERE name = :room_name"
    result = database.session.execute(text(sql), {"room_name": room_name}).fetchone()
    return result[0] if result else None


def get_rooms() -> list[str]:
    sql = "SELECT name FROM rooms"
    result = database.session.execute(text(sql)).fetchall()
    return [row[0] for row in result]


def add_room(room_name: str) -> None:
    try:
        sql = "INSERT INTO rooms (name) VALUES (:room_name)"
        database.session.execute(text(sql), {"room_name": room_name})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def get_config(room_id: int) -> dict:
    sql = "SELECT current_word, previous_word, admin_username, starter_username FROM rooms WHERE id = :room_id"
    row = database.session.execute(text(sql), {"room_id": room_id}).fetchone()
    return {
        "current_word": row[0],
        "previous_word": row[1],
        "admin_username": row[2],
        "starter_username": row[3],
    }


def set_admin(room_id: int, admin_username: Optional[str]) -> None:
    sql = "UPDATE rooms SET admin_username = :admin_username WHERE id = :room_id"
    database.session.execute(
        text(sql), {"room_id": room_id, "admin_username": admin_username}
    )
    database.session.commit()


def set_starter(room_id: int, starter_username: str) -> None:
    sql = "UPDATE rooms SET starter_username = :starter_username WHERE id = :room_id"
    database.session.execute(
        text(sql), {"room_id": room_id, "starter_username": starter_username}
    )
    database.session.commit()


def set_current_word(room_id: int, word: str) -> None:
    sql = "UPDATE rooms SET current_word = :word WHERE id = :room_id"
    database.session.execute(text(sql), {"room_id": room_id, "word": word})
    database.session.commit()


def update_previous_word(room_id: int) -> None:
    sql = "UPDATE rooms SET previous_word = current_word WHERE id = :room_id"
    database.session.execute(text(sql), {"room_id": room_id})
    database.session.commit()


def delete_room(room_id: int) -> None:
    sql = "DELETE FROM rooms WHERE id = :room_id"
    database.session.execute(text(sql), {"room_id": room_id})
    database.session.commit()


def reset_room(room_id: int) -> None:
    sql = (
        "UPDATE rooms SET previous_word = NULL, current_word = NULL WHERE id = :room_id"
    )
    database.session.execute(text(sql), {"room_id": room_id})
    database.session.commit()
