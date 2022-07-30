import shutil
from pathlib import Path

from tests.utils import applitoolsify_cmd


def test_instrument_apk_absolute_path(path_to_apk):
    artifacts_dir = Path(__file__).parent.parent.joinpath("instrumented-apk")
    try:
        applitoolsify_cmd(path_to_apk, "android_nmg")
        assert artifacts_dir.joinpath("ready.apk").exists()
    finally:
        shutil.rmtree(artifacts_dir, ignore_errors=True)


def test_instrument_apk_relative_path(path_to_apk_relative_to_applitoolsify):
    artifacts_dir = Path(__file__).parent.parent.joinpath("instrumented-apk")
    try:
        applitoolsify_cmd(path_to_apk_relative_to_applitoolsify, "android_nmg")
        assert artifacts_dir.joinpath("ready.apk").exists()
    finally:
        shutil.rmtree(artifacts_dir, ignore_errors=True)
