from pathlib import Path

from ..config import SdkData


class BaseInstrumentifyStrategy(object):
    """Base Patch Strategy class. Helps to instrumentify app with specific SDK."""

    def __init__(
        self, path_to_app, sdk_data, signing_certificate_name, provisioning_profile
    ):
        # type: (Path, SdkData, str, str) -> None
        self.path_to_app = path_to_app
        self.sdk_data = sdk_data
        self.signing_certificate_name = signing_certificate_name
        self.provisioning_profile = provisioning_profile

    @property
    def app_frameworks(self):
        # type: () -> Path
        raise NotImplementedError

    @property
    def sdk_in_app_frameworks(self):
        # type: () -> Path
        return self.app_frameworks.joinpath(self.sdk_data.name)

    def instrumentify(self):
        # type: () -> bool
        raise NotImplementedError
