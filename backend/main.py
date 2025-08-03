from fastapi import FastAPI
from infra.job_queue import queue_instance
from api.separate import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background worker
    import asyncio
    worker_task = asyncio.create_task(queue_instance.start_worker())
    yield
    # Clean up on shutdown
    worker_task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(router)