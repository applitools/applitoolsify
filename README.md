# Applitoolsify
## Install
$ git clone git@github.com:applitools/applitoolsify.git # Get the code

$ pushd applitoolsify/src/frameworks # Update framework

$ ./get_frameworks.sh

$ popd

## Usage
$ pushd applitoolsify

$ python applitoolsify.py <path-to-app> 

## Pre-requirements
* Python 3.7+ version
* On Windows you need to [verify that LongPathsEnabled](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell) parameter is set.

## Examples
`python  applitoolsify.py "some.app"`

`python  applitoolsify.py "some.ipa"`
