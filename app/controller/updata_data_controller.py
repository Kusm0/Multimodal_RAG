import asyncio
from app.usecase.update_data_usecase import pipeline_entry_point

def sync_run_pipeline() -> str:
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(pipeline_entry_point())
        return "Initialization successful"
    except Exception as e:
        return f"Initialization failed: {e}"
    finally:
        loop.close()