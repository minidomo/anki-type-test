from aqt.reviewer import Reviewer
from anki.hooks import wrap
from typing import Optional


def strip(val: Optional[str]):
    if val is None:
        return val
    return val.strip()


def default_ease(self: Reviewer):
    assert self.card is not None
    assert self.mw.col is not None

    button_count = self.mw.col.sched.answerButtons(self.card)

    if self.typedAnswer is not None and strip(self.typedAnswer) == strip(
        self.typeCorrect
    ):
        return button_count

    return 1


def on_typed_answer(self: Reviewer, val: Optional[str]):
    self.typedAnswer = strip(val) or ""

    if len(self.typedAnswer) > 0:
        self._showAnswer()


def move_to_next_card(self: Reviewer):
    self._answerCard(self._defaultEase())


Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer

Reviewer._showAnswer = wrap(Reviewer._showAnswer, move_to_next_card)
