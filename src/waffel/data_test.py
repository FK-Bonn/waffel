import csv
import datetime
from pathlib import Path

import pytest

from waffel.classes import Student
from waffel.data import load_students, filter_students_for_semester


class TestData:
    def test_load_students_sorts_last_names_correctly(self, tmp_path):
        names = [
            ('Peter', 'Uworra'),
            ('Peter', 'Überall'),
            ('Peter', 'Uberall'),
            ('Peter', 'Ozguz'),
            ('Peter', 'Öse'),
            ('Peter', 'Ober'),
            ('Peter', 'Lysow'),
            ('Peter', 'Łukasz'),
            ('Peter', 'Labertasche'),
            ('Peter', 'Azur'),
            ('Peter', 'Ástek'),
            ('Peter', 'Ärger'),
            ('Peter', 'Aalen'),
        ]
        create_students_file(names, tmp_path / 'students.csv')
        result = load_students(tmp_path / 'students.csv')
        items = [(s.first_names, s.given_names) for s in result]
        assert items == list(reversed(names))

    def test_load_students_sorts_first_names_correctly(self, tmp_path):
        names = [
            ('Undine', 'Beispiel'),
            ('Übrahim', 'Beispiel'),
            ('Ubo', 'Beispiel'),
            ('Otto', 'Beispiel'),
            ('Ödem', 'Beispiel'),
            ('Ober', 'Beispiel'),
            ('Lysander', 'Beispiel'),
            ('Łukasz', 'Beispiel'),
            ('Lana', 'Beispiel'),
            ('Azzizzle', 'Beispiel'),
            ('Ázure', 'Beispiel'),
            ('Ämine', 'Beispiel'),
            ('Abel', 'Beispiel'),
        ]
        create_students_file(names, tmp_path / 'students.csv')
        result = load_students(tmp_path / 'students.csv')
        items = [(s.first_names, s.given_names) for s in result]
        assert items == list(reversed(names))

    def test_load_students_sorts_last_names_correctly_single_letters(self, tmp_path):
        names = [
            ('Peter', 'V'),
            ('Peter', 'Ü'),
            ('Peter', 'U'),
            ('Peter', 'P'),
            ('Peter', 'Ö'),
            ('Peter', 'O'),
            ('Peter', 'M'),
            ('Peter', 'Ł'),
            ('Peter', 'L'),
            ('Peter', 'B'),
            ('Peter', 'Ä'),
            ('Peter', 'Á'),
            ('Peter', 'A'),
        ]
        create_students_file(names, tmp_path / 'students.csv')
        result = load_students(tmp_path / 'students.csv')
        items = [(s.first_names, s.given_names) for s in result]
        assert items == list(reversed(names))

    def test_load_students_teest(self, tmp_path):
        names = [
            ('Peter', 'achm'),
            ('Peter', 'ächl'),
            ('Peter', 'ache'),
        ]
        create_students_file(names, tmp_path / 'students.csv')
        result = load_students(tmp_path / 'students.csv')
        items = [(s.first_names, s.given_names) for s in result]
        assert items == list(reversed(names))

    @pytest.mark.parametrize('date_string, matriculation_number', [
        ['2024-04-01','1'],
        ['2024-09-30','1'],
        ['2024-10-01','2'],
        ['2025-03-31','2'],
        ['2025-04-01','3'],
        ['2025-09-30','3'],
    ])
    def test_filter_students(self, date_string, matriculation_number):
        students = [
            Student(first_names='A', given_names='a', semester='20241', matriculation_number='1', faks=[]),
            Student(first_names='B', given_names='b', semester='20242', matriculation_number='2', faks=[]),
            Student(first_names='C', given_names='c', semester='20251', matriculation_number='3', faks=[]),
        ]

        result = filter_students_for_semester(students, datetime.date.fromisoformat(date_string))
        assert len(result) == 1
        assert result[0].matriculation_number == matriculation_number


def create_students_file(names: list[tuple[str, str]], target: Path):
    with target.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=row('', '').keys(), delimiter=';')
        writer.writeheader()
        for first_names, last_names in names:
            writer.writerow(row(first_names, last_names))


def row(first_names: str, last_names: str) -> dict[str, str]:
    return {
        'OID_stg': 'deadbeef',
        'mtknr': '0123456789',
        'semester': '20242',
        'vorname': first_names,
        'nachname': last_names,
        'abschluss1': '69',
        'abschluss1dtxt': 'degree',
        'fach11': '420',
        'fach11dtxt': 'degree_1_subject_1',
        'fach12': '',
        'fach12dtxt': '',
        'fach13': '',
        'fach13dtxt': '',
        'abschluss2': '',
        'abschluss2dtxt': '',
        'fach21': '',
        'fach21dtxt': '',
        'fach22': '',
        'fach22dtxt': '',
        'fach23': '',
        'fach23dtxt': '',
        'abschluss3': '',
        'abschluss3dtxt': '',
        'fach31': '',
        'fach31dtxt': '',
        'fach32': '',
        'fach32dtxt': '',
        'fach33': '',
        'fach33dtxt': '',
    }
