import csv
import locale
import datetime
from pathlib import Path

from waffel.classes import Student, FAK


def collator_sort_key(stud: Student) -> tuple[str, str]:
    return locale.strxfrm(stud.given_names), locale.strxfrm(stud.first_names)

def load_students(students_csv: Path) -> list[Student]:
    students = []
    with students_csv.open('r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for line in reader:
            students.append(Student.from_dict(line))
    locale.setlocale(locale.LC_COLLATE, 'de_DE.utf8')
    students = list(sorted(students, key=collator_sort_key))
    return students


def load_mapping(mapping_md: Path) -> dict[str, list[FAK]]:
    data: dict[str, list[FAK]] = {}
    with mapping_md.open('r') as f:
        current_fs = "None"

        # skip title
        f.readline()
        f.readline()
        f.readline()

        for line in f:
            # fak
            if line[0:2] == "  ":
                if current_fs not in data:
                    data[current_fs] = []
                data[current_fs].append(FAK.from_line(line[4:].strip()))
            # fs
            elif line[0] != "-":
                current_fs = line.strip()
            # else: --- or newline
    return data


def write_new_faks(output_directory: Path, students: list[Student], mapping: dict[str, list[FAK]]) -> list[str]:
    output_file = output_directory / 'unknown_faks.txt'
    new_fak_strings = determine_new_faks(mapping, students)
    print(f'Writing {len(new_fak_strings)} new FAKs to {output_file}')
    output_file.write_text('\n'.join(new_fak_strings))
    return new_fak_strings


def determine_new_faks(mapping: dict[str, list[FAK]], students: list[Student]) -> list[str]:
    student_faks = set()
    for student in students:
        for fak in student.faks:
            student_faks.add(fak)
    assigned_faks = set()
    for fs, faks in mapping.items():
        for fak in faks:
            assigned_faks.add(fak)
    new_faks = student_faks - assigned_faks
    new_fak_strings = sorted(str(fak) for fak in new_faks)
    return new_fak_strings

def filter_students_for_semester(students: list[Student], date: datetime.date) -> list[Student]:
    year = date.year
    semester_index = 1
    if date.month >= 10:
        semester_index = 2
    elif date.month < 4:
        semester_index = 2
        year -= 1
    semester = f'{year}{semester_index}'
    return [s for s in students if s.semester == semester]
