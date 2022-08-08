from applitoolsify.entities import SdkData, SdkParams

__version__ = "0.2.0"


FILES_COPY_SKIP_LIST = [".DS_Store"]
VERBOSE = False

SUPPORTED_FRAMEWORKS = {
    SdkParams.android_nmg: SdkData(
        **{
            "name": "NMG_lib",
            "download_url": "https://applitools.jfrog.io/artifactory/nmg/android/instrumentation/NMG_lib.zip",
        }
    ),
    SdkParams.ios_nmg: SdkData(
        **{
            "name": "UFG_lib.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/nmg/ios/instrumentation/UFG_lib.xcframework.zip",
        }
    ),
    SdkParams.ios_classic: SdkData(
        **{
            "name": "EyesiOSHelper.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/iOS/EyesiOSHelper/EyesiOSHelper.zip",
        }
    ),
}
