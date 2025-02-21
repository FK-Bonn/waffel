import argparse
import datetime
import locale
import shutil
from pathlib import Path

from waffel.data import load_students, load_mapping, write_new_faks, filter_students_for_semester
from waffel.pdf import write_electoral_registers, register_fonts


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
    parser.add_argument('output_directory', type=Path)
    return parser.parse_args()



def prepare_output_directory(output_dir: Path):
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(exist_ok=True, parents=True)


def main():
    args = _parse_args()
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    register_fonts(Path(__file__).parent.resolve().parent.parent)
    students = load_students(args.students_csv)
    mapping = load_mapping(args.mapping)
    prepare_output_directory(args.output_directory)
    write_new_faks(args.output_directory, students, mapping)
    students = filter_students_for_semester(students, args.date)
    write_electoral_registers(args.date, args.output_directory, mapping, students)
