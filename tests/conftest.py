import codecs
import os
import shutil
import zipfile
from os import path

import pytest

here = path.dirname(path.abspath(__file__))


def get_resource_path(name):
    resource_dir = path.join(here, "resources")
    return path.join(resource_dir, name)


def get_resource(pth):
    with codecs.open(pth, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture()
def path_to_app_zip(tmpdir):
    # type: (...) -> str
    app_pth = get_resource_path("IOSTestApp.zip")
    shutil.copy2(app_pth, str(tmpdir))
    return str(tmpdir.join("IOSTestApp.zip"))


@pytest.fixture()
def path_to_ipa(tmpdir):
    # type: (...) -> str
    ipa_path = get_resource_path("IOSTestApp.ipa")
    shutil.copy2(ipa_path, str(tmpdir))
    return str(tmpdir.join("IOSTestApp.ipa"))


@pytest.fixture()
def path_to_app(tmpdir):
    # type: (...) -> str
    pth = get_resource_path("IOSTestApp.zip")
    with zipfile.ZipFile(pth) as zfile:
        zfile.extractall(str(tmpdir))
    return str(tmpdir.join("IOSTestApp.app"))


@pytest.fixture()
def path_to_apk(tmpdir):
    # type: (...) -> str
    app_pth = get_resource_path("eyes-android-hello-world.apk")
    shutil.copy2(app_pth, str(tmpdir))
    return str(tmpdir.join("eyes-android-hello-world.apk"))


@pytest.fixture
def sauce_driver_url():
    return "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
        os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]
    )
