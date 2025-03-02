from fractions import Fraction

from waffel.classes import Student, FAK
from waffel.funds import get_fractions


class TestFunds:
    def test_fractions_one_fak_no_fs(self):
        mapping = {}
        student = sample_student(faks=[
            FAK(degree='Bachelor of Arts', subject='Geschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'unknown': Fraction(numerator=1, denominator=1),
        }

    def test_fractions_one_fak_one_fs(self):
        mapping = {
            'Geschichte': [
                FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
            ],
        }
        student = sample_student(faks=[
            FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'Geschichte': Fraction(numerator=1, denominator=1),
        }

    def test_fractions_one_fak_two_fs(self):
        mapping = {
            'Geschichte': [FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte')],
            'Zauberei': [FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte')],
        }
        student = sample_student(faks=[
            FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'Geschichte': Fraction(numerator=1, denominator=2),
            'Zauberei': Fraction(numerator=1, denominator=2),
        }

    def test_fractions_two_fak_one_fs(self):
        mapping = {
            'Geschichte': [
                FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
                FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            ],
        }
        student = sample_student(faks=[
            FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'Geschichte': Fraction(numerator=1, denominator=1),
        }

    def test_fractions_two_shared_fak_two_fs(self):
        mapping = {
            'Geschichte': [
                FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
                FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            ],
            'Zauberei': [
                FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
                FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            ],
        }
        student = sample_student(faks=[
            FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'Geschichte': Fraction(numerator=1, denominator=2),
            'Zauberei': Fraction(numerator=1, denominator=2),
        }

    def test_fractions_two_distinct_fak_two_fs(self):
        mapping = {
            'Geschichte': [
                FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
            ],
            'Zauberei': [
                FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            ],
        }
        student = sample_student(faks=[
            FAK(degree='Bachelor of Science', subject='Früh- und Spätgeschichte'),
            FAK(degree='Bachelor of Arts', subject='Früh- und Spätgeschichte'),
        ])
        assert get_fractions(student, mapping) == {
            'Geschichte': Fraction(numerator=1, denominator=2),
            'Zauberei': Fraction(numerator=1, denominator=2),
        }

    def test_fractions_lehramt_case(self):
        mapping = {
            'Lehramt': [
                FAK(degree='LA BA Gym Ge', subject='Bildungswissenschaften'),
                FAK(degree='LA BA Gym Ge', subject='Deutsch'),
                FAK(degree='LA BA Gym Ge', subject='Englisch'),
            ],
            'Germanistik': [
                FAK(degree='LA BA Gym Ge', subject='Deutsch'),
            ],
            'Anglistik, Amerikanistik und Keltologie': [
                FAK(degree='LA BA Gym Ge', subject='Englisch'),
            ],
            'VWL': [
                FAK(degree='Bachelor of Arts', subject='Volkswirtschaftslehre'),
            ],
        }
        student = sample_student(faks=[
            FAK(degree='LA BA Gym Ge', subject='Bildungswissenschaften'),
            FAK(degree='LA BA Gym Ge', subject='Deutsch'),
            FAK(degree='LA BA Gym Ge', subject='Englisch'),
            FAK(degree='Bachelor of Arts', subject='Volkswirtschaftslehre'),
        ])
        assert get_fractions(student, mapping) == {
            'Lehramt': Fraction(numerator=1, denominator=2),
            'Germanistik': Fraction(numerator=1, denominator=8),
            'Anglistik, Amerikanistik und Keltologie': Fraction(numerator=1, denominator=8),
            'VWL': Fraction(numerator=1, denominator=4),
        }


def sample_student(faks: list[FAK]) -> Student:
    return Student(first_names='', given_names='', matriculation_number='', semester='', faks=faks)
