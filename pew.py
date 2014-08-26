import os
import sys
import shutil
from subprocess import check_call
from contextlib import contextmanager
from pathlib import Path

import click


__meta__ = type


windows = sys.platform == 'win32'
bin = 'Scripts' if windows else 'bin'


class Context:
    """Manage the context of commands"""

    def __init__(self):
        """Shared script context"""
        virtual_env = os.environ.get('VIRTUAL_ENV')
        workon_home = os.path.expanduser(os.environ.get('WORKON_HOME', ''))

        if not workon_home:
            sys.exit('WORKON_HOME not set')

        self.workon_home = Path(workon_home)
        self.virtual_env = None
        if virtual_env:
            self.virtual_env = Path(virtual_env)

    def envs(self, path):
        """List all virtual environments in path"""
        home = self.workon_home / path
        pythons = home.glob('*/{}/python'.format(bin))
        envs = set(path.parent.parent.relative_to(home) for path in pythons)
        return envs

    def dirs(self, path):
        """List all directories that aren't virtual environments in path"""
        home = self.workon_home / path
        dirs = set(f.relative_to(home) for f in home.iterdir() if f.is_dir())
        return dirs - self.envs(path)


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
def pew():
    """Manage your virtual environments"""


@pew.command()
@pass_context
def show(ctx):
    """Show the active virtual environment"""
    click.echo(ctx.virtual_env or 'No virtual environment active.')


@pew.command()
@click.argument('path', default='')
@pass_context
def ls(ctx, path):
    """List available virtual environments"""
    envs = [str(env) for env in ctx.envs(path)]
    dirs = [str(dir) + '/' for dir in ctx.dirs(path)]
    click.echo(' '.join(sorted(envs + dirs)))


@pew.command(name='in')
@click.argument('env')
@click.argument('command', required=False)
@click.argument('args', nargs=-1)
@pass_context
def inve(ctx, env, command, args):
    """Enter a virtual environment"""
    path = ctx.workon_home / env
    if not path.exists():
        sys.exit("Environment '{}' does not exist.".format(env))

    if not command:
        command = 'powershell' if windows else os.environ['SHELL']

    with temp_environ():
        os.environ['VIRTUAL_ENV'] = str(path)
        os.environ['PATH'] = os.pathsep.join(
            [str(path / bin), os.environ['PATH']])

        os.unsetenv('PYTHONHOME')
        os.unsetenv('__PYVENV_LAUNCHER__')

        try:
            return check_call([command] + list(args), shell=windows)
            # need to have shell=True on windows, otherwise the PYTHONPATH
            # won't inherit the PATH
        except OSError as e:
            if e.errno == 2:
                click.echo('Unable to find {}'.format(command))
            else:
                raise


@pew.command()
@click.argument('env')
@click.option('--python', '-p', help='Path to Python interpreter.')
@pass_context
def new(ctx, env, python):
    """Create a new virtual environment"""
    path = ctx.workon_home / env
    extra = ['--python={}'.format(python)] if python else []
    check_call(['virtualenv', str(path)] + extra)


@pew.command()
@click.argument('envs', nargs=-1)
@pass_context
def rm(ctx, envs):
    """Remove virtual environments."""
    for env in envs:
        path = ctx.workon_home / env
        if path == ctx.virtual_env:
            sys.exit('You cannot remove the active environment.')
        shutil.rmtree(str(path))


@contextmanager
def temp_environ():
    environ = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(environ)
