from .card_stats import CardStats
from statistics import median, mean


class ReviewStats:
    def __init__(self):
        self.cards: list[CardStats] = []
        self.active_card: CardStats | None = None

    def total_time(self):
        return sum(map(CardStats.duration, self.cards))

    def average_time(self):
        return mean(map(CardStats.duration, self.cards))

    def median_time(self):
        return median(sorted(map(CardStats.duration, self.cards)))

    def total_attempts(self):
        return len(self.cards)

    def correct_attempts(self):
        return sum(1 for _ in self.correct_attempts_it())

    def incorrect_attempts(self):
        return sum(1 for _ in self.incorrect_attempts_it())

    def correct_attempts_it(self):
        return filter(CardStats.is_user_correct, self.cards)

    def incorrect_attempts_it(self):
        return filter(lambda card: not card.is_user_correct(), self.cards)

    def card_accuracy(self):
        return self.correct_attempts() / self.total_attempts() * 100

    def get_displayed_cards(self, limit: int) -> list[CardStats]:
        return self.cards[-limit:]

    def finish_active_card(self):
        assert self.active_card
        self.cards.append(self.active_card)
        self.active_card = None

    def prepare_new_active_card(self):
        assert self.active_card is None
        self.active_card = CardStats()

    def __str__(self):
        return f"""
review stats
total attempts: {self.total_attempts()}
correct: {self.correct_attempts()}
incorrect: {self.incorrect_attempts()}
accuracy: {self.card_accuracy():.3f}%
total time: {self.total_time():.3f}
average time: {self.average_time():.3f}
median time: {self.median_time():.3f}
"""
