import gradio as gr

from app.controller.mrag_inference_controllerr import rag_interface
from app.controller.updata_data_controller import sync_run_pipeline



def launch_gradio_ui():
    with gr.Blocks(title="Multimodal RAG for The Batch") as demo:
        # Custom styles
        gr.HTML("""
        <style>
        .hidden-block { display: none; }
        .custom-label-container .gradio-group { border: none !important; padding: 0 !important; }
        .custom-label {
            font-family: 'IBM Plex Sans', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #374151;
        }
        </style>
        """)

        # Sync status init
        init_status = gr.Textbox(visible=False)

        # User query input
        gr.Markdown("## 🔍 Ask a question about AI news from The Batch")

        with gr.Row():
            query_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. How is AI used in medicine?",
                interactive=True
            )
            submit_btn = gr.Button("Submit")

        # Output: answer + image + caption + sources
        with gr.Column(visible=False) as output_blocks:
            with gr.Row():
                with gr.Column(scale=1):
                    image_output = gr.Image(label="🖼️ Relevant Image", type="filepath")
                    with gr.Group(elem_classes="custom-label-container"):
                        gr.HTML('<div class="custom-label">Image Caption</div>')
                        caption_output = gr.Markdown()
                with gr.Column(scale=2):
                    with gr.Group(elem_classes="custom-label-container"):
                        gr.HTML('<div class="custom-label">🧠 Answer</div>')
                        answer_output = gr.Markdown()
                    with gr.Group(elem_classes="custom-label-container"):
                        gr.HTML('<div class="custom-label">📚 Read more about this topic</div>')
                        sources_output = gr.Markdown()

        # Query submit logic
        submit_btn.click(
            fn=rag_interface,
            inputs=[query_input],
            outputs=[answer_output, image_output, caption_output, sources_output]
        ).success(
            fn=lambda: gr.Column(visible=True),
            outputs=[output_blocks],
            show_progress=False
        )

        # Reset on input change
        query_input.change(
            fn=lambda: [None, None, None, None, gr.Column(visible=False)],
            outputs=[answer_output, image_output, caption_output, sources_output, output_blocks]
        )

        # Optional: pipeline sync on UI load
        demo.load(
            fn=sync_run_pipeline,
            inputs=[],
            outputs=[init_status]
        )

    # Run app
    demo.launch(server_name="0.0.0.0", server_port=7860)