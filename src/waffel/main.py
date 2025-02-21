import argparse
import datetime
import json
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



def prepare_date_directory(output_dir: Path):
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(exist_ok=True, parents=True)


def copy_students_file(students_csv: Path, output_dir: Path, date: datetime.date):
    shutil.copyfile(students_csv, output_dir / f'students-{date}.csv')

def write_status_json(output_directory: Path, new_faks: list[str]):
    print('Writing status json')
    student_csvs = sorted(output_directory.glob('students-*.csv'), reverse=True)
    current_content = student_csvs[0].read_text()
    last_data_change = student_csvs[0].stem[-10:]
    for csv_file in student_csvs[1:]:
        if csv_file.read_text() != current_content:
            break
        else:
            last_data_change = csv_file.stem[-10:]
    data = {
        'last_successful_run': datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        'last_data_change': last_data_change,
        'unassigned_faks': new_faks,
    }
    (output_directory / 'status.json').write_text(json.dumps(data, indent=2))


def main():
    args = _parse_args()
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    register_fonts(Path(__file__).parent.resolve().parent.parent)
    students = load_students(args.students_csv)
    mapping = load_mapping(args.mapping)
    date_directory = args.output_directory / 'electoral-registers' / str(args.date)
    prepare_date_directory(date_directory)
    new_faks = write_new_faks(date_directory, students, mapping)
    students = filter_students_for_semester(students, args.date)
    write_electoral_registers(args.date, date_directory, mapping, students)
    copy_students_file(args.students_csv, args.output_directory, args.date)
    write_status_json(args.output_directory, new_faks)
