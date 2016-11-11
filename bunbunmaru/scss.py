
import os
import hashlib
import fnmatch
import functools
import subprocess
from threading import Thread, Lock

from watchdog.events import (
    PatternMatchingEventHandler,
    FileMovedEvent, FileCreatedEvent,
    FileDeletedEvent, FileModifiedEvent
)


class ScssHandler(PatternMatchingEventHandler):
    patterns = ['*.scss']

    def __init__(self, binary, scss_path, target_path, filename):
        super().__init__()
        self.binary = binary
        self.scss_path = scss_path
        self.target_path = target_path
        self.filename = filename

        self.file_hashes = {}
        self.reset_all_hashes()

        self.threads = []
        self.lock = Lock()

    def reset_all_hashes(self):
        self.file_hashes = {}
        for path, dirnames, filenames in os.walk(self.scss_path):
            for filename in filenames:
                if any(fnmatch.fnmatch(filename, pattern)
                       for pattern in self.patterns):
                    filepath = os.path.abspath(os.path.join(path, filename))
                    self.file_hashes[filepath] = ''

        for path in self.file_hashes:
            self.file_hashes[path] = self.generate_file_hash(path)

    def generate_file_hash(self, path):
        if not self.test_pattern(path):
            return
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            d = hashlib.sha1()
            for chunk in iter(functools.partial(f.read, 16 << 10), b''):
                d.update(chunk)
        return d.hexdigest()

    def test_pattern(self, path):
        return any(fnmatch.fnmatch(path, pattern)
                   for pattern in self.patterns)

    def recompile(self, files):
        t = Thread(target=self.recompile_threaded, args=(files,))
        t.start()

    def recompile_threaded(self, files):
        with self.lock:
            src_file = os.path.join(self.scss_path, self.filename + '.scss')
            dst_file = os.path.join(self.target_path, self.filename + '.css')
            print('Detecting changes. Recompiling:')
            for file in files:
                cwd = os.getcwd().rstrip('/')
                if file.startswith(cwd):
                    file = file[len(cwd)+1:]
                print('-', file)
            proc = subprocess.Popen([self.binary, '-t', 'nested',
                                     src_file, dst_file],
                                    stderr=subprocess.PIPE)

            _, errput = proc.communicate()
            r = proc.wait()
            if r != 0:
                print('\033[31m', end='')
                print(errput.decode('utf-8'), end='')
                print('\033[0m')
            else:
                print('Done.')

    def on_modified(self, event: FileModifiedEvent):
        _, path, _ = event.key

        if not self.test_pattern(path):
            return

        if path not in self.file_hashes:
            self.file_hashes[path] = ''

        tmp_hash = self.generate_file_hash(path)
        if tmp_hash != self.file_hashes[path]:
            self.file_hashes[path] = tmp_hash
            self.recompile([path])

    def on_moved(self, event: FileMovedEvent):
        _, src_path, dst_path, _ = event.key
        if not self.test_pattern(src_path) or not self.test_pattern(dst_path):
            return

        tmp_hash = self.generate_file_hash(dst_path)
        old_hash = ''

        if src_path in self.file_hashes:
            old_hash = self.file_hashes[src_path]
            del self.file_hashes[src_path]
        self.file_hashes[dst_path] = tmp_hash

        # don't rehash if not changed.
        # recompilation happens when the importing script is changed
        if tmp_hash != old_hash:
            self.recompile([src_path, dst_path])

    def on_created(self, event: FileCreatedEvent):
        # after every create follows a modified. so use that instead
        pass

    def on_deleted(self, event: FileDeletedEvent):
        _, path, _ = event.key
        if not self.test_pattern(path):
            return

        if path in self.file_hashes:
            del self.file_hashes[path]
        self.recompile([path])
