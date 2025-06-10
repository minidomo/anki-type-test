from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt import gui_hooks
from anki.cards import Card
from datetime import datetime
from .card_stats import CardStatsQueue, CardStats

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


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    global card_stats_queue

    if kind != "reviewQuestion":
        return text

    if len(card_stats_queue.queue) > 1:
        history_entries = card_stats_queue.queue[0 : len(card_stats_queue.queue) - 1]
        html_entries = map(CardStats.html, reversed(history_entries))

        content = [
            "<style>",
            ".custom-container {display: flex; flex-direction: column; row-gap: 5px; font-size: 14px;}",
            ".letter-extra {color: #A2575F;}",
            ".letter-missing {color: #7F848E;}",
            ".letter-correct {color: #98C379;}",
            ".letter-incorrect {color: #E06C75;}",
            "</style>",
            '<div class="custom-container">',
            "\n".join(html_entries),
            "</div>",
        ]
        html_str = "\n".join(content)

        return f"{text}\n<br>\n{html_str}"

    return text


def on_reviewer_did_show_question(card: Card):
    global card_stats_queue

    cur = card_stats_queue.current()
    assert cur
    cur.start_time = datetime.now()


def cleanup():
    global card_stats_queue
    card_stats_queue.cleanup()


def on_next_card(self: Reviewer):
    global card_stats_queue
    card_stats_queue.create_new_card_stats()


def init_state(self: Reviewer):
    global card_stats_queue
    card_stats_queue.init_state()


Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer

Reviewer._showAnswer = wrap(Reviewer._showAnswer, store_answers)
Reviewer._showAnswer = wrap(Reviewer._showAnswer, move_to_next_card)

Reviewer.nextCard = wrap(Reviewer.nextCard, on_next_card, "before")

Reviewer.show = wrap(Reviewer.show, init_state, "before")


gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_will_end.append(cleanup)
