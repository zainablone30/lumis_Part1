"""
LoRA fine-tuning of a small open-source base model on your custom dialogue dataset.
Usage:
    python lora_finetune.py --base_model microsoft/Phi-3-mini-4k-instruct \
                             --dataset data/seed_dialogues_final.jsonl \
                             --output_dir ./lumis-lora-adapter
"""
import argparse
import json
import os
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

PERSONA_PATH = os.path.join(os.path.dirname(__file__), "persona_system_prompt.txt")
PERSONA_PREFIX = open(PERSONA_PATH).read()


def load_dataset(path, tokenizer, max_len=512):
    rows = []
    with open(path) as f:
        for line in f:
            rows.append(json.loads(line))

    def format_example(ex):
        prompt = (
            f"<|system|>\n{PERSONA_PREFIX}\n"
            f"Detected user emotion: {ex.get('emotion', 'Neutral')}\n<|end|>\n"
            f"<|user|>\n{ex['instruction']}\n<|end|>\n"
            f"<|assistant|>\n{ex['response']}<|end|>"
        )
        tokenized = tokenizer(prompt, truncation=True, max_length=max_len, padding="max_length")
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    ds = Dataset.from_list(rows)
    ds = ds.map(format_example, remove_columns=ds.column_names)
    return ds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", default="microsoft/Phi-3-mini-4k-instruct")
    ap.add_argument("--dataset", default="data/seed_dialogues_final.jsonl")
    ap.add_argument("--output_dir", default="./lumis-lora-adapter")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch_size", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    args = ap.parse_args()

    use_cuda = torch.cuda.is_available()

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if use_cuda:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model, quantization_config=bnb_config, device_map="auto"
        )
        model = prepare_model_for_kbit_training(model)
    else:
        print("WARNING: No GPU detected. This will be very slow or may not work on CPU.")
        model = AutoModelForCausalLM.from_pretrained(args.base_model)

    lora_config = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    train_ds = load_dataset(args.dataset, tokenizer)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=8,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=use_cuda,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
    )

    collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = Trainer(
        model=model, args=training_args,
        train_dataset=train_ds, data_collator=collator,
    )
    trainer.train()
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"LoRA adapter saved to {args.output_dir}")


if __name__ == "__main__":
    main()
