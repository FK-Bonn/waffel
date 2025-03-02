import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from waffel.classes import FAK, Student


def write_funds_distribution(output_directory: Path, mapping: dict[str, list[FAK]],
                             students: list[Student]):
    distribution: dict[str, Fraction] = defaultdict(lambda: Fraction(numerator=0, denominator=1))
    for student in students:
        fractions = get_fractions(student, mapping)
        for fs, fraction in fractions.items():
            distribution[fs] += fraction
    write_distribution = {}
    for fs, value in distribution.items():
        write_distribution[fs] = {'numerator': value.numerator, 'denominator': value.denominator}
    (output_directory / 'funds-distribution.json').write_text(json.dumps(write_distribution, indent=2))


def get_fractions(student: Student, mapping: dict[str, list[FAK]]) -> dict[str, Fraction]:
    fractions: dict[str, Fraction] = defaultdict(lambda: Fraction(numerator=0, denominator=1))
    for fak in student.faks:
        fs_with_fak = [fs for fs in mapping if fak in mapping[fs]]
        if not fs_with_fak:
            fs_with_fak = ['unknown']
        for fs in fs_with_fak:
            fractions[fs] += Fraction(numerator=1, denominator=len(student.faks) * len(fs_with_fak))
    return fractions
