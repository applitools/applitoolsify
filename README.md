# Applitoolsify
Add Applitools SDKs (`UFG_lib.xcframework` and\or `EyesiOSHelper.xcframework`) to `ipa` and `app` iOS apps.

## Install
`curl -O https://raw.githubusercontent.com/applitools/applitoolsify/main/applitoolsify.py`

## Usage
`python applitoolsify.py <path-to-app> <sdk-to-patch> <optional certificate name> <optional provisioning profile>`

## Example instrumentation of `app`
Instrument with `EyesiOSHelper.xcframework`

`python  applitoolsify.py "some.app" ios_classic`

Instrument with `UFG_lib.xcframework`

`python  applitoolsify.py "some.app" ios_ufg`

## Example instrumentation of `ipa` without signing
Instrument with `UFG_lib.xcframework`

`python  applitoolsify.py "some.app" ios_ufg`

Instrument with `EyesiOSHelper.xcframework`

`python  applitoolsify.py "some.ipa" ios_classic`
