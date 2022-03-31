from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


def get_words(room_id: int) -> list:
    sql = "SELECT word, suggester_username FROM words WHERE room_id = :room_id"
    result = database.session.execute(sql, {"room_id": room_id}).fetchall()
    return [(row[0], row[1]) for row in result] if result else []


def get_word_count(room_id: int) -> int:
    sql = "SELECT COUNT(*) FROM words WHERE room_id = :room_id"
    return database.session.execute(sql, {"room_id": room_id}).fetchone()[0]


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


def remove_word(room_id: int, word: str) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id AND word = :word"
    database.session.execute(sql, {"room_id": room_id, "word": word})
    database.session.commit()


def delete_all(room_id: int) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
