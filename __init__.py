from aqt.reviewer import Reviewer
from anki.hooks import wrap
from typing import Optional


def strip(val: Optional[str]):
    if val is None:
        return val
    return val.strip()


def default_ease(self: Reviewer):
    button_count = self.mw.col.sched.answerButtons(self.card)

    if strip(self.typedAnswer) == strip(self.typeCorrect):
        return button_count

    return 1


def on_typed_answer(self: Reviewer, val: Optional[str]):
    self.typedAnswer = strip(val) or ""

    if len(self.typedAnswer) > 0:
        self._showAnswer()


Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer
