from typing import Any, Dict
import gradio as gr

from mathforge_core import *
from mathforge_core import _rng
from mathforge_generators import *
from mathforge_evaluation import *
from mathforge_worksheet import *
from mathforge_adaptive import *


def generate_api(topic: str, difficulty: str, count: int, seed: Any, strategy: str):
    rows = generate_problems(topic, difficulty, count, seed, strategy, blank_profile())
    return rows


def check_api(user_answer: str, problem_json: Dict[str, Any]):
    ok = equivalent(user_answer, problem_json)
    return {"correct": ok, "diagnostic": "" if ok else diagnose_mistake(user_answer, problem_json), "expected": problem_json.get("answer")}


# ----------------------------
# Interface
# ----------------------------
CSS = """
.gradio-container { max-width: 1280px !important; }
.hero { padding: 1.5rem 1.6rem; border: 1px solid var(--border-color-primary); border-radius: 24px; margin-bottom: 1rem; background: linear-gradient(135deg, color-mix(in srgb, var(--primary-500) 12%, transparent), transparent 55%); }
.hero h1 { margin: 0 0 .3rem; font-size: clamp(2rem,5vw,3rem); letter-spacing: -.055em; }
.hero p { margin: 0; opacity: .78; font-size: 1rem; max-width: 900px; }
.kicker { font-size: .78rem; text-transform: uppercase; letter-spacing: .13em; font-weight: 700; opacity: .65; }
.problem-card { min-height: 170px; border-radius: 18px; }
.compact-note { opacity: .75; font-size: .9rem; }
footer { display: none !important; }
"""

with gr.Blocks(title=APP_TITLE) as demo:
    gr.HTML(f"""
    <section class="hero">
      <div class="kicker">procedural education engine · v{APP_VERSION}</div>
      <h1>∑ MathForge X</h1>
      <p>Generate reproducible maths, run an adaptive mastery loop, diagnose common errors, inspect worked solutions, and export classroom-ready bundles without an external AI API.</p>
    </section>
    """)

    # Persistent client-side learning profile.
    profile_state = gr.BrowserState(default_value=blank_profile(), storage_key="mathforge_x_profile_v2")
    history_state = gr.BrowserState(default_value=[], storage_key="mathforge_x_history_v2")
    worksheet_state = gr.State([])
    adaptive_state = gr.State({})

    with gr.Tabs():
        with gr.Tab("Worksheet Forge"):
            with gr.Row():
                with gr.Column(scale=1, min_width=290):
                    gr.Markdown("### Generator controls")
                    topic = gr.Dropdown(TOPICS, value="Mixed", label="Topic")
                    difficulty = gr.Radio(DIFFICULTY_ORDER, value="Medium", label="Difficulty")
                    mix_strategy = gr.Radio(["Balanced", "Random", "Mastery-aware"], value="Balanced", label="Mixed-set strategy")
                    count = gr.Slider(1, 100, value=12, step=1, label="Number of questions")
                    seed = gr.Number(value=42, precision=0, label="Seed", info="Same settings + seed = same worksheet")
                    include_hints = gr.Checkbox(value=False, label="Show hints on worksheet")
                    generate_btn = gr.Button("Forge worksheet", variant="primary")
                with gr.Column(scale=2, min_width=430):
                    with gr.Tabs():
                        with gr.Tab("Questions"):
                            worksheet = gr.Markdown("Choose settings and press **Forge worksheet**.")
                        with gr.Tab("Worked answer key"):
                            answer_key = gr.Markdown("Answers and deterministic worked solutions appear after generation.")
                        with gr.Tab("Generation audit"):
                            audit = gr.Markdown("No set generated yet.")

            gr.Markdown("### Export bundle")
            gr.Markdown("<span class='compact-note'>Creates one ZIP containing printable HTML, TXT, CSV and JSON.</span>")
            with gr.Row():
                export_answers = gr.Checkbox(value=True, label="Include answers/solutions")
                export_hints = gr.Checkbox(value=False, label="Include hints")
                export_btn = gr.Button("Build export bundle")
                download = gr.File(label="Download bundle", interactive=False)

        with gr.Tab("Adaptive Tutor"):
            with gr.Row():
                with gr.Column(scale=1, min_width=290):
                    gr.Markdown("### Adaptive controls")
                    focus = gr.Dropdown(TOPICS, value="Mixed", label="Focus")
                    adaptive_seed = gr.Number(value=2026, precision=0, label="Session seed")
                    challenge_bias = gr.Slider(-2, 2, value=0, step=1, label="Challenge bias", info="-2 gentler · 0 calibrated · +2 stretch")
                    start_btn = gr.Button("Start / New Problem", variant="primary")
                    next_adaptive_btn = gr.Button("Next adaptive problem")
                with gr.Column(scale=2, min_width=430):
                    adaptive_problem = gr.Markdown("### Adaptive problem\nPress **Start / New Problem** to begin.", elem_classes="problem-card")
                    adaptive_answer = gr.Textbox(label="Your answer", placeholder="Examples: 3/4 · -2, 5 · 3.2e5 · 2:3")
                    check_adaptive_btn = gr.Button("Check + update mastery", variant="primary")
                    adaptive_feedback = gr.Markdown("")
                    worked_solution = gr.Markdown("")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Mastery model")
                    mastery = gr.Markdown(mastery_markdown(blank_profile()))
                with gr.Column():
                    coach = gr.Markdown(recommendation_markdown(blank_profile()))
                    reset_btn = gr.Button("Reset mastery profile", variant="secondary")
                    reset_status = gr.Markdown("")
            gr.Markdown("### Recent adaptive history")
            history_view = gr.Markdown("No adaptive attempts yet.")
            refresh_history_btn = gr.Button("Refresh history")

        with gr.Tab("Developer / API"):
            gr.Markdown(
                """### Deterministic engine API
MathForge X exposes Gradio API endpoints for programmatic generation and checking. Every generated challenge carries an ID, concept tag, difficulty rating, answer type, hint and worked solution. The browser profile is kept client-side for adaptive practice."""
            )
            with gr.Row():
                api_topic = gr.Dropdown(TOPICS, value="Mixed", label="API topic")
                api_diff = gr.Dropdown(DIFFICULTY_ORDER, value="Medium", label="API difficulty")
                api_count = gr.Slider(1, 20, 5, step=1, label="API count")
                api_seed = gr.Number(42, precision=0, label="API seed")
                api_strategy = gr.Dropdown(["Balanced", "Random", "Mastery-aware"], value="Balanced", label="API strategy")
            api_btn = gr.Button("Preview API generation")
            api_json = gr.JSON(label="Generated problem objects")

    generate_btn.click(
        generate_set,
        inputs=[topic, difficulty, count, seed, mix_strategy, include_hints, profile_state],
        outputs=[worksheet, answer_key, audit, worksheet_state],
        api_name="generate_math_set_v2",
    )
    export_btn.click(
        export_bundle,
        inputs=[topic, difficulty, worksheet_state, export_answers, export_hints],
        outputs=download,
        api_name="export_math_bundle_v2",
    )
    start_btn.click(
        start_adaptive,
        inputs=[focus, adaptive_seed, challenge_bias, profile_state],
        outputs=[adaptive_problem, adaptive_feedback, worked_solution, adaptive_state, profile_state, mastery, coach, adaptive_answer],
        api_name="start_adaptive_session",
    )
    check_adaptive_btn.click(
        adaptive_check,
        inputs=[adaptive_answer, adaptive_state, profile_state, history_state],
        outputs=[adaptive_feedback, worked_solution, adaptive_state, profile_state, history_state, mastery, coach],
        api_name="adaptive_check_answer",
    ).then(refresh_history, inputs=history_state, outputs=history_view)
    adaptive_answer.submit(
        adaptive_check,
        inputs=[adaptive_answer, adaptive_state, profile_state, history_state],
        outputs=[adaptive_feedback, worked_solution, adaptive_state, profile_state, history_state, mastery, coach],
    ).then(refresh_history, inputs=history_state, outputs=history_view)
    next_adaptive_btn.click(
        adaptive_next,
        inputs=[focus, challenge_bias, adaptive_state, profile_state],
        outputs=[adaptive_problem, adaptive_feedback, worked_solution, adaptive_state, adaptive_answer],
        api_name="next_adaptive_problem",
    )
    refresh_history_btn.click(refresh_history, inputs=history_state, outputs=history_view)
    reset_btn.click(
        reset_profile,
        outputs=[profile_state, history_state, mastery, coach, history_view, reset_status],
        api_name="reset_mastery_profile",
    )
    api_btn.click(
        generate_api,
        inputs=[api_topic, api_diff, api_count, api_seed, api_strategy],
        outputs=api_json,
        api_name="generate_problem_objects",
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=CSS)
