from dataclasses import dataclass


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
            first_names=line['first_names'],
            given_names=line['given_names'],
            matriculation_number=line['matriculation_number'],
            faks=FAK.from_dict(line),
        )
