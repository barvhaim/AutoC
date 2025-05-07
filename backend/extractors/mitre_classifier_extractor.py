import os
import torch
import json
import joblib
from transformers import BertTokenizer
from typing import List, Optional
from huggingface_hub import hf_hub_download
from langchain.text_splitter import RecursiveCharacterTextSplitter


class mitreClassifierExtractor:
    def __init__(
        self,
        article_content: str,
        model_repo: str = "dvir056/mitre_ttp",
        threshold: float = 0.2,
        qna: Optional[List[dict]] = None,
    ):
        self.article_content = article_content
        self.threshold = threshold
        self.qna = qna or []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # === Load model, tokenizer, label binarizer from Hugging Face ===
        self.model_path = model_repo
        self.cache_dir = os.path.expanduser("~/.cache/mitre_model")

        self.tokenizer = BertTokenizer.from_pretrained(self.model_path)

        config_path = hf_hub_download(repo_id=model_repo, filename="config.json", local_dir=self.cache_dir)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.max_tokens = config.get("max_position_embeddings", 512)

        scripted_model_path = hf_hub_download(repo_id=model_repo, filename="model_scripted.pt", local_dir=self.cache_dir)
        self.model = torch.jit.load(scripted_model_path).to(self.device)
        self.model.eval()

        label_binarizer_path = hf_hub_download(repo_id=model_repo, filename="label_binarizer.pkl", local_dir=self.cache_dir)
        self.mlb = joblib.load(label_binarizer_path)

        mitre_json_path = hf_hub_download(repo_id=model_repo, filename="enterprise-attack.json", local_dir=self.cache_dir)
        self.mitre_map = self._load_mitre_map(mitre_json_path)

    def _load_mitre_map(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        mapping = {}
        for obj in data["objects"]:
            if obj.get("type") == "attack-pattern":
                for ref in obj.get("external_references", []):
                    if ref.get("source_name") == "mitre-attack" and "external_id" in ref:
                        mapping[ref["external_id"]] = {
                            "name": obj.get("name", "Unknown"),
                            "url": ref.get("url", "")
                        }
        return mapping

    def classify(self):
        chunks = []
        # 1. Split article into chunks
        if len(self.tokenizer.encode(self.article_content, add_special_tokens=False)) > self.max_tokens:
            chunks = self._split_text_into_chunks(self.article_content)
        else:
            chunks = [self.article_content]

        # 2. Add QnA answers
        for item in self.qna:
            answer = item.get("answer", "").strip()
            if answer:
                if len(self.tokenizer.encode(answer, add_special_tokens=False)) > self.max_tokens:
                    chunks.extend(self._split_text_into_chunks(answer))
                else:
                    chunks.append(answer)

        # 3. Predict for each chunk
        from collections import defaultdict
        all_preds = defaultdict(list)

        for chunk in chunks:
            inputs = self.tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=self.max_tokens)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(inputs["input_ids"], inputs.get("attention_mask"), inputs.get("token_type_ids"))
                probs = torch.sigmoid(logits).cpu().numpy()[0]

            for idx, prob in enumerate(probs):
                if prob > self.threshold:
                    label = self.mlb.classes_[idx]
                    all_preds[label].append(prob)

        # 4. Sort by max confidence
        sorted_preds = sorted(
            all_preds.items(),
            key=lambda x: max(x[1]),
            reverse=True
        )

        # 5. Prepare results with max confidence
        results = []
        for tid, confidences in sorted_preds:
            info = self.mitre_map.get(tid, {"name": "Unknown Technique", "url": ""})
            results.append({
                "id": tid,
                "name": info["name"],
                "confidence": round(max(confidences), 4),
                "url": info["url"]
            })

        return results

    def _split_text_into_chunks(self, text, stride=384):
        # Use your existing self.tokenizer (a BertTokenizer)
        def count_tokens(t):
            return len(self.tokenizer.encode(t, add_special_tokens=False))

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_tokens,
            chunk_overlap=stride,
            separators=["\n\n", "\n", ".", " "],
            length_function=count_tokens
        )

        chunks = splitter.split_text(text)
        return chunks

    def enrich_ids_with_metadata(self, technique_ids):
        results = []
        for tid in technique_ids:
            info = self.mitre_map.get(tid, {"name": "Unknown Technique", "url": ""})
            results.append({
                "id": tid,
                "name": info["name"],
                "url": info["url"]
            })
        return results
