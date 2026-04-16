from database import database
from sqlalchemy.sql import text
from util import ann


def add_card(room_id: int, word: str, username: str) -> None:
    sql = "INSERT INTO cards (room_id, word, assigned_to) VALUES (:room_id, :word, :username)"
    database.session.execute(
        text(sql),
        {"room_id": room_id, "word": word, "username": username},
    )
    database.session.commit()


def get_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id"
    return ann(database.session.execute(text(sql), {"room_id": room_id}).fetchone())[0]


def get_seen_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND seen = True"
    return ann(database.session.execute(text(sql), {"room_id": room_id}).fetchone())[0]


def has_card(room_id: int, username: str) -> bool:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        text(sql),
        {"room_id": room_id, "username": username},
    )
    return ann(result.fetchone())[0] > 0


def set_seen(room_id: int, username: str) -> None:
    sql = "Update cards SET seen = True WHERE room_id = :room_id AND assigned_to = :username"
    database.session.execute(text(sql), {"room_id": room_id, "username": username})
    database.session.commit()


def has_seen_card(room_id: int, username: str) -> bool:
    sql = "SELECT seen FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        text(sql),
        {"room_id": room_id, "username": username},
    ).fetchone()
    return result[0] if result else False


def get_card(room_id: int, username: str) -> str:
    sql = "SELECT word FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        text(sql),
        {"room_id": room_id, "username": username},
    )
    return ann(result.fetchone())[0]


def delete_all(room_id: int) -> None:
    sql = "DELETE FROM cards WHERE room_id = :room_id"
    database.session.execute(text(sql), {"room_id": room_id})
    database.session.commit()
