"""Prompt templates loader module."""

import yaml


def get_prompts():
    prompts = {}
    with open("backend/prompts/extract_qna.yaml", encoding="utf-8") as f:
        prompts["qna"] = yaml.safe_load(f)

    with open("backend/prompts/extract_iocs.yaml", encoding="utf-8") as f:
        prompts["iocs"] = yaml.safe_load(f)

    with open("backend/prompts/validate_iocs.yaml", encoding="utf-8") as f:
        prompts["validate_iocs"] = yaml.safe_load(f)

    return prompts
