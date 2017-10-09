import os
import re
import fnmatch

import pkg_resources

try:
    from flake8.style_guide import Violation
except ImportError:
    # flake8 <3.4.0
    from flake8.style_guide import Error as Violation

ERROR_CODE = 'X100'


def is_inline_ignored(style_guide, filename, result):
    code, lineno, colno, text, line = result
    error = Violation(code, filename, lineno, (colno or 0) + 1, text, line)

    if hasattr(error, 'is_inline_ignored'):
        return error.is_inline_ignored(style_guide.options.disable_noqa)

    # flake8 <3.4.0
    return style_guide.is_inline_ignored(error)


def patch_flake8(spec):
    from flake8.checker import Manager
    orig_run = Manager.run

    def run(self):
        orig_run(self)

        for pattern, ignores in spec:
            redundant = ignores.copy()
            checkers = []
            for checker in self.checkers:
                filename = checker.display_name
                if not pattern.match(os.path.normpath(filename)):
                    continue

                for i, result in reversed(list(enumerate(checker.results))):
                    if is_inline_ignored(self.style_guide, filename, result):
                        continue

                    for code in ignores:
                        if result[0].startswith(code):
                            del checker.results[i]
                            redundant.discard(code)
                            break

                checkers.append(checker)

            if redundant and ERROR_CODE not in ignores:
                text = ('Superfluous per-file-ignores for ' +
                        ','.join(sorted(redundant)))
                for checker in checkers:
                    checker.report(ERROR_CODE, 0, 0, text)

    Manager.run = run


class PerFileIgnores:
    name = 'per-file-ignores'
    version = pkg_resources.get_distribution('flake8-' + name).version

    def __init__(self, tree):
        pass

    def run(self):
        return []

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--per-file-ignores', parse_from_config=True)
        parser.extend_default_select([ERROR_CODE])

    @classmethod
    def parse_options(cls, options):
        spec = []
        if options.per_file_ignores:
            for line in options.per_file_ignores.splitlines():
                if ':' in line:
                    filename, ignores = line.rsplit(':', 1)
                    spec.append((
                        re.compile(fnmatch.translate(filename.strip())),
                        {x.strip() for x in ignores.split(',')} - {''}
                    ))
        if spec:
            patch_flake8(spec)
