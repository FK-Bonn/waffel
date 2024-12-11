import datetime
import re
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

from waffel.classes import Student, FAK

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

ASSETS_DIR = Path(__file__).parent.resolve().parent.parent / 'assets'


def register_fonts(base_folder: Path):
    lato_path = base_folder / 'assets' / 'fonts' / 'Lato'
    pdfmetrics.registerFont(TTFont('LatoBold', lato_path / 'Lato-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('LatoBlack', lato_path / 'Lato-Black.ttf'))
    pdfmetrics.registerFont(TTFont('LatoItalic', lato_path / 'Lato-Italic.ttf'))
    pdfmetrics.registerFont(TTFont('LatoRegular', lato_path / 'Lato-Regular.ttf'))


def to_table(students: list[Student]) -> list[list[str | Paragraph]]:
    data: list[list[str | Paragraph]] = [['Lfd. Nr.', 'Name', 'Matrikelnr.']]
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
    canvas.drawImage(ASSETS_DIR / 'logo.png', A4[0] / 2 - 10 * mm, 40 * mm, width=20 * mm, height=20 * mm)
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


def any_fak(haystack: list[FAK], needles: list[FAK] | None) -> bool:
    if needles is None:
        return True
    return bool(len(set(haystack) & set(needles)))


def write_electoral_register(
        fs_name: str,
        deadline: datetime.date,
        first_election_day: datetime.date,
        students: list[Student],
        faks: list[FAK] | None,
        output_directory: Path,
):
    fs_id = re.sub(r'[^a-zA-Z0-9]+', '-', fs_name)
    doc = SimpleDocTemplate(str(output_directory / f'{fs_id}.pdf'), pagesize=A4, leftMargin=15 * mm,
                            rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
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


def write_electoral_registers(today: datetime.date, output_directory: Path, mapping: dict[str, list[FAK]],
                              students: list[Student]):
    first_election_day = today + datetime.timedelta(days=30)
    for fs, faks in mapping.items():
        print(f'Generating electoral register for {fs=}')
        write_electoral_register(f'Fachschaft {fs}',
                                 today, first_election_day, students, faks, output_directory)
    first_election_day = today + datetime.timedelta(days=45)
    print('Generating full electoral register')
    write_electoral_register('Wahl zum Studierendenparlament',
                             today, first_election_day, students, None, output_directory)
