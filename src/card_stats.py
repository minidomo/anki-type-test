from datetime import datetime


class CardStats:
    def __init__(self):
        self.correct_answer: str | None = None
        self.user_answer: str | None = None
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    def duration(self) -> float:
        if self.end_time is None or self.start_time is None:
            return 0
        delta = self.end_time - self.start_time
        return delta.total_seconds()


class CardStatsQueue:
    def __init__(self):
        self.queue: list[CardStats] = []
        self.history_limit = 5

    def create_new_card_stats(self):
        if len(self.queue) == self.history_limit:
            self.queue.pop(0)

        self.queue.append(CardStats())

    def current(self):
        if len(self.queue) == 0:
            return None
        return self.queue[-1]

    def previous(self):
        if len(self.queue) <= 1:
            return None
        return self.queue[-2]

    def reset(self):
        self.queue.clear()
