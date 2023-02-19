#!/bin/bash -ex

which pyinstaller &>/dev/null
FOUND="$?"

if [ $FOUND != 0 ]; then
    echo "pyinstaller not found in path, please make sure you have pyinstaller by pip install pyinstaller"
    exit 1
fi
VER=$(git rev-parse --short HEAD)
echo "Making binary version"
pyinstaller ./instrument.spec
echo "After pyinstaller"
EXT=ios-$(uname)-$VER
cd ../src/frameworks/
echo "Get latest framework"
./get_frameworks.sh
cd -
pyinstaller ./instrument.spec
mv dist/instrument dist/applitoolsify-$EXT
jfrog rt u dist/applitoolsify-$EXT nmg/android/instrumentation/applitoolsify-$EXT
echo "Uploaded to Testrepo/nmg/android/instrumentation/applitoolsify-$EXT "

