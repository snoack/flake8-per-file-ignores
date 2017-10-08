import os
import re
import fnmatch

import pkg_resources


def patch_flake8(spec):
    from flake8.checker import Manager
    orig_run = Manager.run

    def run(self):
        orig_run(self)

        for pattern, ignores in spec:
            ignored = set()
            checkers = []
            for checker in self.checkers:
                if pattern.match(os.path.normpath(checker.display_name)):
                    results = []
                    for result in checker.results:
                        for code in ignores:
                            if result[0].startswith(code):
                                ignored.add(code)
                                break
                        else:
                            results.append(result)
                    checker.results = results
                    checkers.append(checker)

            redundant = ignores - ignored
            if redundant:
                text = ('Superfluous per-file-ignores for ' +
                        ','.join(sorted(redundant)))
                for checker in checkers:
                    checker.report('X100', 0, 0, text)

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
        parser.extend_default_select(['X100'])

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
