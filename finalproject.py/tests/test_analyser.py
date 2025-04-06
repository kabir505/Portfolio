import pytest
from analyser import analyse_code

def test_detects_list():
    code = "numbers = [1, 2, 3]"
    structures = analyse_code(code)
    assert any(struct['type'] == 'List' for struct in structures)

def test_detects_dict():
    code = "person = {'name': 'Alice'}"
    structures = analyse_code(code)
    assert any(struct['type'] == 'Dictionary' for struct in structures)

def test_detects_membership_context():
    code = """numbers = [1, 2, 3]\nif 2 in numbers:\n    pass"""
    structures = analyse_code(code)
    assert any(struct.get('usage_context') == 'membership_test' for struct in structures)
