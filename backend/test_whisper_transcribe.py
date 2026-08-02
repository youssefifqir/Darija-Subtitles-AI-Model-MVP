import sys
import torch
import soundfile as sf
from transformers import pipeline

model_id = sys.argv[1]
out_file = sys.argv[2]

print(f"Loading {model_id}...")
pipe = pipeline(
    "automatic-speech-recognition",
    model=model_id,
    device=0,
    torch_dtype=torch.float16,
    chunk_length_s=30,
)

data, sr = sf.read("../test_16k.wav", dtype="float32", always_2d=False)
print(f"Audio: {len(data)/sr:.1f}s at {sr}Hz")

result = pipe(
    {"array": data, "sampling_rate": sr},
    generate_kwargs={"language": "arabic", "task": "transcribe"},
)

with open(out_file, "w", encoding="utf-8") as f:
    f.write(result["text"])
print(f"--- TRANSCRIPT written to {out_file} ---")
