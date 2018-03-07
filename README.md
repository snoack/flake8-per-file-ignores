# flake8-per-file-ignores

[![Build Status][1]][2]
[![Pypi Entry][3]][4]

An extension for [flake8][5] that lets you configure (out-of-source) individual
error codes to be ignored per file.

This is mostly useful when dealing with legacy code, so that you don't have to
ignore any existing error globally, but get the benefits of all checks in new
files, while you avoid introducing new kind of errors in existing files.

The advantage over inline `# noqa` comments is, that it doesn't clutter your
source files or even requires touching them.

## Installation

    pip install flake8-per-file-ignores

## Configuration

You can can use following configuration syntax in any [configuration file
considered by flake8][6]:

    [flake8]
    per-file-ignores =
      <filename>: <error>[,<error>[,...]]
      [...]

* `filename` is a [glob pattern][7] matching the filename of the script.
  If it starts with a slash, it must be a path relative to the directory,
  flake8 is running from.
* `error` has the same semantics as the [`--ignore` command line option][8].

If an error to be ignored, no longer occurs for a given file, this will
cause an `X100` error, in order to make you progressively reduce the number
of ignores as legacy code gets rewritten or removed.

For an example see the [`test` folder][9].

[1]: https://travis-ci.org/snoack/flake8-per-file-ignores.svg?branch=master
[2]: https://travis-ci.org/snoack/flake8-per-file-ignores
[3]: https://badge.fury.io/py/flake8-per-file-ignores.svg
[4]: https://pypi.python.org/pypi/flake8-per-file-ignores
[5]: https://gitlab.com/pycqa/flake8
[6]: http://flake8.pycqa.org/en/latest/user/configuration.html#configuration-locations
[7]: https://en.wikipedia.org/wiki/Glob_(programming)
[8]: http://flake8.pycqa.org/en/latest/user/options.html#cmdoption-flake8-ignore
[9]: https://github.com/snoack/flake8-per-file-ignores/tree/master/test
