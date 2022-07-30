import os
import subprocess
from pathlib import Path

import requests
from appium.webdriver import Remote
from applitools.common import (
    AndroidDeviceInfo,
    AndroidDeviceName,
    AndroidVersion,
    IosDeviceInfo,
    IosDeviceName,
    ScreenOrientation,
)
from applitools.selenium import Eyes, VisualGridRunner

from src.instrument import Archiver


def upload_app_to_sauce(path_to_app_archive: str, app_name_on_sauce: str) -> int:
    with open(path_to_app_archive, "rb") as f:
        r = requests.post(
            "https://api.us-west-1.saucelabs.com/v1/storage/upload",
            files={"payload": f},
            data={"name": app_name_on_sauce},
            auth=(os.getenv("SAUCE_USERNAME"), os.getenv("SAUCE_ACCESS_KEY")),
        )
    r.raise_for_status()
    return r.status_code


def applitoolsify(path_to_app, sdk):
    os.chdir(
        os.environ.get("GITHUB_WORKSPACE", Path(__name__).absolute().parent.parent)
    )
    os.environ["APPLITOOLSIFY_DEBUG"] = "True"
    output = subprocess.run(
        [
            "python",
            "applitoolsify.py",
            path_to_app,
            sdk,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    print(output)
    output.check_returncode()
    if output.stderr:
        raise Exception("Failed to patch")

def test_applitoolsify_ios_app(path_to_app, sauce_driver_url):
    applitoolsify(path_to_app, "ios_nmg")

    path_to_app_zip = f"{path_to_app}.zip"
    app_name_on_sauce = "e2e_applitoolsify_test.app.zip"
    Archiver.zip_dir(path_to_app, path_to_app_zip)
    upload_app_to_sauce(path_to_app_zip, app_name_on_sauce)

    caps = {
        "app": f"storage:filename={app_name_on_sauce}",
        "deviceName": "iPhone 12 Pro Simulator",
        "platformName": "iOS",
        "platformVersion": "15.2",
        "deviceOrientation": "portrait",
        "processArguments": {
            "args": [],
            "env": {
                "DYLD_INSERT_LIBRARIES": "@executable_path/Frameworks/UFG_lib.xcframework/"
                "ios-arm64_x86_64-simulator/UFG_lib.framework/UFG_lib"
            },
        },
    }
    with Remote(sauce_driver_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_mobile_device(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT)
        )
        eyes.open(driver, "Applitoolsify Test", "UFG native iOS applitoolsify")
        eyes.check_window()
        eyes.close_async()

        all_results = runner.get_all_test_results()

        assert all_results.passed == 1


def test_applitoolsify_android_apk(path_to_apk, sauce_driver_url):
    applitoolsify(path_to_apk, "android_nmg")

    app_name_on_sauce = "e2e_applitoolsify_test.apk"
    upload_app_to_sauce(path_to_apk, app_name_on_sauce)

    caps = {
        "app": f"storage:filename={app_name_on_sauce}",
        "deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
        "platformVersion": "10.0",
        "platformName": "Android",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "UiAutomator2",
        "name": "Pixel 3a xl (Python)",
        "appiumVersion": "1.20.2",
    }
    with Remote(sauce_driver_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_mobile_device(
            AndroidDeviceInfo(
                AndroidDeviceName.Pixel_4_XL, android_version=AndroidVersion.LATEST
            )
        )
        eyes.open(driver, "Applitoolsify Test", "UFG native Android applitoolsify")
        eyes.check_window()
        eyes.close()

        all_results = runner.get_all_test_results()

        assert all_results.passed == 1
