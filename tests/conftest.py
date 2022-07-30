import codecs
import os
import shutil
import zipfile
from pathlib import Path

import pytest

here = Path(__file__).absolute().parent


def get_resource_path(name) -> Path:
    resource_dir = here / "resources"
    return resource_dir / name


def get_resource(pth) -> str:
    with codecs.open(pth, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture()
def path_to_app_zip(tmpdir) -> Path:
    app_pth = get_resource_path("IOSTestApp.zip")
    shutil.copy2(app_pth, str(tmpdir))
    return Path(tmpdir.join("IOSTestApp.zip"))


@pytest.fixture()
def path_to_ipa(tmpdir) -> Path:
    ipa_path = get_resource_path("IOSTestApp.ipa")
    shutil.copy2(ipa_path, str(tmpdir))
    return Path(tmpdir.join("IOSTestApp.ipa"))


@pytest.fixture()
def path_to_app(tmpdir) -> Path:
    pth = get_resource_path("IOSTestApp.zip")
    with zipfile.ZipFile(pth) as zfile:
        zfile.extractall(str(tmpdir))
    return Path(tmpdir.join("IOSTestApp.app"))


@pytest.fixture()
def path_to_app_relative_to_applitoolsify() -> str:
    pth = get_resource_path("IOSTestApp.zip")
    dst = here.parent / "IOSTestApp.app"
    try:
        with zipfile.ZipFile(pth) as zfile:
            zfile.extractall(dst)
        os.chdir(here.parent)
        yield "IOSTestApp.app"
    finally:
        shutil.rmtree(dst)


@pytest.fixture()
def path_to_ipa_relative_to_applitoolsify() -> str:
    pth = get_resource_path("IOSTestApp.ipa")
    dst = here.parent / "IOSTestApp.ipa"
    try:
        shutil.copy2(pth, dst)
        os.chdir(here.parent)
        yield "IOSTestApp.ipa"
    finally:
        os.remove(dst)


@pytest.fixture()
def path_to_apk_relative_to_applitoolsify() -> str:
    pth = get_resource_path("eyes-android-hello-world.apk")
    dst = here.parent / "eyes-android-hello-world.apk"
    try:
        shutil.copy2(pth, dst)
        os.chdir(here.parent)
        yield "eyes-android-hello-world.apk"
    finally:
        os.remove(dst)


@pytest.fixture()
def path_to_apk(tmpdir) -> Path:
    app_pth = get_resource_path("eyes-android-hello-world.apk")
    shutil.copy2(app_pth, str(tmpdir))
    return Path(tmpdir.join("eyes-android-hello-world.apk"))


@pytest.fixture
def sauce_driver_url() -> str:
    return "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
        os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]
    )
