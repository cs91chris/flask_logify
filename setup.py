"""
Flask-Logify
-------------

Logging configuration for flask application
"""
import os
import re
import sys

from setuptools.command.test import test
from setuptools import setup, find_packages

BASE_PATH = os.path.dirname(__file__)
VERSION_FILE = os.path.join("flask_logify", "version.py")


def read(file):
    """

    :param file:
    :return:
    """
    with open(os.path.join(BASE_PATH, file)) as f:
        return f.read()


def grep(file, name):
    """

    :param file:
    :param name:
    :return:
    """
    (value,) = re.findall(rf"{name}\W*=\W*'([^']+)'", read(file))
    return value


def readme(file):
    """

    :param file:
    :return:
    """
    try:
        return read(file)
    except OSError as exc:
        print(str(exc), file=sys.stderr)


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)

    def run_tests(self):
        # noinspection PyUnresolvedReferences
        import pytest

        sys.exit(pytest.main(["tests"]))


setup(
    license="MIT",
    name="Flask-Logify",
    url="https://github.com/cs91chris/flask_logify",
    version=grep(VERSION_FILE, "__version__"),
    author=grep(VERSION_FILE, "__author_name__"),
    author_email=grep(VERSION_FILE, "__author_email__"),
    description="Logging configuration for flask application",
    long_description=readme("README.rst"),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=["Flask", "PyYAML"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
