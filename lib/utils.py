from typing import Literal


def probability_to_prediction(probability: int) -> Literal["ON", "OFF"]:
    return "ON" if probability > 0.5 else "OFF"

def probability_to_confidence(probability: int) -> float:
    return probability if probability > 0.5 else 1 - probability

