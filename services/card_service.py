from database import database


def add_card(room_id: int, word: str) -> None:
    sql = "INSERT INTO cards (room_id, word) VALUES (:room_id, :word)"
    database.session.execute(sql, {"room_id": room_id, "word": word})
    database.session.commit()


def add_seen_card(room_id: int, word: str, username: str) -> None:
    sql = "INSERT INTO cards (room_id, word, assigned_to) VALUES (:room_id, :word, :username)"
    database.session.execute(
        sql,
        {"room_id": room_id, "word": word, "username": username}
    )
    database.session.commit()


def get_seen_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND assigned_to IS NOT NULL"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def get_card_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


def has_card(room_id: int, username: str) -> bool:
    sql = "SELECT COUNT(*) FROM cards WHERE room_id = :room_id AND assigned_to = :username"
    result = database.session.execute(
        sql, {"room_id": room_id, "username": username}
    )
    return result.fetchone()[0] > 0


def give_card(room_id: int, username: str) -> None:
    sql = "UPDATE cards SET assigned_to = :username WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM cards WHERE room_id = :room_id AND assigned_to IS NULL ORDER BY random() LIMIT 1)"
    database.session.execute(sql, {"room_id": room_id, "username": username})
    database.session.commit()


def get_card(room_id: int, username: str) -> str:
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
