import os
import sys
import shutil
from subprocess import check_call, call
from contextlib import contextmanager
from pathlib import Path

import click


windows = sys.platform == 'win32'
bin = 'Scripts' if windows else 'bin'

# Global variables used by pew
virtual_env, workon_home = None, None


def project_dir(path):
    """Get the project directory at the given path"""
    try:
        return Path((path / '.project').open().read().strip())
    except:
        return None


@click.group()
def pew():
    """Manage your virtual environments"""
    global virtual_env, workon_home

    virtual_env = os.environ.get('VIRTUAL_ENV')
    workon_home = os.path.expanduser(os.environ.get('WORKON_HOME', ''))

    if not workon_home:
        sys.exit('WORKON_HOME not set')

    workon_home = Path(workon_home)

    if virtual_env:
        virtual_env = Path(virtual_env)


@pew.command()
@click.option('--relative', is_flag=True,
              help='Attempt to construct a useful relative path.')
def show(relative):
    """Show the active virtual environment"""
    if not virtual_env:
        return

    if relative:
        try:
            return click.echo(virtual_env.relative_to(workon_home))
        except ValeuError:
            pass

    click.echo(virtual_env)


@pew.command()
@click.argument('path', default='')
def ls(path):
    """List available virtual environments"""
    home = workon_home / path

    # Virtual environments
    pythons = home.glob('*/{}/python*'.format(bin))
    envs = {path.parent.parent.relative_to(home) for path in pythons}

    # Directories that aren't virtual environments
    dirs = {f.relative_to(home) for f in home.iterdir() if f.is_dir()} - envs

    environments = [str(env) for env in envs]
    directories = [str(dir) + '/' for dir in dirs]  # Add slash to directories
    click.echo(' '.join(sorted(environments + directories)))


@pew.command(name='in')
@click.argument('env')
@click.argument('command', required=False)
@click.argument('args', nargs=-1)
def inve(env, command, args):
    """Enter a virtual environment"""
    path = workon_home / env
    if not path.exists():
        sys.exit("Environment '{}' does not exist.".format(env))

    if not command:
        command = 'powershell' if windows else os.environ['SHELL']

    with chdir(project_dir(path) or Path.cwd()), temp_environ():
        os.environ['VIRTUAL_ENV'] = str(path)
        os.environ['PATH'] = os.pathsep.join(
            [str(path / bin), os.environ['PATH']])

        os.unsetenv('PYTHONHOME')
        os.unsetenv('__PYVENV_LAUNCHER__')

        try:
            sys.exit(call([command] + list(args), shell=windows))
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
@click.option('--project', '-a', help='Path to project directory.')
def new(env, python, project):
    """Create a new virtual environment"""
    path = workon_home / env
    extra = ['--python={}'.format(python)] if python else []
    check_call(['virtualenv', str(path)] + extra)

    if project:
        (path / '.project').open('w').write(str(Path(project).absolute()))


@pew.command()
@click.argument('envs', nargs=-1)
def rm(envs):
    """Remove virtual environments"""
    for env in envs:
        path = workon_home / env
        if path == virtual_env:
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


@contextmanager
def chdir(dirname):
    curdir = os.getcwd()
    try:
        os.chdir(str(dirname))
        yield
    finally:
        os.chdir(curdir)
