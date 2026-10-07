import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LocalQwen:
    def __init__(self, model_path: str):
        self.model_path = model_path

        # Use GPU if CUDA is available.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Loading model from: {self.model_path}")
        print(f"Using device: {self.device}")

        # Load tokenizer from local files.
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            local_files_only=True
        )

        # Load model from local files.
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            local_files_only=True,
            torch_dtype="auto"
        )

        self.model.to(self.device)
        self.model.eval()

        print("Qwen model loaded successfully.")

    def generate(self, prompt: str) -> str:

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Convert chat messages into the format expected by Qwen.
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Convert text into token IDs.
        inputs = self.tokenizer(
            text,
            return_tensors="pt"
        )

        # Move input tensors to the same device as the model.
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        # Generate the response.
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=600,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )

        # Remove the original prompt tokens.
        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

        # Convert generated tokens back into normal text.
        response = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return response.strip()