from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.main import MainWindowState
from aqt.webview import AnkiWebView
from aqt import gui_hooks
from anki.cards import Card
from datetime import datetime
from .card_stats import CardStatsQueue, CardStats
from . import config
import re

card_stats_queue = CardStatsQueue()
finished_review = False


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
        html_entries_str = "\n".join(map(CardStats.html, reversed(history_entries)))

        html_str = f"""
<style>
    .custom-container {{
        display: flex;
        flex-direction: column;
        row-gap: 5px;
        font-size: .7em;
    }}

    .letter-extra {{ color: {config.word_stat_color_letter_extra()};}}
    .letter-missing {{ color: {config.word_stat_color_letter_missing()};}}
    .letter-correct {{ color: {config.word_stat_color_letter_correct()};}}
    .letter-incorrect {{ color: {config.word_stat_color_letter_incorrect()};}}
    .card-stat-duration {{ color: {config.word_stat_color_duration()};}}
</style>
<div class="custom-container">
    {html_entries_str}
</div>
"""

        return f"{text}\n{html_str}"

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
    pass


old_type_ans_question_filter = Reviewer.typeAnsQuestionFilter


def type_ans_question_filter(self: Reviewer, buf: str) -> str:
    res = old_type_ans_question_filter(self, buf)

    if not self.typeCorrect:
        return res

    initial_width = "10em"

    content = f"""
<style>
    .type-area {{
        display: flex;
        justify-content: center;
        
        
        & span {{
            position: absolute;
            left: -1e6px;
            display: inline-block;
            min-width: {initial_width};
        }}

        & * {{
            font-size: 1em;
            font-family: inherit;
            border: 2px solid #666;
        }}
    }}

    #typeans {{
        width: {initial_width};
        padding: .5em 1em;
        border-radius: 2em;
        outline: 0;
        box-sizing: content-box;
        text-align: center;
    }}
</style>

<div class="type-area">
    <input type=text id=typeans onkeypress="_typeAnsPress();">
    <span></span>
</div>

<script>
    (() => {{
        const input = document.querySelector('#typeans');
        const span = document.querySelector('.type-area > span');

        input.addEventListener('input', function (event) {{
            span.innerHTML = this.value.replace(/\\\\s/g, '&nbsp;');

            const sStyles = window.getComputedStyle(span);
            const sWidth = Number.parseInt(sStyles.width);

            const pStyles = window.getComputedStyle(this.parentElement);
            const pWidth = Number.parseInt(pStyles.width);

            const styles = window.getComputedStyle(this);
            const exteriorPx = [
                styles.marginLeft,
                styles.marginRight,
                styles.borderLeftWidth,
                styles.borderRightWidth,
                styles.paddingLeft,
                styles.paddingRight,
            ]
                .map(e => {{
                    const pat = /\\\\d+/;
                    const match = pat.exec(e);
                    return Number.parseInt(match[0])
                }})
                .reduce((prev, cur) => prev + cur, 0)

            const width = Math.min(pWidth - exteriorPx, sWidth);
            this.style.width = width + 'px';
        }});
    }})();
</script>
"""

    return re.sub(self.typeAnsPat, content, buf)


def state_change(new_state: MainWindowState, old_state: MainWindowState):
    global finished_review
    finished_review = old_state == "review" and new_state == "overview"


def post_webview_inject_style(webview: AnkiWebView):
    global finished_review

    print(f"post webview inject style: {finished_review}")

    if not finished_review:
        return

    review_main_id = "post-review-main"

    js = f"""
(() => {{
    if (document.getElementById("{review_main_id}")) return;

    document.querySelector("body > div").insertAdjacentHTML("afterend", `
        <div id="{review_main_id}">
            some test text
        </div>
    `);
}})();
"""

    webview.eval(js)


Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer

Reviewer._showAnswer = wrap(Reviewer._showAnswer, store_answers)
Reviewer._showAnswer = wrap(Reviewer._showAnswer, move_to_next_card)

Reviewer.nextCard = wrap(Reviewer.nextCard, on_next_card, "before")

Reviewer.show = wrap(Reviewer.show, init_state, "before")

Reviewer.typeAnsQuestionFilter = type_ans_question_filter


gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_will_end.append(cleanup)
gui_hooks.state_did_change.append(state_change)
gui_hooks.webview_did_inject_style_into_page.append(post_webview_inject_style)
