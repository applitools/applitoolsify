import codecs
import re
import sys
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version(package_name):
    version_file = read("{}/__version__.py".format(package_name))
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


install_requires = ["requests"]

#
# if sys.version_info[:2] <= (2, 7):
#     install_requires.append("tinycss2==0.6.1")
# else:
#     install_requires.append("tinycss2>=0.6.1,<1.1.0")

# using this way of defining instead of 'typing>=3.5.2; python_version<="3.4"'
# for run on old version of setuptools without issues
if sys.version_info[:2] < (3, 5):
    # typing module was added as builtin in Python 3.5
    install_requires.append("typing >= 3.5.2")

# if sys.version_info[:1] < (3,):
#     install_requires.append("futures==3.2.0")

# brotli doesn't have binary distribution on py27/win64
# so let's use brotlipy there to avoid requirement to have msvc to build
# if sys.version_info[:1] < (3,) and sys.platform.startswith("win"):
#     install_requires.append("brotlipy==0.7.0")
# else:
#     install_requires.append("brotli>=1.0.9")

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
    install_requires=install_requires,
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
