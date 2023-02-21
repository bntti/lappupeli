import random

from flask import abort, session

from repositories import (
    card_repository,
    player_repository,
    room_repository,
    word_repository,
)

EMPTY_CARD = "Sait tyhjän lapun!"


def check_room(room_name: str) -> int:
    room_id = room_repository.get_room_id(room_name)
    if not room_id:
        abort(404, f"Ei huonetta nimellä {room_name}")
    return room_id


def check_user() -> str:
    if "username" not in session:
        abort(401)
    return session["username"]


def add_word(room_id: int, word: str, suggester_username: str) -> None:
    if 0 < len(word) <= 64:
        word_repository.add_word(room_id, word, suggester_username)
    else:
        abort(400, "Sana ei saa olla tyhjä ja sen pituus saa olla enintään 64 merkkiä")


def add_room(room_name: str) -> None:
    if 0 < len(room_name) <= 32:
        room_repository.add_room(room_name)
    else:
        abort(
            400,
            "Huoneen nimi ei saa olla tyhjä ja sen pituus saa olla enintään 32 merkkiä",
        )


def get_card(room_id: int, username: str) -> str:
    if card_repository.get_card_count(room_id) == 0:
        return "Kierros on loppunut / ei ole vielä alkanut"
    if not card_repository.has_card(room_id, username):
        return "Et ole kierroksella mukana"

    card = card_repository.get_card(room_id, username)
    card_repository.set_seen(room_id, username)
    return card


def round_in_progress(room_id: int) -> bool:
    return card_repository.get_card_count(room_id) > 0


def start_round(room_id: int) -> None:
    words = word_repository.get_words(room_id)
    players = player_repository.get_players(room_id)
    player_count = len(players)

    if len(words) == 0 or not 2 <= player_count <= 64:
        abort(
            400,
            "Sanamäärän pitää olla yli 0 ja pelaajamäärän pitää olla vähintään 2 ja enintään 64",
        )

    if random.randint(1, 10 * player_count) == 1:
        next_word, suggester_username = (EMPTY_CARD, None)
    else:
        random.shuffle(words)
        next_word, suggester_username = words.pop()
        word_repository.remove_word(room_id, next_word)

    cards = [EMPTY_CARD]
    for _ in range(player_count - 2):
        cards.append(next_word)
    if not suggester_username or suggester_username not in players:
        cards.append(next_word)
    random.shuffle(cards)

    for username in players:
        if username == suggester_username:
            card_repository.add_card(room_id, next_word, username)
        else:
            card_repository.add_card(room_id, cards.pop(), username)

    room_repository.set_starter(room_id, random.choice(players))
    room_repository.set_current_word(room_id, next_word)


def end_round(room_id: int) -> None:
    card_repository.delete_all(room_id)
    room_repository.update_previous_word(room_id)


def reset_room(room_id: int) -> None:
    card_repository.delete_all(room_id)
    word_repository.delete_all(room_id)
    player_repository.delete_all(room_id)
    room_repository.reset_room(room_id)
