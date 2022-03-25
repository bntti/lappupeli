import random
from flask import abort
from database import database
import services.card_service as card_service
import services.room_service as room_service
import services.word_service as word_service
import services.ready_players_service as rps

EMPTY_CARD = "Sait tyhjän lapun!"


# Normal functions
def start_round(room_id: int) -> None:
    words = word_service.get_words(room_id)
    ready_players = rps.get_ready_players(room_id)
    ready_count = len(ready_players)

    if len(words) == 0 or ready_count < 2 or ready_count > 100:
        abort(400, "Sanamäärän pitää olla yli 0 ja pelaajamäärän pitää olla vähintään 2 ja enintään 100")

    r = random.randint(1, 10)
    if r == 1:
        next_word, suggester_username = (EMPTY_CARD, None)
    else:
        random.shuffle(words)
        next_word, suggester_username = words.pop()
        word_service.remove_word(room_id, next_word)

    cards = [EMPTY_CARD]
    for _ in range(ready_count - 2):
        cards.append(next_word)
    if not suggester_username or suggester_username not in ready_players:
        cards.append(next_word)
    random.shuffle(cards)

    for username in ready_players:
        if username == suggester_username:
            card_service.add_card(room_id, next_word, username)
        else:
            card_service.add_card(room_id, cards.pop(), username)

    room_service.set_current_word(room_id, next_word)
    rps.set_room_to_not_ready(room_id)


def end_round(room_id: int) -> None:
    card_service.clear_cards(room_id)
    room_service.update_previous_word(room_id)


def give_card(room_id: int, username: str) -> None:
    sql = "UPDATE cards SET assigned_to = :username WHERE room_id = :room_id " \
          "AND id = (SELECT id FROM cards WHERE room_id = :room_id AND assigned_to IS NULL ORDER BY random() LIMIT 1)"
    database.session.execute(sql, {"room_id": room_id, "username": username})
    database.session.commit()


# Database functions
def reset_game(room_id: int) -> None:
    sql = "DELETE FROM words WHERE room_id = :room_id;"\
          "DELETE FROM cards WHERE room_id = :room_id;"\
          "UPDATE rooms SET previous_word = NULL, current_word = NULL WHERE id = :room_id"
    database.session.execute(sql, {"room_id": room_id})
    database.session.commit()
