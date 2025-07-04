from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.main import MainWindowState
from aqt.webview import AnkiWebView
from aqt import gui_hooks
from anki.cards import Card
from timeit import default_timer as timer
from .card_stats import CardStats
from .review_stats import ReviewStats
from .format import format_short_time
from . import config
from . import web_exports
from . import javascript
import re

post_review = False
review_stats_data: ReviewStats | None = None


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
    time = timer()

    self.typedAnswer = strip(val) or ""

    if len(self.typedAnswer) > 0:
        global review_stats_data
        assert review_stats_data
        assert review_stats_data.active_card

        review_stats_data.active_card.end_time = time

        self._showAnswer()


def move_to_next_card(self: Reviewer):
    self._answerCard(self._defaultEase())


def store_answers(self: Reviewer):
    global review_stats_data
    assert review_stats_data
    assert review_stats_data.active_card

    review_stats_data.active_card.correct_answer = strip(self.typeCorrect)
    review_stats_data.active_card.user_answer = strip(self.typedAnswer)

    print(review_stats_data.active_card)
    review_stats_data.finish_active_card()


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    if kind != "reviewQuestion":
        return text

    global review_stats_data
    assert review_stats_data
    display_cards = review_stats_data.get_displayed_cards(config.stat_display_limit())

    if len(display_cards):
        html_entries = "\n".join(map(CardStats.html, reversed(display_cards)))

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
    {html_entries}
</div>
"""

        return f"{text}\n{html_str}"

    return text


def on_reviewer_did_show_question(card: Card):
    time = timer()

    global review_stats_data
    assert review_stats_data
    assert review_stats_data.active_card

    review_stats_data.active_card.start_time = time


def cleanup():
    global review_stats_data
    print(review_stats_data)


def on_next_card(self: Reviewer):
    if not self.card:
        return

    global review_stats_data
    assert review_stats_data
    review_stats_data.prepare_new_active_card()

    assert review_stats_data.active_card
    review_stats_data.active_card.card_id = self.card.id


def init_state(self: Reviewer):
    global review_stats_data
    review_stats_data = ReviewStats()


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
    <input type=text id="typeans" onkeypress="_typeAnsPress();">
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
    global post_review
    post_review = old_state == "review" and new_state == "overview"


def post_webview_inject_style(webview: AnkiWebView):
    global post_review, review_stats_data
    assert review_stats_data

    if not post_review:
        return

    review_main_id = "post-review-main"
    total_time = review_stats_data.total_time()
    average_time = review_stats_data.average_time()
    median_time = review_stats_data.median_time()
    correct_attempts = review_stats_data.correct_attempts()
    incorrect_attempts = review_stats_data.incorrect_attempts()
    card_accuracy = review_stats_data.card_accuracy()

    html = f"""
<style>
    #{review_main_id} {{
        display: grid;
        grid-template-columns: minmax(3rem, auto) minmax(10rem, 800px) minmax(3rem, auto);
        grid-template-areas: ". content .";
    }}

    .container {{
        grid-area: content;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
        grid-auto-rows: 1fr;
        gap: .5rem;
    }}

    .group {{
        width: fit-content;
        height: fit-content;
    }}

    .top {{
        cursor: default;
    }}

    .bottom {{
        font-size: 2rem;
        line-height: 2rem;
        width: fit-content;
    }}

    .bottom::after {{
        line-height: normal;
    }}

    .cardtime>.bottom,
    .top {{
        font-size: 1rem;
        line-height: 1rem;
    }}

    .cardtime>.bottom {{
        line-height: 1.25rem;
    }}
</style>


<div id="{review_main_id}">
    <div class="container">
        <div class="group">
            <div class="top">time</div>
            <div class="bottom" aria-label="{format_short_time(total_time, decimals=3)}" data-balloon-pos="up">{format_short_time(total_time, decimals=0)}</div>
        </div>
        <div class="group">
            <div class="top">acc</div>
            <div class="bottom" aria-label="{round(card_accuracy, 3)}%
{correct_attempts} correct
{incorrect_attempts} incorrect" data-balloon-break data-balloon-pos="up">{round(card_accuracy)}%</div>
        </div>
        <div class="group">
            <div class="top">cards</div>
            <div class="bottom" aria-label="correct
incorrect" data-balloon-break data-balloon-pos="up">{correct_attempts}/{incorrect_attempts}</div>
        </div>
        <div class="group cardtime">
            <div class="top">card time</div>
            <div class="bottom" aria-label="{format_short_time(average_time, decimals=3)} average
{format_short_time(median_time, decimals=3)} median" data-balloon-break data-balloon-pos="up">{format_short_time(average_time, decimals=0, decimals_if_only_seconds=1)}<br>{format_short_time(median_time, decimals=0, decimals_if_only_seconds=1)}</div>
        </div>
    </div>
</div>
"""

    js = javascript.func_wrap(
        f"{javascript.ensure_run_once('post-review')} {javascript.insert_html('body', 'beforeend', html)}"
    )

    webview.eval(js)


web_exports.init_web_exports(r"web/.*(css|js)", css=["web/balloon.min.css"])

Reviewer._defaultEase = wrap(Reviewer._defaultEase, default_ease)

Reviewer._onTypedAnswer = on_typed_answer

Reviewer._showAnswer = wrap(Reviewer._showAnswer, store_answers)
Reviewer._showAnswer = wrap(Reviewer._showAnswer, move_to_next_card)

Reviewer._get_next_v3_card = wrap(Reviewer._get_next_v3_card, on_next_card)

Reviewer.show = wrap(Reviewer.show, init_state, "before")

Reviewer.typeAnsQuestionFilter = type_ans_question_filter


gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.reviewer_will_end.append(cleanup)
gui_hooks.state_did_change.append(state_change)
gui_hooks.webview_did_inject_style_into_page.append(post_webview_inject_style)
