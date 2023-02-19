#!/bin/bash -e

cd ../src/frameworks/
./get_frameworks.sh
cd -
pyinstaller ./instrument.spec
mv dist/instrument applitoolsify-ios
