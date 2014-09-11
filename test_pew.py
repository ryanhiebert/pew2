import os
import sys
from pathlib import Path
from click.testing import CliRunner

import pew


class Runner(object):
    runner = CliRunner()


class TestContextManagers(Runner):
    def test_chdir_string(self):
        """Temporarily change the working directory to string path"""
        dirname = 'newdirectory'
        with self.runner.isolated_filesystem():
            Path(dirname).mkdir()

            cwd = os.getcwd()

            with pew.chdir(dirname):
                assert os.getcwd() == os.path.join(cwd, dirname)

            assert os.getcwd() == cwd

    def test_chdir_path(self):
        """Temporarily change the working directory to Path path"""
        dirname = Path('newdirectory')
        with self.runner.isolated_filesystem():
            dirname.mkdir()

            cwd = os.getcwd()

            with pew.chdir(dirname):
                assert os.getcwd() == os.path.join(cwd, str(dirname))

            assert os.getcwd() == cwd

    def test_temp_environ(self):
        """Temporarily allow arbitrary changes to the environment"""
        old_environ = dict(os.environ)
        with pew.temp_environ():
            os.environ['X'] = 'x'
            os.environ['Y'] = 'y'
            os.environ['Z'] = 'z'
            assert dict(os.environ) != old_environ
            assert all(k in os.environ for k in 'XYZ')

        assert dict(os.environ) == old_environ


class TestEnvHelpers(object):
    def test_workon_home(self):
        cwd = os.getcwd()
        with pew.temp_environ():
            os.environ['WORKON_HOME'] = cwd
            assert pew.workon_home() == Path(cwd)

    def test_workon_home_expanduser(self):
        path = '~/path'
        with pew.temp_environ():
            os.environ['WORKON_HOME'] = path
            assert pew.workon_home() == Path(os.path.expanduser(path))

    def test_virtual_env(self):
        cwd = os.getcwd()
        with pew.temp_environ():
            os.environ['VIRTUAL_ENV'] = cwd
            assert pew.virtual_env() == Path(cwd)
