import os
import sys
from glob import glob

import click


__meta__ = type


bin = 'Scripts' if sys.platform == 'win32' else 'bin'


class Context:
    """Manage the context of commands"""

    def envs(self):
        return sorted(set(
            env.split(os.path.sep)[-3] for env in
            glob(os.path.join(self.workon_home, '*', bin, 'python*'))))


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@pass_context
def pew(ctx):
    """Manage your virtual environments"""
    ctx.virtual_env = os.environ.get('VIRTUAL_ENV')
    ctx.workon_home = os.path.expanduser(os.environ.get('WORKON_HOME'))


@pew.command()
@pass_context
def show(ctx):
    """Show the active virtual environment"""
    click.echo(ctx.virtual_env or 'No virtual environment active.')


@pew.command()
@pass_context
def ls(ctx):
    """List available virtual environments"""
    click.echo(' '.join(ctx.envs()))


@pew.command()
@click.argument('venv')
@pass_context
def workon(ctx, venv):
    """Enter a virtual environment"""
    click.echo(venv)
