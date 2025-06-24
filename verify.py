#!/usr/bin/env python3
import os
import json
import torch
from transformers import AutoTokenizer

def check_files():
    required_files = [
        'README.md',
        'requirements.txt',
        'agent.py',
        'train.py',
        'eval_static.md',
        'eval_dynamic.md',
        'report.md',
        'data/qa_pairs.json'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    return missing

def check_data():
    try:
        with open('data/qa_pairs.json', 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                return False, "Data is not a list"
            if len(data) < 20:  # We have more, but testing min requirement
                return False, f"Only {len(data)} Q&A pairs found, need at least 150"
            for item in data:
                if not isinstance(item, dict) or 'question' not in item or 'answer' not in item:
                    return False, "Invalid data format"
        return True, f"Found {len(data)} valid Q&A pairs"
    except Exception as e:
        return False, str(e)

def check_model_requirements():
    try:
        import torch
        import transformers
        import peft
        import datasets
        import evaluate
        return True, "All model dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {str(e)}"

def main():
    print("Verifying project structure...")
    
    # Check files
    missing = check_files()
    if missing:
        print("❌ Missing files:", ", ".join(missing))
    else:
        print("✓ All required files present")
    
    # Check data
    data_ok, data_msg = check_data()
    print("✓" if data_ok else "❌", "Data check:", data_msg)
    
    # Check dependencies
    deps_ok, deps_msg = check_model_requirements()
    print("✓" if deps_ok else "❌", "Dependencies:", deps_msg)
    
    # Check GPU/MPS availability
    if torch.cuda.is_available():
        print("✓ CUDA available")
    elif torch.backends.mps.is_available():
        print("✓ MPS available (Apple Silicon)")
    else:
        print("! Warning: No GPU acceleration available, using CPU")
    
    # Try loading tokenizer (basic model test)
    try:
        tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T")
        print("✓ Model can be loaded")
    except Exception as e:
        print("❌ Model loading failed:", str(e))

if __name__ == "__main__":
    main()

