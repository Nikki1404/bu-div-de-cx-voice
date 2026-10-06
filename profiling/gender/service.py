from profiling.config import SEX_LABELS


def format_gender_result(prediction: dict) -> dict:
    female = float(prediction["female"])
    male = float(prediction["male"])
    if female > male:
        gender, confidence = SEX_LABELS[0], female
    else:
        gender, confidence = SEX_LABELS[1], male
    return {
        "gender": gender,
        "gender_confidence": round(confidence, 4),
        "gender_probabilities": {"female": round(female, 4), "male": round(male, 4)},
    }