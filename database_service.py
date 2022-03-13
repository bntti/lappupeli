from uuid import UUID
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from database import database


# words
def get_words() -> list:
    sql = "SELECT word FROM words"
    result = database.session.execute(sql).fetchall()
    return [a[0] for a in result] if result else []


def add_word(word: str, suggester_uuid: UUID) -> None:
    try:
        sql = "INSERT INTO words (word, suggester_uuid) VALUES (:word, :suggester_uuid)"
        database.session.execute(
            sql, {"word": word, "suggester_uuid": suggester_uuid}
        )
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def pop_word() -> tuple[str, UUID]:
    sql = "DELETE FROM words WHERE id = (SELECT id FROM words ORDER BY random() LIMIT 1) RETURNING word, suggester_uuid"
    word, suggester_uuid = database.session.execute(sql).fetchone()
    database.session.commit()
    return word, suggester_uuid


# config
def get_config() -> dict:
    sql = "SELECT suggester_uuid, current_word, previous_word, players, admin_uuid FROM config"
    row = database.session.execute(sql).fetchone()
    return {
        "suggester_uuid": row[0],
        "current_word": row[1],
        "previous_word": row[2],
        "players": row[3],
        "admin_uuid": row[4]
    }


def next_word(next_word: str, suggester_uuid: UUID) -> None:
    sql = "UPDATE config SET previous_word = current_word, " \
          "suggester_uuid = :suggester_uuid, current_word = :next_word"
    database.session.execute(
        sql, {"next_word": next_word, "suggester_uuid": suggester_uuid}
    )
    database.session.commit()


def set_players(players: int) -> None:
    sql = "UPDATE config SET players = :players"
    database.session.execute(sql, {"players": players})
    database.session.commit()


def set_admin_uuid(admin_uuid: UUID) -> None:
    sql = "UPDATE config SET admin_uuid = :admin_uuid"
    database.session.execute(sql, {"admin_uuid": admin_uuid})
    database.session.commit()


# player_words
def add_to_player_list(word: str) -> None:
    sql = "INSERT INTO player_words (word) VALUES (:word)"
    database.session.execute(sql, {"word": word})
    database.session.commit()


def add_suggester_to_player_list(word: str, suggester_uuid: UUID) -> None:
    sql = "INSERT INTO player_words (word, uuid) VALUES (:word, :suggester_uuid)"
    database.session.execute(
        sql, {"word": word, "suggester_uuid": suggester_uuid}
    )
    database.session.commit()


def get_seen_count() -> int:
    sql = "SELECT COUNT(*) FROM player_words WHERE uuid IS NOT NULL"
    return database.session.execute(sql).fetchone()[0]


def get_player_list_size() -> int:
    sql = "SELECT COUNT(*) FROM player_words"
    return database.session.execute(sql).fetchone()[0]


def has_word(uuid: UUID) -> bool:
    sql = "SELECT COUNT(*) FROM player_words WHERE uuid = :uuid"
    result = database.session.execute(sql, {"uuid": uuid})
    return result.fetchone()[0] > 0


def give_word(uuid: UUID) -> None:
    sql = "UPDATE player_words SET uuid = :uuid WHERE id = (SELECT id FROM player_words WHERE uuid IS NULL ORDER BY random() LIMIT 1)"
    database.session.execute(sql, {"uuid": uuid})
    database.session.commit()


def get_word(uuid: UUID) -> str:
    sql = "SELECT word FROM player_words WHERE uuid = :uuid"
    result = database.session.execute(sql, {"uuid": uuid})
    return result.fetchone()[0]


# clear
def clear_player_words() -> None:
    sql = "DELETE FROM player_words"
    database.session.execute(sql)
    database.session.commit()


def clear_tables() -> None:
    sql = "DELETE FROM words;"\
          "DELETE FROM player_words;"\
          "UPDATE config SET previous_word = NULL, current_word = NULL, suggester_uuid = NULL"
    database.session.execute(sql)
    database.session.commit()
