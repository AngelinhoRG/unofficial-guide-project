"""
app.py — Milestone 5: Gradio web interface for the Unofficial CS Guide

Run with:
    python3 app.py

Then open http://localhost:7860 in your browser.
"""

import gradio as gr

from generate import ask


def handle_query(question: str):
    question = question.strip()
    if not question:
        return "", ""

    result  = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial CS Guide") as demo:
    gr.Markdown(
        "# The Unofficial CS Guide\n"
        "Ask about CS student experiences, course workloads, and reviews. "
        "Answers are grounded in real student discussions and course reviews — "
        "not general advice."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="How many hours per week do CS students spend on coursework?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")

    answer  = gr.Textbox(label="Answer",         lines=8,  interactive=False)
    sources = gr.Textbox(label="Retrieved from", lines=4,  interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
