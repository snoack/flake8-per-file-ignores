import os
import pkg_resources


def patch_flake8(spec):
    from flake8.checker import Manager
    orig_handle_results = Manager._handle_results

    def _handle_results(self, filename, results):
        final_results = []
        ignores = spec.get(os.path.normpath(filename)) or set()
        ignored = set()

        for result in results:
            for code in ignores:
                if result[0].startswith(code):
                    ignored.add(code)
                    break
            else:
                final_results.append(result)

        redundant = ignores - ignored
        if redundant:
            text = ('Superfluous per-file-ignores for ' +
                    ','.join(sorted(redundant)))
            final_results.append(('X100', 0, 0, text, ''))

        return orig_handle_results(self, filename, final_results)

    Manager._handle_results = _handle_results


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
        spec = {}
        if options.per_file_ignores:
            for line in options.per_file_ignores.splitlines():
                if ':' in line:
                    filename, ignores = line.rsplit(':', 1)
                    spec[filename.strip()] = \
                        {x.strip() for x in ignores.split(',')} - {''}
        if spec:
            patch_flake8(spec)
