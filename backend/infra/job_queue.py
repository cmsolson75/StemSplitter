import asyncio
from model.htdemucs import DemucsWrapper
from infra.file_repo import create_gcs_file_repository

class SeparationJob:
    def __init__(self, audio_bytes: bytes):
        self.audio_bytes = audio_bytes
        self.result = asyncio.Future()

class SeparationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.model = DemucsWrapper()
        self.repo = create_gcs_file_repository()

    async def start_worker(self):
        while True:
            job: SeparationJob = await self.queue.get()
            try:
                zip_bytes = await asyncio.to_thread(self.model.separate, job.audio_bytes)
                gcs_path = await asyncio.to_thread(self.repo.upload_file, zip_bytes, ".zip")
                signed_url = await asyncio.to_thread(self.repo.generate_signed_url, gcs_path)
                job.result.set_result(signed_url)
            except Exception as e:
                job.result.set_exception(e)
            finally:
                self.queue.task_done()

    async def submit(self, job: SeparationJob) -> str:
        await self.queue.put(job)
        return await job.result

queue_instance = SeparationQueue()