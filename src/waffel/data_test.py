import csv
from pathlib import Path

from waffel.data import load_students


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


def create_students_file(names: list[tuple[str, str]], target: Path):
    with target.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=row('', '').keys(), delimiter=';')
        writer.writeheader()
        for first_names, last_names in names:
            writer.writerow(row(first_names, last_names))


def row(first_names: str, last_names: str) -> dict[str, str]:
    return {
        'vorname': first_names,
        'nachname': last_names,
        'mtknr': '0123456789',
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
