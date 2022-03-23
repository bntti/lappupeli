import random
from flask import session
from database import database
import services.card_service as card_service
import services.room_service as room_service
import services.word_service as word_service

EMPTY_CARD = "Sait tyhjän lapun!"


# Normal functions
def next_word(room_id: int) -> None:
    words = word_service.get_words(room_id)
    if len(words) == 0:
        return

    player_count = room_service.get_config(room_id)["player_count"]
    card_service.clear_cards(room_id)

    r = random.randint(1, 10)
    if r == 1:
        next_word, suggester_username = (EMPTY_CARD, None)
    else:
        next_word, suggester_username = word_service.pop_word(room_id)

    for _ in range(player_count - 2):
        card_service.add_card(room_id, next_word)
    if not suggester_username:
        card_service.add_card(room_id, next_word)
    card_service.add_card(room_id, EMPTY_CARD)
    start_round(room_id, next_word, suggester_username)


def get_word(room_id: int) -> str:
    config = room_service.get_config(room_id)

    if card_service.has_card(room_id, session["username"]):
        return card_service.get_card(room_id, session["username"])
    if session["username"] == config["suggester_username"]:
        card_service.add_seen_card(
            room_id, config["current_word"], config["suggester_username"]
        )
        return config["current_word"]
    if card_service.get_card_count(room_id) == 0:
        return "Peli ei ole vielä alkanut"
    if card_service.get_card_count(room_id) == card_service.get_seen_card_count(room_id):
        if card_service.get_seen_card_count(room_id) != config['player_count']:
            # The suggester left the game (hopefully)
            card_service.add_seen_card(
                room_id, config["current_word"], session["username"]
            )
            return config["current_word"]
        return f"Lappuja on jo jaettu {config['player_count']} kpl"

    card_service.give_card(room_id, session["username"])
    return card_service.get_card(room_id, session["username"])


# Database functions
def start_round(room_id: int, next_word: str, suggester_username: str) -> None:
    sql = "UPDATE rooms SET previous_word = current_word, " \
          "suggester_username = :suggester_username, current_word = :next_word " \
          "WHERE id = :room_id"
    database.session.execute(
        sql,
        {
            "room_id": room_id,
            "next_word": next_word,
            "suggester_username": suggester_username
        }
    )
    database.session.commit()


def reset_game(room_id: int) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id;"\
          "DELETE FROM cards WHERE room_id = :room_id;"\
          "UPDATE rooms SET previous_word = NULL, current_word = NULL, " \
          "suggester_username = NULL WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
