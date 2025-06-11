from app.ui.gradio_app import launch_gradio_ui
from app.controller.updata_data_controller import sync_run_pipeline

if __name__ == "__main__":
    print(sync_run_pipeline())
    launch_gradio_ui()