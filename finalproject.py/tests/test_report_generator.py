import os
from report_generator import ReportGenerator

def test_generate_markdown_report(tmp_path):
    suggestions = [
        {
            'line': 3,
            'current_type': 'List',
            'suggestion': 'Use a set for membership testing.',
            'explanation': 'Sets are faster for membership checks.',
            'impact_estimate': 'Large efficiency gain.'
        }
    ]
    report_gen = ReportGenerator(suggestions, sustainability_score=90)
    report_file = tmp_path / "test_report.md"
    report_gen.generate_markdown_report(file_name=str(report_file))
    assert os.path.exists(report_file)
    with open(report_file) as f:
        content = f.read()
        assert 'Line 3' in content
        assert 'Sustainability Score' in content
