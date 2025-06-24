# CLI Q&A Agent

A command-line agent that generates step-by-step plans for CLI tasks using a fine-tuned TinyLlama model.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download the Q&A dataset and place it in `data/qa_pairs.json`

3. Fine-tune the model:
```bash
python train.py
```

This will create an adapter in the `adapter/` directory.

## Usage

Run the agent with a natural language instruction:
```bash
python agent.py "Create a new Git branch and switch to it"
```

The agent will:
1. Generate a step-by-step plan
2. If the first step is a shell command, show it in dry-run mode
3. Log the interaction to `logs/trace.jsonl`

## Dataset

The training dataset should be in the following format:
```json
[
    {
        "question": "How do I create and switch to a new Git branch?",
        "answer": "1. Use git checkout -b new_branch_name\n2. This creates and switches to the new branch"
    },
    // ... more Q&A pairs
]
```

## Model

- Base model: TinyLlama-1.1B
- Fine-tuning: LoRA adaptation
- Device: Uses CUDA if available, falls back to MPS (Mac M1/M2) or CPU

