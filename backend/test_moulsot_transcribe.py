import sys
import torch
import soundfile as sf
from transformers import BitsAndBytesConfig
from qwen_asr import Qwen3ASRModel

wav_path = sys.argv[1] if len(sys.argv) > 1 else "../test_16k.wav"
out_path = sys.argv[2] if len(sys.argv) > 2 else "transcript_moulsot.md"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
)

print("Loading moulsot.v0.3 (local) in 4-bit...")
model = Qwen3ASRModel.from_pretrained(
    "models/moulsot.v0.3",
    quantization_config=bnb_config,
    device_map="cuda:0",
)
print("LOADED OK")

data, sr = sf.read(wav_path, dtype="float32", always_2d=False)
print(f"Audio: {len(data)/sr:.1f}s at {sr}Hz")

result = model.transcribe(audio=(data, sr), language="Arabic")
if isinstance(result, list):
    result = result[0]
text = getattr(result, "text", str(result))
with open(out_path, "w", encoding="utf-8") as f:
    f.write("# moulsot.v0.3 transcript\n\n")
    f.write(text)
    f.write("\n")
print(f"--- TRANSCRIPT written to {out_path} ---")
