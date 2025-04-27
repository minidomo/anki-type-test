from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt import gui_hooks
from anki.cards import Card
from datetime import datetime
from .card_stats import CardStatsQueue

card_stats_queue = CardStatsQueue()


def strip(val: str | None):
    if val is None:
        return val
    return val.strip()


def default_ease(self: Reviewer):
    assert self.card
    assert self.mw.col

    button_count = self.mw.col.sched.answerButtons(self.card)

    if self.typedAnswer is not None and strip(self.typedAnswer) == strip(
        self.typeCorrect
    ):
        return button_count

    return 1


def on_typed_answer(self: Reviewer, val: str | None):
    global card_stats_queue

    self.typedAnswer = strip(val) or ""

    if len(self.typedAnswer) > 0:
        cur = card_stats_queue.current()
        assert cur
        cur.end_time = datetime.now()
        self._showAnswer()


def move_to_next_card(self: Reviewer):
    self._answerCard(self._defaultEase())


def store_answers(self: Reviewer):
    global card_stats_queue

    cur = card_stats_queue.current()
    assert cur
    cur.correct_answer = strip(self.typeCorrect)
    cur.user_answer = strip(self.typedAnswer)


def generate_html_word(correct: str, user: str) -> str:
    def determine_color(target: str, value: str):
        # not typed #7F848E
        # extra #A2575F
        # correct #98C379
        # wrong #E06C75

        if len(target) == 0:
            return "#A2575F"

        if len(value) == 0:
            return "#7F848E"

        if target == value:
            return "#98C379"

        return "#E06C75"

    def create_span(character: str, color: str):
        return f'<span style="font-size: 14px; color: {color};">{character}</span>'

    ret: list[str] = []

    i = 0
    j = 0

    while i < len(correct) and j < len(user):
        ret.append(create_span(correct[i], determine_color(correct[i], user[j])))
        i += 1
        j += 1

    while i < len(correct):
        ret.append(create_span(correct[i], determine_color(correct[i], "")))
        i += 1

    while j < len(user):
        ret.append(create_span(user[j], determine_color("", user[j])))
        j += 1

    return "".join(ret)


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    global card_stats_queue
    global previous_answer
    global previous_user_answer

    if kind != "reviewQuestion":
        return text

    prev = card_stats_queue.previous()
    if prev is not None:
        assert prev.correct_answer
        assert prev.user_answer

        time = f'<span style="font-size: 14px;">({prev.duration():.3f})</span>'
        return f"{text}\n<br>\n{generate_html_word(prev.correct_answer, prev.user_answer)} {time}"

    return text


def on_reviewer_did_show_question(card: Card):
    global card_stats_queue

    cur = card_stats_queue.current()
    assert cur
    cur.start_time = datetime.now()


def reset_state():
    global card_stats_queue
    card_stats_queue.reset()


def on_next_card(self: Reviewer):
    global card_stats_queue
    card_stats_queue.create_new_card_stats()


Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer

Reviewer._showAnswer = wrap(Reviewer._showAnswer, store_answers)
Reviewer._showAnswer = wrap(Reviewer._showAnswer, move_to_next_card)

Reviewer.nextCard = wrap(Reviewer.nextCard, on_next_card, "before")


gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_will_end.append(reset_state)
