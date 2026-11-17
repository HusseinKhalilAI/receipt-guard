from engine.ocr import OCR, group_into_rows


def make_segment(text, left, top, width=100, height=40):
    return OCR(
        text=text,
        confidence=1.0,
        box=[(left, top), (left + width, top), (left + width, top + height), (left, top + height)],
    )


def test_group_same_row():
    total = make_segment("Total", left=10, top=480)
    amount = make_segment("8,24", left=300, top=485)
    rows = group_into_rows([total, amount])
    assert len(rows) == 1


def test_group_different_rows_top_to_bottom():
    lower = make_segment("Danke", left=10, top=480)
    upper = make_segment("Bäckerei", left=10, top=80)
    rows = group_into_rows([lower, upper])
    assert [[seg.text for seg in row] for row in rows] == [["Bäckerei"], ["Danke"]]


def test_group_sorts_row_left_to_right():
    amount = make_segment("8,24", left=300, top=480)
    total = make_segment("Total", left=10, top=482)
    rows = group_into_rows([amount, total])
    assert [seg.text for seg in rows[0]] == ["Total", "8,24"]


def test_group_empty_input():
    assert group_into_rows([]) == []