from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


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
