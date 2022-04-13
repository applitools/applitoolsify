# Applitoolsify
Add Applitools SDKs (`UFG_lib.xcframework` and\or `EyesiOSHelper.xcframework`) to `ipa` and `app` iOS apps.

## Install
`curl -O https://raw.githubusercontent.com/applitools/applitoolsify/main/applitoolsify.py`

## Usage
`python -m applitoolsify.py <path-to-app> <sdk> `

* On Windows you need to [verify that LongPathsEnabled](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell) parameter is set.

Parameters:
* _sdk_ - `ios_classic` | `ios_nmg` | `android_nmg`

## Examples

`python  applitoolsify.py "some.app" ios_classic`

`python  applitoolsify.py "some.ipa" ios_nmg`

`python  applitoolsify.py "some.apk" android_nmg`
