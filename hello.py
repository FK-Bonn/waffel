#! /usr/bin/env python3
import argparse
import csv
import datetime
import locale
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, LongTable, TableStyle, Table, Flowable, Spacer

TABLE_STYLE = TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'LatoBold'),
    ('BACKGROUND', (0, 0), (-1, 0), HexColor(0xcccccc)),
    ('FONTNAME', (0, 1), (-1, -1), 'LatoRegular'),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
])

PARAGRAPH_STYLE = ParagraphStyle(name='default', fontName='LatoRegular')
TITLE = ParagraphStyle(name='title', fontName='LatoBlack', fontSize=40, leading=50, alignment=TA_CENTER,
                       backColor=HexColor(0x111111), textColor=HexColor(0xffffff))
SUBTITLE = ParagraphStyle(name='subtitle', fontName='LatoBold', fontSize=20, leading=24, alignment=TA_CENTER)
META = ParagraphStyle(name='meta', fontName='LatoRegular', fontSize=20, leading=24, alignment=TA_CENTER)
CREDITS = ParagraphStyle(name='credits', fontName='LatoRegular', fontSize=10, leading=12, alignment=TA_LEFT,
                         textColor=HexColor(0x888888))


@dataclass(eq=True, frozen=True)
class FAK:
    degree: str
    subject: str

    @classmethod
    def from_dict(cls, line: dict) -> list['FAK']:
        faks = []
        for degree_index in range(1, 6):
            for subject_index in range(1, 4):
                degree = line[f'degree_{degree_index}']
                subject = line[f'degree_{degree_index}_subject_{subject_index}']
                if degree and subject:
                    faks.append(FAK(degree=degree, subject=subject))
        return faks

    @classmethod
    def from_line(cls, line: str) -> 'FAK':
        m = re.fullmatch(r'^(?P<subject>.+) +\((?P<degree>.+)\)$', line)
        if not m:
            print(line)
        return FAK(degree=m.group('degree'), subject=m.group('subject'))


@dataclass(eq=True, frozen=True)
class Student:
    first_names: str
    given_names: str
    matriculation_number: str
    faks: list[FAK]

    @classmethod
    def from_dict(cls, line: dict) -> 'Student':
        return Student(
            first_names=line['first_names'],
            given_names=line['given_names'],
            matriculation_number=line['matriculation_number'],
            faks=FAK.from_dict(line),
        )


def valid_date(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a valid date: {s!r}. Use format: YYYY-MM-DD")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--students-csv', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--date', type=valid_date, required=True)
    return parser.parse_args()


def load_students(students_csv: Path):
    students = []
    with students_csv.open('r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for line in reader:
            students.append(Student.from_dict(line))
    students = list(sorted(students, key=lambda s: (s.given_names, s.first_names)))
    return students


def load_mapping(mapping_md: Path) -> dict[str, list[FAK]]:
    data = {}
    with mapping_md.open('r') as f:
        current_fs = "None"

        # skip title
        f.readline()
        f.readline()
        f.readline()

        for line in f:
            # fak
            if (line[0:2] == "  "):
                if current_fs not in data:
                    data[current_fs] = []
                data[current_fs].append(FAK.from_line(line[4:].strip()))
            # fs
            elif (line[0] != "-"):
                current_fs = line.strip()
            # else: --- or newline
    return data


def any_fak(haystack: list[FAK], needles: list[FAK] | None) -> bool:
    if needles is None:
        return True
    return bool(len(set(haystack) & set(needles)))


def to_table(students: list[Student]) -> list[list[str | Paragraph]]:
    data = [['Lfd. Nr.', 'Name', 'Matrikelnr.']]
    for i, student in enumerate(students, start=1):
        data.append([
            f'{i:n}',
            Paragraph(f'{student.given_names}, {student.first_names}', style=PARAGRAPH_STYLE),
            str(student.matriculation_number),
        ])
    data.append(['- - -', '- - - E N D E - - -', '- - -'])
    return data


def to_faks_table(faks: list[FAK]):
    data = [['Lfd. Nr.', 'Abschluss', 'Fach']]
    for i, fak in enumerate(faks, start=1):
        data.append([
            f'{i:n}',
            fak.degree,
            fak.subject,
        ])
    data.append(['- - -', '- - - E N D E - - -', '- - -'])
    return data


def title_page_func(canvas: Canvas, doc: SimpleDocTemplate):
    canvas.saveState()
    canvas.drawImage('logo.png', A4[0] / 2 - 10 * mm, 40 * mm, width=20 * mm, height=20 * mm)
    canvas.setFont('LatoRegular', 10)
    canvas.setFillColorRGB(128 / 255, 128 / 255, 128 / 255)
    canvas.drawString(10 * mm, 10 * mm, 'Generiert durch das Fachschaftenkollektiv mit WAFFEL')
    canvas.restoreState()


def content_pages(canvas: Canvas, doc: SimpleDocTemplate):
    canvas.saveState()
    canvas.setFont('LatoRegular', 9)
    canvas.drawCentredString(A4[0] / 2, 15 * mm, f'Seite {doc.page - 1}')
    canvas.restoreState()


def title_page(subtitle: str, deadline: datetime.date, first_election_day: datetime.date, student_count: int) -> list[
    Flowable]:
    return [
        Spacer(0, 65 * mm),
        Paragraph('Wählendenverzeichnis', style=TITLE),
        Spacer(0, 20 * mm),
        Paragraph(subtitle, style=SUBTITLE),
        Spacer(0, 40 * mm),
        Paragraph(f'Stichtag: {deadline}', style=META),
        Spacer(0, 2 * mm),
        Paragraph(f'Erster Wahltag: {first_election_day}', style=META),
        Spacer(0, 10 * mm),
        Paragraph(f'{student_count:n} Wahlberechtigte', style=META),
        PageBreak(),
    ]


def write_electoral_register(
        fs_name: str,
        deadline: datetime.date,
        first_election_day: datetime.date,
        students: list[Student],
        faks: list[FAK] | None,
):
    fs_id = re.sub(r'[^a-zA-Z0-9]+', '-', fs_name)
    doc = SimpleDocTemplate(f"output/{fs_id}.pdf", pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    eligible_students = [student for student in students if any_fak(student.faks, faks)]
    items = title_page(fs_name, deadline, first_election_day, len(eligible_students))
    t = LongTable(to_table(eligible_students), repeatRows=1, colWidths=[20 * mm, 140 * mm, 25 * mm], style=TABLE_STYLE)
    items.append(t)
    if faks:
        items.extend([
            PageBreak(),
            Paragraph(
                f'In diesem Verzeichnis berücksichtigte Fach-Abschluss-Kombinationen ({len(faks)} Stück):',
                style=PARAGRAPH_STYLE),
            Spacer(0, 5 * mm),
        ])
        ft = Table(to_faks_table(faks), repeatRows=1, colWidths=[20 * mm, 50 * mm, 115 * mm], style=TABLE_STYLE)
        items.append(ft)
    doc.build(items, onFirstPage=title_page_func, onLaterPages=content_pages)


def register_fonts():
    pdfmetrics.registerFont(
        TTFont('LatoBold', Path(__file__).parent / 'fonts' / 'Lato' / 'Lato-Bold.ttf'))
    pdfmetrics.registerFont(
        TTFont('LatoBlack', Path(__file__).parent / 'fonts' / 'Lato' / 'Lato-Black.ttf'))
    pdfmetrics.registerFont(
        TTFont('LatoItalic', Path(__file__).parent / 'fonts' / 'Lato' / 'Lato-Italic.ttf'))
    pdfmetrics.registerFont(
        TTFont('LatoRegular', Path(__file__).parent / 'fonts' / 'Lato' / 'Lato-Regular.ttf'))


def write_new_faks(students: list[Student], mapping: dict[str, list[FAK]]):
    output_file = Path(__file__).parent / 'output' / 'unknown_faks.txt'
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
    print(f'Writing {len(new_faks)} new FAKs to {output_file}')
    output_file.write_text('\n'.join(new_fak_strings))


def main():
    args = _parse_args()
    students = load_students(args.students_csv)  # [:2000]
    mapping = load_mapping(args.mapping)
    register_fonts()
    output_dir = Path(__file__).parent / 'output'
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(exist_ok=True, parents=True)

    write_new_faks(students, mapping)

    first_election_day = args.date + datetime.timedelta(days=30)
    for fs, faks in mapping.items():
        print(f'Generating electoral register for {fs=}')
        write_electoral_register(f'Fachschaft {fs}', args.date, first_election_day, students, faks)

    first_election_day = args.date + datetime.timedelta(days=45)
    print(f'Generating full electoral register')
    write_electoral_register('Wahl zum Studierendenparlament', args.date, first_election_day, students, None)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    main()
