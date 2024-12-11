from waffel.classes import FAK


class TestClasses:
    def test_load_fak_with_parentheses(self):
        result = FAK.from_line('Evangelische Theologie (Magister Theologiae (ev.))')
        assert result == FAK(degree='Magister Theologiae (ev.)', subject='Evangelische Theologie')

    def test_load_fak_worst_case_parentheses(self):
        result = FAK.from_line('Fach Fach (Fach (Fach)) Fach (Fach) (Abschluss (Abschluss))')
        assert result == FAK(degree='Abschluss (Abschluss)', subject='Fach Fach (Fach (Fach)) Fach (Fach)')
