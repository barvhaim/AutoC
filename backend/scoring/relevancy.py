import json
from typing import List, Dict


def _get_total_keywords_length() -> int:
    with open("config.json") as f:
        config = json.load(f)
        keywords = list(set(config["keywords"]))
    return len(keywords)


total_keywords_length = _get_total_keywords_length()


def calculate_relevancy_score(qna: List[Dict], keywords: List[str]) -> float:
    # TODO: improve initial implementation
    positive_answers = sum(
        1
        for qa in qna
        if qa["answer"]
        and (
            qa["answer"].strip().lower().startswith("yes")
            or (
                "cannot be determined" not in qa["answer"].lower()
                and not qa["answer"].strip().lower().startswith("no")
            )
        )
    )

    keywords_score = (
        (len(keywords) / total_keywords_length) * 50 if total_keywords_length else 0
    )
    answers_score = (positive_answers / len(qna)) * 50 if qna else 0
    relevancy_score = keywords_score + answers_score
    return round(relevancy_score, 2)


def get_positive_qna(qna: List[Dict]) -> List[Dict]:
    # TODO: improve initial implementation
    positive_answers = [
        qa
        for qa in qna
        if qa["answer"]
        and (
            qa["answer"].strip().lower().startswith("yes")
            or (
                "cannot be determined" not in qa["answer"].lower()
                and not qa["answer"].strip().lower().startswith("no")
            )
        )
    ]

    return positive_answers


# if __name__ == '__main__':
#     from backend.scoring.mock_response import mock_response
#     _score = calculate_relevancy_score(qna=mock_response['qna'],
#                                        keywords=mock_response['keywords_found'])
#     print(f"Score: ", _score)
