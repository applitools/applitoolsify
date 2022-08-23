import os
import shutil
import sys
from pathlib import Path

from .base import BaseInstrumentifyStrategy


class AndroidInstrumentifyStrategy(BaseInstrumentifyStrategy):
    """
    Patch Android `apk` with default SDK (XXX: Support multiple sdks).

    This is a very basic implementation essentially calling the main
    script for android injector provided in the zip file
    """

    ARTIFACT_DIR = "instrumented-apk"

    @property
    def app_frameworks(self):
        # Not used for android, kept bc required
        return self.path_to_app.joinpath("Frameworks")

    def instrumentify(self):
        # type: () -> bool
        print("Preparing application...")
        # os.chdir is required because we want to create our directories under applitoolsify NMG_lib dir
        # but still allow them to run in standalone mode
        instrumentation_folder = self.sdk_data.sdk_location.parent
        os.chdir(self.sdk_data.sdk_location)
        work_dir = Path(os.getcwd())

        # Prepare output directory
        artifact_dir = instrumentation_folder.parent.joinpath(self.ARTIFACT_DIR)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        # Import module that handels injection
        sys.path.insert(0, str(instrumentation_folder))
        import NMG_lib

        log_loc = work_dir.joinpath("android-nmg.log")
        log_tgt = artifact_dir.joinpath("android-nmg.log")
        try:
            out_dir = NMG_lib.patchnfill.run(self.path_to_app)
            apk_loc = (
                Path(out_dir).joinpath("final.apk").joinpath("out-aligned-signed.apk")
            )

        except Exception as e:
            # sometimes log file doesn't present which raise an exception during copying
            if log_loc.exists():
                shutil.copyfile(log_loc, log_tgt)
                print(
                    f"Instrumentation failed with error: {e}. Please submit `{log_tgt}` to applitools"
                )
            else:
                print(f"Instrumentation failed with error: {e}. No log file")
            return False
        # all jazz below is just to rename the original outputs from our code to a proper artifacts directory
        # (it used to be much more complicated (; )

        shutil.copyfile(log_loc, log_tgt)
        print("Collecting artifacts")
        target_file = artifact_dir.joinpath("ready.apk")
        ret = shutil.move(apk_loc, target_file)
        return ret == target_file
