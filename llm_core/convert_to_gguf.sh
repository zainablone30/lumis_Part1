#!/bin/bash
# After LoRA fine-tuning, merge adapter into base weights, then convert to GGUF
# using llama.cpp so Ollama can serve it locally.

BASE_MODEL=$1            # e.g. microsoft/Phi-3-mini-4k-instruct
LORA_DIR=$2              # ./lumis-lora-adapter
MERGED_DIR=./lumis-merged
GGUF_OUT=./lumis-q4.gguf

python - <<PYEOF
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = AutoModelForCausalLM.from_pretrained("$BASE_MODEL")
model = PeftModel.from_pretrained(base, "$LORA_DIR")
model = model.merge_and_unload()
model.save_pretrained("$MERGED_DIR")
AutoTokenizer.from_pretrained("$BASE_MODEL").save_pretrained("$MERGED_DIR")
PYEOF

python ../llama.cpp/convert_hf_to_gguf.py $MERGED_DIR --outfile $GGUF_OUT --outtype q4_0

echo "Done. Now run: ollama create lumis -f Modelfile"
