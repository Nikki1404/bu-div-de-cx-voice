import unittest

from profiling.age.service import format_age_result, get_age_bucket
from profiling.gender.service import format_gender_result


class AgeGenderServiceTests(unittest.TestCase):
    def test_age_bucket_boundaries(self):
        self.assertEqual(get_age_bucket(19.9), "Under 20")
        self.assertEqual(get_age_bucket(20), "20-30")
        self.assertEqual(get_age_bucket(30), "30-40")
        self.assertEqual(get_age_bucket(100), "100+")

    def test_age_prediction_uses_rounded_estimate_for_bucket(self):
        self.assertEqual(
            format_age_result({"age": 29.96}),
            {"age_bucket": "30-40", "estimated_age": 30.0},
        )

    def test_gender_prediction_formats_class_and_probabilities(self):
        result = format_gender_result({"female": 0.8, "male": 0.2})
        self.assertEqual(result["gender"], "Female")
        self.assertEqual(result["gender_confidence"], 0.8)
        self.assertEqual(
            result["gender_probabilities"], {"female": 0.8, "male": 0.2}
        )


if __name__ == "__main__":
    unittest.main()