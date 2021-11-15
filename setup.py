import codecs
import re
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version(package_name):
    version_file = read("applitoolsify/applitoolsify.py")
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


setup(
    name="applitoolsify",
    version=get_version("applitoolsify"),
    packages=find_packages(),
    url="http://www.applitools.com",
    author="Applitools Team",
    author_email="team@applitools.com",
    description="Applitools Mobile Native helper",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="applitools eyes eyes_selenium",
    package_data={
        "": ["README.rst", "LICENSE"],
        "applitoolsify": [
            "py.typed",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/applitools/applitoolsify/issues",
        "Source": "https://github.com/applitools/applitoolsify/tree/master"
        "/applitoolsify",
    },
    entry_points={
        "console_scripts": ["applitoolsify=applitoolsify"],
    },
)
