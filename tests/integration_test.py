import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run, CompletedProcess


class TestIntegration:
    def test_happy_path(self, tmp_path):
        create_sample_data(tmp_path)

        before = datetime.now(tz=timezone.utc)
        run_waffel(tmp_path)
        after = datetime.now(tz=timezone.utc)

        unassigned_faks = [
            "FAK(degree='LA MA Berufskolleg', subject='Pflanzenwissenschaften (Pflanzenbau)')",
            "FAK(degree='LA MA Berufskolleg', subject='Wirtschafts- und Sozialwissenschaften des Landbaus')",
            "FAK(degree='Master of Science', subject='Economics')",
            "FAK(degree='Med.Doc/Doc.of Philosophy', subject='Medizinische Neurowissenschaften')",
        ]
        electoral_registers_folder = tmp_path / 'output' / 'electoral-registers' / '2024-12-24'
        lehramt_pdf = electoral_registers_folder / 'Fachschaft-Lehramt.pdf'
        assert lehramt_pdf.is_file()
        assert (electoral_registers_folder / 'Fachschaft-Agrarwissenschaften.pdf').is_file()
        assert (electoral_registers_folder / 'Fachschaft-Altkatholisches-Seminar.pdf').is_file()
        assert (electoral_registers_folder / 'Fachschaft-Anglistik-Amerikanistik-und-Keltologie.pdf').is_file()
        assert (electoral_registers_folder / 'Wahl-zum-Studierendenparlament.pdf').is_file()
        assert (electoral_registers_folder / 'unknown_faks.txt').read_text().splitlines() == unassigned_faks
        assert (tmp_path / 'output' / 'students-2024-12-24.csv').is_file()
        funds_distribution = json.loads((electoral_registers_folder / 'funds-distribution.json').read_text())
        assert funds_distribution == {
            'Agrarwissenschaften': {'numerator': 1, 'denominator': 2},
            'Altkatholisches Seminar': {'numerator': 5, 'denominator': 2},
            'Anglistik, Amerikanistik und Keltologie': {'numerator': 1, 'denominator': 1},
            'unknown': {'numerator': 1, 'denominator': 1},
        }
        status = json.loads((tmp_path / 'output' / 'status.json').read_text())
        assert status['last_successful_run'] > before.isoformat()
        assert status['last_successful_run'] < after.isoformat()
        assert status['last_data_change'] == "2024-12-22"
        assert status['unassigned_faks'] == unassigned_faks
        assert_pdf_does_not_contain_text(lehramt_pdf, tmp_path, 'Gunkel')

    def test_invalid_date_format(self, tmp_path):
        result = run_waffel(tmp_path, date='1.1.2025', succeeds=False)
        assert "waffel: error: argument --date: not a valid date: '1.1.2025'. Use format: YYYY-MM-DD" in result.stderr


def run_waffel(folder: Path, date: str = '2024-12-24', succeeds=True) -> CompletedProcess:
    return run(['waffel',
                '--students-csv', str(folder / 'students.csv'),
                '--mapping', str(folder / 'fachschaftenliste.md'),
                '--date', date,
                str(folder / 'output'),
                ], check=succeeds, capture_output=True, text=True)


def assert_pdf_does_not_contain_text(pdf_file: Path, tmp_path: Path, text: str):
    text_file = tmp_path / 'pdfcontent.txt'
    run(['pdftotext', str(pdf_file), str(text_file)], check=True)
    content = text_file.read_text()
    assert text not in content


def create_sample_data(tmp_path):
    shutil.copyfile(sample_file('fachschaftenliste.md'), tmp_path / 'fachschaftenliste.md')
    shutil.copyfile(sample_file('students.csv'), tmp_path / 'students.csv')
    (tmp_path / 'output').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample_file('students.csv'), tmp_path / 'output' / 'students-2024-12-23.csv')
    shutil.copyfile(sample_file('students.csv'), tmp_path / 'output' / 'students-2024-12-22.csv')
    shutil.copyfile(sample_file('students.csv'), tmp_path / 'output' / 'students-2024-12-21.csv')
    (tmp_path / 'output' / 'students-2024-12-21.csv').write_text(
        ''.join((tmp_path / 'output' / 'students-2024-12-21.csv').read_text().splitlines()[:-1])
    )


def sample_file(filename: str) -> Path:
    return Path(__file__).parent / 'testdata' / filename
