def get_age_bucket(age: float) -> str:
    if age < 20:
        return "Under 20"
    if age < 30:
        return "20-30"
    if age < 40:
        return "30-40"
    if age < 50:
        return "40-50"
    if age < 60:
        return "50-60"
    if age < 70:
        return "60-70"
    if age < 80:
        return "70-80"
    if age < 90:
        return "80-90"
    if age < 100:
        return "90-100"
    return "100+"


def format_age_result(prediction: dict) -> dict:
    estimated_age = round(float(prediction["age"]), 1)
    return {
        "age_bucket": get_age_bucket(estimated_age),
        "estimated_age": estimated_age,
    }