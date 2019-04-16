#!/usr/bin/env python3
import click
import subprocess


def run(cmd):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    subprocess.call(cmd, shell=True)


@click.group()
def tasks():
    pass


@tasks.command()
def build():
    run('rm -rf dist/*')
    run('python3 setup.py sdist bdist_wheel')


@tasks.command()
def deploy():
    run('twine upload dist/*')


if __name__ == '__main__':
    tasks()
