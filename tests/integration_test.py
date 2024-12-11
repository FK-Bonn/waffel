import shutil
from pathlib import Path
from subprocess import run, CompletedProcess


class TestIntegration:
    def test_happy_path(self, tmp_path):
        create_sample_data(tmp_path)

        run_waffel(tmp_path)

        assert (tmp_path / 'output' / 'Fachschaft-Agrarwissenschaften.pdf').is_file()
        assert (tmp_path / 'output' / 'Fachschaft-Altkatholisches-Seminar.pdf').is_file()
        assert (tmp_path / 'output' / 'Fachschaft-Anglistik-Amerikanistik-und-Keltologie.pdf').is_file()
        assert (tmp_path / 'output' / 'Wahl-zum-Studierendenparlament.pdf').is_file()
        assert (tmp_path / 'output' / 'unknown_faks.txt').read_text().splitlines() == [
            "FAK(degree='LA MA Berufskolleg', subject='Bildungswissenschaften')",
            "FAK(degree='LA MA Berufskolleg', subject='Pflanzenwissenschaften (Pflanzenbau)')",
            "FAK(degree='LA MA Berufskolleg', subject='Wirtschafts- und Sozialwissenschaften des Landbaus')",
            "FAK(degree='Master of Science', subject='Economics')",
            "FAK(degree='Med.Doc/Doc.of Philosophy', subject='Medizinische Neurowissenschaften')",
        ]

    def test_invalid_date_format(self, tmp_path):
        result = run_waffel(tmp_path, date='1.1.2025', succeeds=False)
        assert "waffel: error: argument --date: not a valid date: '1.1.2025'. Use format: YYYY-MM-DD" in result.stderr


def run_waffel(folder: Path, date: str = '2024-12-24', succeeds=False) -> CompletedProcess:
    return run(['waffel',
                '--students-csv', str(folder / 'students.csv'),
                '--mapping', str(folder / 'fachschaftenliste.md'),
                '--date', date,
                str(folder / 'output'),
                ], check=succeeds, capture_output=True, text=True)


def create_sample_data(tmp_path):
    shutil.copyfile(sample_file('fachschaftenliste.md'), tmp_path / 'fachschaftenliste.md')
    shutil.copyfile(sample_file('students.csv'), tmp_path / 'students.csv')


def sample_file(filename: str) -> Path:
    return Path(__file__).parent / 'testdata' / filename
