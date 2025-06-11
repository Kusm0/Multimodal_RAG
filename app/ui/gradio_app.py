import gradio as gr

from app.controller.mrag_inference_controllerr import rag_interface
from app.controller.updata_data_controller import sync_run_pipeline


def launch_gradio_ui():
    with gr.Blocks(title="Multimodal RAG for The Batch") as demo:

        gr.HTML(
            """
            <style>
            /* прибираємо рамки навколо кастом-лейблів */
            .custom-label-container .gradio-group { border:none !important; padding:0 !important; }

            /* стиль усіх лейблів */
            .custom-label {
                font-family:'IBM Plex Sans','Segoe UI','Roboto','Helvetica Neue',Arial,sans-serif;
                font-size:1rem;
                font-weight:600;          /* жирний */
                margin-bottom:0.4rem;
                color:#374151;
            }
            /* робимо кнопку компактнішою */
            #submit-btn { 
                padding:0.25rem 0.9rem; 
                font-size:0.85rem;
            }
            </style>
            """
        )


        init_status = gr.Textbox(visible=False)


        gr.Markdown("## **Ask a question about AI news from The Batch**")


        with gr.Row():
            query_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. How is AI used in medicine?",
                interactive=True,
                scale=8,
            )
            submit_btn = gr.Button(
                "Submit",
                elem_id="submit-btn",
                scale=1,
            )


        with gr.Row():

            with gr.Column(scale=1, min_width=260):
                image_output = gr.Image(label="Relevant Image", type="filepath")
                with gr.Group(elem_classes="custom-label-container"):
                    gr.Markdown("**Image Caption**")
                caption_output = gr.Markdown()

            with gr.Column(scale=2):
                with gr.Group(elem_classes="custom-label-container"):
                    gr.Markdown("**Answer**")
                answer_output = gr.Markdown()
                with gr.Group(elem_classes="custom-label-container"):
                    gr.Markdown("**Read more about this topic**")
                sources_output = gr.Markdown()


        submit_btn.click(
            fn=rag_interface,
            inputs=[query_input],
            outputs=[answer_output, image_output, caption_output, sources_output],
        )

        query_input.change(
            fn=lambda: [None, None, None, None],
            outputs=[answer_output, image_output, caption_output, sources_output],
        )

        demo.load(
            fn=sync_run_pipeline,
            inputs=[],
            outputs=[init_status],
        )

    demo.launch(server_name="0.0.0.0", server_port=7870)