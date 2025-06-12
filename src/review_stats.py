from .card_stats import CardStats


class ReviewStats:
    def __init__(self):
        self.cards: list[CardStats] = []
        self.active_card: CardStats | None = None

    def get_displayed_cards(self, limit: int) -> list[CardStats]:
        return self.cards[-limit:]

    def finish_active_card(self):
        assert self.active_card
        self.cards.append(self.active_card)
        self.active_card = None

    def prepare_new_active_card(self):
        assert self.active_card is None
        self.active_card = CardStats()
