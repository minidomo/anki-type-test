from datetime import datetime
from . import config


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

    def html(self):
        assert self.correct_answer
        assert self.user_answer

        content = [
            '<div class="card-stat-entry">',
            self._generate_html_word(self.correct_answer, self.user_answer),
            f"<span>({self.duration():.3f})</span>",
            "</div>",
        ]

        return "\n".join(content)

    def _generate_html_word(self, correct: str, user: str) -> str:
        def determine_color_class(target: str, value: str):
            # not typed #7F848E
            # extra #A2575F
            # correct #98C379
            # wrong #E06C75

            if len(target) == 0:
                return "letter-extra"

            if len(value) == 0:
                return "letter-missing"

            if target == value:
                return "letter-correct"

            return "letter-incorrect"

        def create_span(character: str, color_class: str):
            return f'<span class="{color_class}">{character}</span>'

        ret: list[str] = []

        i = 0
        j = 0

        while i < len(correct) and j < len(user):
            ret.append(
                create_span(correct[i], determine_color_class(correct[i], user[j]))
            )
            i += 1
            j += 1

        while i < len(correct):
            ret.append(create_span(correct[i], determine_color_class(correct[i], "")))
            i += 1

        while j < len(user):
            ret.append(create_span(user[j], determine_color_class("", user[j])))
            j += 1

        return "".join(ret)


class CardStatsQueue:
    def __init__(self):
        self.queue: list[CardStats] = []
        self.history_limit = config.history_limit()

    def create_new_card_stats(self):
        # queue has the current card and isn't complete, so -1 when checking length
        if len(self.queue) - 1 == self.history_limit:
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

    def cleanup(self):
        self.queue.clear()

    def init_state(self):
        self.history_limit = config.history_limit()
