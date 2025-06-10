import asyncio

from app.usecase.update_data_usecase import pipeline_entry_point


def sync_run_pipeline():
    try:
        asyncio.run(pipeline_entry_point())
        return "Initialization successful"
    except Exception as e:
        return f"Initialization failed: {str(e)}"