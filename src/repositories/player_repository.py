from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from database import database


def join_room(room_id: int, username: str) -> None:
    try:
        sql = "INSERT INTO players (room_id, username) VALUES (:room_id, :username)"
        database.session.execute(text(sql), {"room_id": room_id, "username": username})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def leave_rooms(username: str) -> None:
    sql = "DELETE FROM players WHERE username = :username"
    database.session.execute(text(sql), {"username": username})
    database.session.commit()


def get_players(room_id: int) -> list[str]:
    sql = "SELECT username FROM players WHERE room_id = :room_id"
    result = database.session.execute(text(sql), {"room_id": room_id})
    return [row[0] for row in result.fetchall()]


def get_player_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM players WHERE room_id = :room_id"
    return database.session.execute(text(sql), {"room_id": room_id}).fetchone()[0]


def delete_all(room_id: int) -> None:
    sql = "DELETE FROM players WHERE room_id = :room_id"
    database.session.execute(text(sql), {"room_id": room_id})
    database.session.commit()
