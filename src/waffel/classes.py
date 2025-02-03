from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class FAK:
    degree: str
    subject: str

    @classmethod
    def from_dict(cls, line: dict) -> list['FAK']:
        faks = []
        for degree_index in range(1, 4):
            for subject_index in range(1, 4):
                # degree_id = line[f'abschluss{degree_index}']
                degree = line[f'abschluss{degree_index}dtxt']
                # subject_id = line[f'fach{degree_index}{subject_index}']
                key = f'fach{degree_index}{subject_index}dtxt'
                subject = line[key]
                if degree and subject:
                    faks.append(FAK(degree=degree, subject=subject))
        return faks

    @classmethod
    def from_line(cls, line: str) -> 'FAK':
        char_index = len(line) - 1
        assert line[char_index] == ')'
        open_parentheses = 1
        while open_parentheses > 0 and char_index >= 0:
            char_index -= 1
            if line[char_index] == '(':
                open_parentheses -= 1
            if line[char_index] == ')':
                open_parentheses += 1
        assert char_index > 0
        subject = line[:char_index].strip()
        degree = line[char_index + 1:len(line) - 1].strip()
        return FAK(subject=subject, degree=degree)


@dataclass(eq=True, frozen=True)
class Student:
    first_names: str
    given_names: str
    matriculation_number: str
    faks: list[FAK]

    @classmethod
    def from_dict(cls, line: dict) -> 'Student':
        return Student(
            first_names=line['vorname'],
            given_names=line['nachname'],
            matriculation_number=line['mtknr'],
            faks=FAK.from_dict(line),
        )
