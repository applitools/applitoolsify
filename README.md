# Applitoolsify
Add Applitools SDKs to your application:
* iOS apps: `UFG_lib.xcframework` and\or `EyesiOSHelper.xcframework` to `ipa` and `app` .
* Android apps: `NMG_lib.zip`

## Install
`curl -O https://raw.githubusercontent.com/applitools/applitoolsify/main/applitoolsify.py`

## Pre-requirements
* Python 3.7+ version
* On Windows you need to [verify that LongPathsEnabled](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell) parameter is set.
* For patching Android apk the Java version must be 11+.

## Usage
`python applitoolsify.py <path-to-app> <sdk> `

Parameters:
* _sdk_ - `ios_classic` | `ios_nmg` | `android_nmg`

## Examples

`python  applitoolsify.py "some.app" ios_classic`

`python  applitoolsify.py "some.ipa" ios_nmg`

`python  applitoolsify.py "some.apk" android_nmg`
