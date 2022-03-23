from database import database


def get_card(room_id: int, username: str) -> str:
    if get_card_count(room_id) == 0:
        return "Kierros on loppunut / ei ole vielä alkanut"
    if not has_card(room_id, username):
        return "Et ole kierroksella mukana"

    card = db_get_card(room_id, username)
    set_seen(room_id, username)
    return card


def add_card(room_id: int, word: str, username: str) -> None:
    sql = "INSERT INTO cards (room_id, word, assigned_to) VALUES (:room_id, :word, :username)"
    database.session.execute(
        sql,
        {"room_id": room_id, "word": word, "username": username}
    )
    database.session.commit()


def get_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def get_seen_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND seen = True"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def has_card(room_id: int, username: str) -> bool:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql, {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0] > 0


def set_seen(room_id: int, username: str) -> None:
    sql = "Update cards SET seen = True WHERE room_id = :room_id AND assigned_to = :username"
    database.session.execute(sql, {"room_id": room_id, "username": username})
    database.session.commit()


def has_seen_card(room_id: int, username: str) -> bool:
    sql = "SELECT seen FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql, {"room_id": room_id, "username": username}
    ).fetchone()
    return result[0] if result else False


def db_get_card(room_id: int, username: str) -> str:
    sql = "SELECT word FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql,
        {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0]


def clear_cards(room_id: int) -> None:
    sql = "DELETE FROM cards WHERE room_id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
