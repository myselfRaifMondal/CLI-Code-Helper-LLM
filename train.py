import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from datasets import Dataset
import json
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from tqdm import tqdm
import numpy as np

def load_dataset(data_path):
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Format data for training
    formatted_data = []
    for item in data:
        prompt = f"Given the command-line instruction: {item['question']}\nProvide a step-by-step plan:"
        response = item['answer']
        formatted_data.append({
            "text": f"{prompt}\n{response}"
        })
    
    return Dataset.from_list(formatted_data)

def train():
    # Initialize model and tokenizer
    model_name = "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token  # Set padding token to end of sequence token
    
    # Determine device
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        device_map=device
    )
    
    # Prepare model for training
    model.train()
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # TinyLlama attention modules
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Create PEFT model
    model = get_peft_model(model, lora_config)
    
    # Load and preprocess dataset
    dataset = load_dataset("data/qa_pairs.json")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="adapter",
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        warmup_ratio=0.03,
    )
    
    # Training function
    def train_function():
        model.train()
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
        total_loss = 0
        progress_bar = tqdm(dataset, desc="Training")
        
        for batch_idx, batch in enumerate(progress_bar):
            inputs = tokenizer(
                batch["text"],
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Forward pass
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            
            # Backward pass
            loss.backward()
            
            # Update weights every 4 steps (gradient accumulation)
            if (batch_idx + 1) % 4 == 0:
                optimizer.step()
                optimizer.zero_grad()
            
            # Update progress
            total_loss += loss.item()
            avg_loss = total_loss / (batch_idx + 1)
            progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})
            
            # Save checkpoint every 100 batches
            if (batch_idx + 1) % 100 == 0:
                model.save_pretrained(f"adapter/checkpoint-{batch_idx+1}")
    
    # Run training
    train_function()
    
    # Save adapter
    model.save_pretrained("adapter")

if __name__ == "__main__":
    train()

