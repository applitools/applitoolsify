import os
import subprocess
import sys
import zipfile
from pathlib import Path
from pprint import pprint

sys.path.append(str(Path(__file__).parent.parent / "src"))

from applitoolsify.instrument_strategies import AndroidInstrumentifyStrategy


def applitoolsify_cmd(path_to_app, sdk):
    # type: (Path | str, str) -> Path
    work_dir = Path(sys.path[0])
    os.chdir(work_dir)  # switch to applitoolsify directory

    cmd = "applitoolsify.pyz"
    if not Path(cmd).exists():
        output = subprocess.run(["make", "build-pyz"])

    output = subprocess.run(
        [
            "python",
            cmd,
            str(path_to_app),
            sdk,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    pprint(output)
    output.check_returncode()
    if "Failed to instrument" in output.stdout:
        raise Exception(f"Failed to patch {path_to_app}")
    if sdk == "android_nmg":
        return work_dir.joinpath(AndroidInstrumentifyStrategy.ARTIFACT_DIR, "ready.apk")
    return path_to_app


def upload_app_to_sauce(path_to_app_archive: str, app_name_on_sauce: str) -> int:
    import requests

    with open(path_to_app_archive, "rb") as f:
        r = requests.post(
            "https://api.us-west-1.saucelabs.com/v1/storage/upload",
            files={"payload": f},
            data={"name": app_name_on_sauce},
            auth=(os.getenv("SAUCE_USERNAME"), os.getenv("SAUCE_ACCESS_KEY")),
        )
    r.raise_for_status()
    return r.status_code


def zip_dir(dirpath, zippath):
    with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as zfile:
        for root, dirs, files in os.walk(dirpath):
            if os.path.basename(root)[0] == ".":
                continue  # skip hidden directories
            for f in files:
                if f[-1] == "~" or (f[0] == "." and f != ".htaccess"):
                    # skip backup files and all hidden files except .htaccess
                    continue
                zfile.write(os.path.join(root, f))
