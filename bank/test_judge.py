"""Tests for bank/judge.py's structural checks (2026-11-10).

    python3 -m unittest bank/test_judge.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402


def run(expect, files, final='', tools=('read',)):
    """Judge one turn: `final` as the reply, `files` as /app after the run."""
    with tempfile.TemporaryDirectory() as tmp:
        logs, app = Path(tmp, 'logs'), Path(tmp, 'app')
        logs.mkdir()
        app.mkdir()
        (logs / 'events-1.jsonl').write_text(''.join(json.dumps({'type': 'tool_call', 'tool': t}) + '\n' for t in tools))
        (logs / 'final-1.txt').write_text(final)
        for path, text in files.items():
            (app / path).parent.mkdir(parents=True, exist_ok=True)
            (app / path).write_text(text)
        return judge.judge(expect, logs, app)


class Groups(unittest.TestCase):
    EXP = {'turns': [{'output_contains_groups': [['人民广场(东)', '人民广场（东）'], ['9605', '9,605']]}]}

    def test_each_group_needs_a_hit(self):
        self.assertTrue(run(self.EXP, {}, '人民广场（东），共 9,605 人')[0])
        ok, details = run(self.EXP, {}, '人民广场（东）')
        self.assertFalse(ok)
        self.assertIn('9605', details['turns'][0]['failures'][0])

    def test_token_mode(self):
        exp = {'turns': [{'output_contains_groups': [['12']], 'output_contains_groups_token': True}]}
        self.assertFalse(run(exp, {}, '共 120 次')[0])
        self.assertTrue(run(exp, {}, '共 12 次')[0])


class Files(unittest.TestCase):
    def check(self, want, text):
        return run({'turns': [None], 'case': {'files': {'out.txt': want}}}, {'out.txt': text})[0]

    def test_text_equals_ignores_trailing_space_and_blank_lines(self):
        self.assertTrue(self.check({'text_equals': 'a\nb\n'}, 'a  \r\n\r\n\r\nb\n\n'.replace('\r\n\r\n\r\n', '\r\n')))
        self.assertTrue(self.check({'text_equals': 'a\n\nb'}, 'a\n\n\n\nb   \n'))
        self.assertFalse(self.check({'text_equals': 'a\nb'}, 'a\nc'))

    def test_lines_unordered(self):
        self.assertTrue(self.check({'lines_unordered': ['周岚 12', '郑宁 12']}, '郑宁 12\n\n周岚 12\n'))
        self.assertFalse(self.check({'lines_unordered': ['周岚 12', '郑宁 12']}, '郑宁 12\n'))

    def test_json_and_jsonl(self):
        self.assertTrue(self.check({'json_equals': {'a': 1, 'b': [2]}}, '{\n  "b": [2],\n  "a": 1\n}\n'))
        self.assertFalse(self.check({'json_equals': {'a': 1}}, '{"a": 2}'))
        self.assertFalse(self.check({'json_equals': {'a': 1}}, 'not json'))
        self.assertTrue(self.check({'jsonl_equals': [{'x': 1}, {'y': 2}]}, '{"x":1}\n\n{ "y" : 2 }\n'))
        self.assertFalse(self.check({'jsonl_equals': [{'x': 1}, {'y': 2}]}, '{"y":2}\n{"x":1}\n'))

    def test_markdown_table(self):
        want = [['书名', '年份'], ['SICP', '1985']]
        self.assertTrue(self.check({'markdown_table_equals': want}, '# 书单\n\n| 书名 | 年份 |\n|:---|---:|\n|SICP|1985|\n\n后记\n'))
        self.assertFalse(self.check({'markdown_table_equals': want}, '| 书名 | 年份 |\n|---|---|\n| SICP | 1986 |\n'))

    def test_old_fields_unchanged(self):
        self.assertTrue(self.check({'equals': 'x\n'}, 'x\r\n'))
        self.assertFalse(self.check({'equals': 'x y\n'}, 'x  y\n'))


if __name__ == '__main__':
    unittest.main()


class ExactEquals(unittest.TestCase):
    WANT = 'a = 1\r\nb = 2  \r\n'

    def test_default_ignores_line_endings(self):
        exp = {'turns': [{}], 'case': {'files': {'x.ini': {'equals': self.WANT}}}}
        self.assertTrue(run(exp, {'x.ini': 'a = 1\nb = 2  \n'})[0])

    def test_exact_needs_the_same_bytes(self):
        exp = {'turns': [{}], 'case': {'files': {'x.ini': {'equals': self.WANT, 'exact': True}}}}
        self.assertTrue(run(exp, {'x.ini': self.WANT})[0])
        for wrong in ('a = 1\nb = 2  \n', 'a = 1\r\nb = 2\r\n', self.WANT + '\r\n'):
            ok, details = run(exp, {'x.ini': wrong})
            self.assertFalse(ok, repr(wrong))
            self.assertIn('exact bytes', json.dumps(details))


class ProgramChecks(unittest.TestCase):
    def check(self, **c):
        exp = {'turns': [{}], 'case': {'checks': [{'argv': ['python3', '-c', "assert open('out.txt').read() == 'ok'"], **c}]},
               'initial': {}}
        return run(exp, {'out.txt': 'ok'})[0]

    def test_empty_protected_files_is_allowed(self):
        self.assertTrue(self.check(protected_files=[]))

    def test_missing_protected_files_is_invalid(self):
        self.assertFalse(self.check())
