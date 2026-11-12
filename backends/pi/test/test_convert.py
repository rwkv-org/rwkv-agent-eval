"""The host-side recovery converter (harbor_agent.convert_session) must match the in-container one
(turn.mjs convert) event for event, so a trial killed mid-turn yields the same contract files.

    PYTHONPATH=. python -m unittest backends.pi.test.test_convert
"""
import json
import subprocess
import unittest
from pathlib import Path

from backends.pi.harbor_agent import convert_session

TURN = Path(__file__).resolve().parents[1] / 'turn.mjs'

SESSION = [
    {'type': 'session', 'id': 's-1', 'cwd': '/app'},
    {'type': 'message', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': '旧的一轮'}]}},
    {'type': 'message', 'message': {'role': 'assistant', 'stopReason': 'stop', 'content': [{'type': 'text', 'text': 'old'}]}},
    {'type': 'message', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': '修复 app.py'}]}},
    {'type': 'message', 'message': {'role': 'assistant', 'stopReason': 'toolUse',
        'usage': {'input': 100, 'cacheRead': 20, 'output': 7},
        'content': [{'type': 'thinking', 'thinking': '先读文件'},
                    {'type': 'toolCall', 'id': 'c1', 'name': 'read', 'arguments': {'path': 'app.py'}}]}},
    {'type': 'message', 'message': {'role': 'toolResult', 'toolCallId': 'c1', 'toolName': 'read', 'isError': False,
        'content': [{'type': 'text', 'text': 'print(1)\n'}]}},
    {'type': 'message', 'message': {'role': 'toolResult', 'toolCallId': 'c2', 'toolName': 'bash', 'isError': True,
        'content': 'exit 1'}},
    {'type': 'message', 'message': {'role': 'assistant', 'stopReason': 'length', 'errorMessage': 'max tokens',
        'usage': {'input': 140, 'output': 9, 'totalTokens': 149}, 'content': [{'type': 'text', 'text': '  已完成。 '}]}},
    'not json',
    ['not', 'an', 'object'],
]


def lines():
    return [x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in SESSION]


def js_convert(start: int):
    code = ("import { readFileSync } from 'node:fs';"
            f"import {{ convert }} from {json.dumps(TURN.as_uri())};"
            "const { lines, start } = JSON.parse(readFileSync(0, 'utf8'));"
            "process.stdout.write(JSON.stringify(convert(lines, start)));")
    out = subprocess.run(['node', '--input-type=module', '-e', code], input=json.dumps({'lines': lines(), 'start': start}),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class ConvertParity(unittest.TestCase):
    def test_python_matches_turn_mjs(self):
        for start in (0, 3, 99):
            with self.subTest(start=start):
                events, final = convert_session(lines(), start)
                js = js_convert(start)
                self.assertEqual(events, js['events'])
                self.assertEqual(final, js['final'])

    def test_turn_slice_final_and_reason(self):
        events, final = convert_session(lines(), 3)
        self.assertEqual(final, '已完成。')
        self.assertEqual(events[0], {'type': 'session', 'sessionId': 's-1', 'cwd': '/app'})
        self.assertEqual(events[-1]['reason'], {'kind': 'max_tokens', 'error': 'max tokens'})
        kinds = [e['type'] for e in events]
        self.assertEqual(kinds, ['session', 'user', 'reasoning', 'tool_call', 'status', 'tool_result', 'tool_result',
                                 'text', 'status', 'final'])
        self.assertEqual(events[4]['usage'], {'inputTokens': 120, 'outputTokens': 7, 'totalTokens': 127})
        self.assertEqual(events[6]['status'], 'error')

    def test_empty_session_has_no_reply(self):
        events, final = convert_session([], 0)
        self.assertEqual(final, '')
        self.assertEqual(events[-1]['reason'], {'kind': 'no_reply'})


if __name__ == '__main__':
    unittest.main()
