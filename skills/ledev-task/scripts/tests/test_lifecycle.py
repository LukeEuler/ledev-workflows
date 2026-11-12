"""Observable lifecycle invariants in isolated projects; no real tasks moved."""
import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import generate_task_index as index
import task_transaction as tx


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.tasks = self.root / '.ai/ledev/tasks'
        self.tasks.mkdir(parents=True)

    def body(self, ident, parent=None, completed='', status='done'):
        p = (parent or self.tasks) / f'{ident}-sample.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f'# {ident} 示例 / Sample\n- Type: docs\n- Status: {status}\n- Completed: {completed}\n')
        return p

    def command(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), str(self.root), *args], capture_output=True, text=True)

    def test_discovery_sorting_links_and_duplicates(self):
        self.body('T001', completed='2026-10-02')
        self.body('T002', completed='2026-10-01')
        self.body('T003')
        archived = self.body('T004', self.tasks / 'archive/2026')
        # A similarly named attachment is not another task body.
        (archived.parent / 'T004-notes.md').write_text('# Notes\n')
        tasks = index.load_tasks(self.tasks)
        self.assertEqual(len(tasks), 4)
        rendered = index.render_index(tasks, self.tasks)
        self.assertLess(rendered.index('[T002]'), rendered.index('[T001]'))
        self.assertNotIn('[T004]', rendered)
        historical = index.render_index(tasks, self.tasks / 'archive', archive=True)
        self.assertIn('./2026/T004-sample.md', historical)
        self.assertEqual(self.command('generate_task_index.py', '--find', 'T004').stdout.strip(), str(archived.relative_to(self.root)))
        self.body('T001', self.tasks / 'archive/2026')
        failed = self.command('generate_task_index.py')
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse((self.tasks / 'index.md').exists())

    def test_next_id_covers_archive_and_records(self):
        self.body('T142', self.tasks / 'archive/2026')
        (self.tasks / 'index.md').write_text('Previously T149')
        self.assertEqual(index.next_task_id(self.root, self.tasks), 'T150')

    def test_two_indexes_and_interrupted_write_guard(self):
        self.body('T001')
        self.assertEqual(self.command('generate_task_index.py').returncode, 0)
        self.assertEqual(self.command('generate_task_index.py', '--check').returncode, 0)
        journal = self.root / tx.JOURNAL
        journal.parent.mkdir(parents=True)
        journal.write_text('{}')
        self.assertNotEqual(self.command('generate_task_index.py').returncode, 0)

    def plan(self, mapping):
        entries = []
        for rel, after in mapping.items():
            before = tx.read(self.root / rel)
            entries.append({'path': rel, 'before': tx.digest(before), 'content_base64': base64.b64encode(after).decode()} if after is not None else
                           {'path': rel, 'before': tx.digest(before), 'content': None})
        p = self.root / 'plan.json'
        p.write_text(json.dumps({'files': entries}))
        return str(p)

    def test_roundtrip_preserves_binary_and_new_edits(self):
        source = '.ai/ledev/tasks/T001-sample.md'
        dest = '.ai/ledev/tasks/archive/2026/T001-sample.md'
        binary = b'\x00\xff\x80'
        (self.root / source).write_bytes(binary)
        plan = self.plan({source: None, dest: binary})
        self.assertEqual(self.command('task_transaction.py', plan).returncode, 0)
        self.assertTrue((self.root / source).exists())
        self.assertEqual(self.command('task_transaction.py', plan, '--apply').returncode, 0)
        self.assertEqual((self.root / dest).read_bytes(), binary)
        (self.root / dest).write_bytes(binary + b'new')
        plan = self.plan({dest: None, source: binary + b'new'})
        self.assertEqual(self.command('task_transaction.py', plan, '--apply').returncode, 0)
        self.assertEqual((self.root / source).read_bytes(), binary + b'new')
        plan = self.plan({source: None, dest: binary + b'new'})
        self.assertEqual(self.command('task_transaction.py', plan, '--apply').returncode, 0)

    def test_batch_conflict_no_partial_mutation(self):
        (self.root / 'a').write_text('before')
        plan = self.plan({'a': b'after', 'b': b'new'})
        (self.root / 'b').write_text('user')
        self.assertNotEqual(self.command('task_transaction.py', plan, '--apply').returncode, 0)
        self.assertEqual((self.root / 'a').read_text(), 'before')
        self.assertEqual((self.root / 'b').read_text(), 'user')

    def test_runtime_failure_rolls_back(self):
        (self.root / 'a').write_text('before')
        plan = self.plan({'a': b'after', 'b': b'new'})
        original = tx.replace
        def fail_new(path, data):
            if path.name == 'b' and data is not None:
                raise OSError('injected write failure')
            return original(path, data)
        with patch.object(sys, 'argv', ['task_transaction.py', str(self.root), plan, '--apply']), patch.object(tx, 'replace', side_effect=fail_new):
            with self.assertRaises(OSError):
                tx.main()
        self.assertEqual((self.root / 'a').read_text(), 'before')
        self.assertFalse((self.root / 'b').exists())
        self.assertFalse((self.root / tx.JOURNAL).exists())

    def test_recovery_preserves_later_edit(self):
        journal = self.root / tx.JOURNAL
        journal.parent.mkdir(parents=True)
        record = {'files': [{'path': 'a', 'before': tx.digest(b'before'), 'after': tx.digest(b'after'), 'backup': tx.encode(b'before')}]}
        journal.write_text(json.dumps(record))
        (self.root / 'a').write_bytes(b'user')
        with self.assertRaises(ValueError):
            tx.recover(self.root, journal)
        self.assertEqual((self.root / 'a').read_bytes(), b'user')
        (self.root / 'a').write_bytes(b'after')
        tx.recover(self.root, journal)
        self.assertEqual((self.root / 'a').read_bytes(), b'before')

    def test_escaping_and_symlinks_rejected(self):
        with self.assertRaises(ValueError):
            tx.safe_path(self.root, '../escape')
        (self.root / 'link').symlink_to(self.tasks, target_is_directory=True)
        with self.assertRaises(ValueError):
            tx.safe_path(self.root, 'link/x')


if __name__ == '__main__':
    unittest.main()
