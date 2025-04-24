# from anki.collection import Collection
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from anki.cards import Card
from anki.hooks import wrap

# col = Collection("C:/Users/domob/AppData/Roaming/Anki2/User 1/collection.anki2")
# print(col.sched.deck_due_tree())


def will_init_answer_buttons(
    buttons_tuple: tuple[tuple[int, str], ...], reviewer: Reviewer, card: Card
):
    print(reviewer.typeCorrect, reviewer.typedAnswer)

    return buttons_tuple


def strip_whitespace_from_typed_answer(self: Reviewer):
    print(f"current: {self.typedAnswer}")
    if self.typedAnswer is not None:
        self.typedAnswer = self.typedAnswer.strip()
    print(f"after: {self.typedAnswer}")


def test(self: Reviewer):
    print("after on typed answer")


def test2(self: Reviewer):
    print("after answer button list")


# Reviewer._showAnswer = wrap(
#     Reviewer._showAnswer, strip_whitespace_from_typed_answer, "before"
# )

# Reviewer._onTypedAnswer = wrap(Reviewer._onTypedAnswer, test)
# Reviewer._answerButtonList = wrap(Reviewer._answerButtonList, test2)


def reviewer_init(reviewer: Reviewer):
    print("reviewer init")
    reviewer._answerButtonList = wrap(reviewer._answerButtonList, test2)


gui_hooks.reviewer_will_init_answer_buttons.append(will_init_answer_buttons)
gui_hooks.reviewer_did_init.append(reviewer_init)

print("anki-test-type loaded")