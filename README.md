# Applitoolsify
Add Applitools SDKs (`UFG_lib.xcframework` and\or `EyesiOSHelper.xcframework`) to `ipa` and `app` iOS apps.

## Install
`curl -O https://raw.githubusercontent.com/applitools/applitoolsify/main/applitoolsify.py`

## Usage
`python -m applitoolsify.py <path-to-app> <sdk> `

Parameters:
* _sdk_ - `ios_classic` or `ios_ufg`

## Examples

`python  applitoolsify.py "some.app" ios_classic`

`python  applitoolsify.py "some.ipa" ios_ufg`
