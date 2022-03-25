from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


# Database functions
def is_ready(room_id: int, username: str) -> bool:
    sql = "SELECT COUNT(*) > 0 FROM ready_players WHERE room_id = :room_id AND username = :username"
    result = database.session.execute(
        sql, {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0]


def get_ready_players(room_id: int) -> list[str]:
    sql = "SELECT username FROM ready_players WHERE room_id = :room_id"
    result = database.session.execute(sql, {"room_id": room_id})
    return [row[0] for row in result.fetchall()]


def get_ready_player_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM ready_players WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def set_ready(room_id: int, username: str) -> None:
    try:
        sql = "INSERT INTO ready_players (room_id, username) VALUES (:room_id, :username)"
        database.session.execute(
            sql, {"room_id": room_id, "username": username}
        )
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def set_not_ready(room_id: int, username: str) -> None:
    sql = "DELETE FROM ready_players WHERE room_id = :room_id AND username = :username"
    database.session.execute(sql, {"room_id": room_id, "username": username})
    database.session.commit()


def set_player_to_not_ready(username: str) -> None:
    sql = "DELETE FROM ready_players WHERE username = :username"
    database.session.execute(sql, {"username": username})
    database.session.commit()


def set_room_to_not_ready(room_id: int) -> None:
    sql = "DELETE FROM ready_players WHERE room_id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
