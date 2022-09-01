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

from tests.utils import applitoolsify_cmd, upload_app_to_sauce, zip_dir


def test_applitoolsify_ios_app(path_to_app, sauce_driver_url):
    applitoolsify_cmd(path_to_app, "ios_nmg")

    path_to_app_zip = f"{path_to_app}.zip"
    app_name_on_sauce = "e2e_applitoolsify_test.app.zip"
    zip_dir(path_to_app, path_to_app_zip)
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
    path_to_apk = applitoolsify_cmd(path_to_apk, "android_nmg")

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
