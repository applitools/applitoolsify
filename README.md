# Applitoolsify
## Install
$ git clone git@github.com:applitools/applitoolsify.git # Get the code
$ pushd applitoolsify/src/frameworks # Update framework
$ ./get_frameworks.sh
$ popd

## Usage
$ pushd applitoolsify
$ python applitoolsify.py <path-to-app> <sdk>

## Pre-requirements
* Python 3.7+ version
* On Windows you need to [verify that LongPathsEnabled](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell) parameter is set.

Parameters:
* _sdk_ - `ios_classic` | `ios_nmg`

## Examples
`python  applitoolsify.py "some.app" ios_classic`
`python  applitoolsify.py "some.ipa" ios_nmg`
