import gradio as gr
from app.controller.mrag_inference_controllerr import rag_interface


def launch_gradio_ui() -> None:

    with gr.Blocks(title="Multimodal RAG for The Batch") as demo:

        gr.HTML(
            """
            <style>
              #answer-text { font-size: 1.15rem; line-height: 1.45; }

              #sources-text a { color: #ffffff !important; }
            </style>
            """
        )

        gr.Markdown("## 🔍 **Ask a question about AI news from The Batch**")


        with gr.Row():
            query_in = gr.Textbox(
                label="Your question",
                placeholder="e.g. How is AI used in medicine?",
                scale=5,
            )
            submit_btn = gr.Button("Submit", scale=1)

        gr.Markdown("---")


        with gr.Row():

            with gr.Column(scale=1):
                image_out = gr.Image(label="Image")
                caption_md = gr.Markdown(label="Image caption")

            with gr.Column(scale=1):
                gr.Markdown("### **Answer**")
                answer_md = gr.Markdown(elem_id="answer-text")
                gr.Markdown("### **Sources**")
                sources_md = gr.Markdown(elem_id="sources-text")

        submit_btn.click(
            fn=rag_interface,
            inputs=query_in,
            outputs=[answer_md, image_out, caption_md, sources_md],
            api_name="ask_rag",
        )

        demo.launch()


if __name__ == "__main__":
    launch_gradio_ui()