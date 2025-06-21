class CardStats:
    def __init__(self):
        self.card_id: int = -1
        self.correct_answer: str | None = None
        self.user_answer: str | None = None
        self.start_time: float | None = None
        self.end_time: float | None = None

    def is_user_correct(self):
        return self.user_answer == self.correct_answer

    def duration(self) -> float:
        if self.end_time is None or self.start_time is None:
            return 0
        delta = self.end_time - self.start_time
        return delta

    def correct_characters(self):
        i = 0
        j = 0
        correct_chars = 0

        assert self.correct_answer
        assert self.user_answer

        while i < len(self.correct_answer) and j < len(self.user_answer):
            if self.correct_answer[i] == self.user_answer[j]:
                correct_chars += 1
            i += 1
            j += 1

        return correct_chars

    def wpm(self):
        return (self.correct_characters() * 60 / self.duration()) / 5

    def accuracy(self):
        assert self.user_answer
        return self.correct_characters() / len(self.user_answer) * 100

    def html(self):
        assert self.correct_answer
        assert self.user_answer

        return f"""
<div class="card-stat-entry">
    {self._generate_html_word(self.correct_answer, self.user_answer)}
    <span class="card-stat-duration">({self.duration():.3f})</span>
</div>
"""

    def _generate_html_word(self, correct: str, user: str) -> str:
        def determine_color_class(target: str, value: str):
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

    def __str__(self):
        return f"{{ {self.card_id}, {self.correct_answer}, {self.user_answer}, {self.duration():.3f}, {self.wpm():.3f}, {self.accuracy():.3f} }}"
