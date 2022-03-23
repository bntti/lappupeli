from typing import Optional
from flask import abort
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


def check_room(room_name: str) -> int:
    room_id = get_room_id(room_name)
    if not room_id:
        abort(404, f"Ei huonetta nimellä {room_name}")
    return room_id


# Database functions
def get_room_id(room_name: str) -> Optional[int]:
    sql = "SELECT id FROM rooms WHERE name = :room_name"
    result = database.session.execute(sql, {"room_name": room_name}).fetchone()
    return result[0] if result else None


def get_rooms() -> list[str]:
    sql = "SELECT name FROM rooms"
    result = database.session.execute(sql).fetchall()
    return [row[0] for row in result]


def add_room(room_name: str) -> None:
    try:
        sql = "INSERT INTO rooms (name) VALUES (:room_name)"
        database.session.execute(sql, {"room_name": room_name})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def get_config(room_id: int) -> dict:
    sql = "SELECT current_word, previous_word, admin_username FROM rooms WHERE id = :room_id"
    row = database.session.execute(sql, {"room_id": room_id}).fetchone()
    return {
        "current_word": row[0],
        "previous_word": row[1],
        "admin_username": row[2]
    }


def set_admin(room_id: int, admin_username: str) -> None:
    sql = "UPDATE rooms SET admin_username = :admin_username WHERE id = :room_id"
    database.session.execute(
        sql, {"room_id": room_id, "admin_username": admin_username}
    )
    database.session.commit()


def set_current_word(room_id: int, word: str) -> None:
    sql = "UPDATE rooms SET current_word = :word WHERE id = :room_id"
    database.session.execute(
        sql, {"room_id": room_id, "word": word}
    )
    database.session.commit()


def update_previous_word(room_id: int) -> None:
    sql = "UPDATE rooms SET previous_word = current_word WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()


def delete_room(room_id: int) -> None:
    sql = "DELETE FROM rooms WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()