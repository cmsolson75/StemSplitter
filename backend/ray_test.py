import ray
from pathlib import Path
from infra.config import get_settings

# Load settings
settings = get_settings()

# Connect to Ray namespace
ray.init(namespace=settings.ray_namespace)

# File to send
input_path = Path("/Users/cameronolson/Developer/Work/Echelon/Repos/StemSplitterTool/DefaultSet.wav")
output_path = Path("output.zip")
audio_bytes = input_path.read_bytes()

# Get Ray actor and call `.separate`
actor = ray.get_actor(settings.ray_actor_name)
result_ref = actor.separate.remote(audio_bytes)

# Fetch result
print("Waiting for Ray result...")
result_bytes = ray.get(result_ref, timeout=180.0)

# Write zip to disk
output_path.write_bytes(result_bytes)
print(f"Separation output written to: {output_path}")