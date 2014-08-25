import os
import sys
from subprocess import check_call
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


@pew.command()
@click.argument('venv')
@pass_context
def workon(ctx, venv):
    """Enter a virtual environment"""
    path = ctx.workon_home / venv
    if not path.exists():
        sys.exit("Environment '{}' does not exist.".format(venv))

    inve = path / bin / 'inve'

    args = ['powershell' if windows else os.environ['SHELL']]
    or_ctrld = '' if windows else "or 'Ctrl+D' "
    click.echo("Launching subshell in virtual environment. Type "
               "'exit' {}to return.\n".format(or_ctrld), err=True)

    check_call(['python', str(inve)] + args)
