from app.services.drawing_service import extract_drawing_number


def test_extract_standard_pattern():
    assert extract_drawing_number("a2v带轮.dwg") == "A2V带轮"


def test_extract_with_underscore():
    assert extract_drawing_number("A3_动刀刃.bak") == "A3动刀刃"


def test_extract_with_space():
    assert extract_drawing_number("a4 轴承座.dwg") == "A4轴承座"


def test_extract_fallback():
    result = extract_drawing_number("unknown_file.dwg")
    assert result == "unknown_file"


def test_extract_assembly_drawing():
    assert extract_drawing_number("ao卧式钢筋切断机装配图.dwg") == "AO卧式钢筋切断机装配图"


def test_extract_with_model_suffix():
    assert extract_drawing_number("A3动刀刃-模型.pdf") == "A3动刀刃"
