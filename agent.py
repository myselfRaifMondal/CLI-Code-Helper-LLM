import sys
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import jsonlines
from datetime import datetime

class CLIAgent:
    def __init__(self, base_model="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T", adapter_path="adapter"):
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map=self.device
        )
        
        # Load fine-tuned adapter
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.model.eval()

    def generate_plan(self, instruction):
        prompt = f"Given the command-line instruction: {instruction}\nProvide a step-by-step plan:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            num_return_sequences=1
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        steps = response.split("\n")
        
        return steps

    def log_trace(self, instruction, steps):
        trace = {
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "steps": steps
        }
        
        with jsonlines.open("logs/trace.jsonl", mode="a") as writer:
            writer.write(trace)

    def run(self, instruction):
        steps = self.generate_plan(instruction)
        self.log_trace(instruction, steps)
        
        # Check if first line is a shell command
        first_step = steps[0].strip()
        if first_step.startswith("$") or first_step.startswith(">"):
            command = first_step.lstrip("$>").strip()
            print(f"Would execute: {command}")
        
        return steps

def main():
    if len(sys.argv) != 2:
        print("Usage: python agent.py \"<instruction>\"")
        sys.exit(1)
    
    instruction = sys.argv[1]
    agent = CLIAgent()
    steps = agent.run(instruction)
    
    print("\nGenerated Plan:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")

if __name__ == "__main__":
    main()

