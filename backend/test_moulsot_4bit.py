import torch
from transformers import BitsAndBytesConfig
from qwen_asr import Qwen3ASRModel

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
print(torch.cuda.memory_allocated(0) / 1e9, "GB allocated")
print(torch.cuda.memory_reserved(0) / 1e9, "GB reserved")
