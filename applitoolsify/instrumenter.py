import os
import shutil
from pathlib import Path

from .entities import SdkData
from .instrument_strategies import (
    AndroidInstrumentifyStrategy,
    IOSAppInstrumentifyStrategy,
    IOSIpaInstrumentifyStrategy,
)
from .utils import print_verbose


class Instrumenter(object):
    """Allow to instrumentify specific application with Applitools SDK."""

    instrument_strategies = {
        "app": IOSAppInstrumentifyStrategy,
        "ipa": IOSIpaInstrumentifyStrategy,
        "apk": AndroidInstrumentifyStrategy,
    }

    def __init__(
        self,
        path_to_app,
        sdk_data,
        signing_certificate_name=None,
        provisioning_profile=None,
    ):
        # type: (str, SdkData, str, str) -> None
        self.path_to_app = Path(path_to_app).absolute()
        self.app_name = path_to_app
        self.app_ext = self.path_to_app.suffix
        self.sdk_data = sdk_data
        self._instrumenter = self.instrument_strategies[self.app_ext.lstrip(".")](
            path_to_app=self.path_to_app,
            sdk_data=sdk_data,
            signing_certificate_name=signing_certificate_name,
            provisioning_profile=provisioning_profile,
        )

    def was_already_instrumented(self):
        # type: () -> bool
        if self._instrumenter.sdk_in_app_frameworks.exists():
            return True
        else:
            return False

    def instrumentify(self):
        # type: () -> bool
        # Obviously need refactoring
        android = self.app_ext.lstrip(".") == "apk"
        if not android and self.was_already_instrumented():
            print_verbose("App already instrumented. Updating...")
            # remove old installation
            shutil.rmtree(self._instrumenter.sdk_in_app_frameworks)
        if not self._instrumenter.instrumentify():
            print("Failed to instrument `{}`".format(self.path_to_app))
            return False
        print_verbose(
            "`{}` framework was added to `{}`".format(
                self.sdk_data.name, self._instrumenter.sdk_in_app_frameworks
            )
        )
        if android:
            print(
                "Application is ready at {}".format(
                    os.path.join(AndroidInstrumentifyStrategy.ARTIFACT_DIR, "ready.apk")
                )
            )
        else:
            print(
                "`{}` is ready for use with the `{}`".format(
                    self.path_to_app, self.sdk_data.name
                )
            )
        return True
