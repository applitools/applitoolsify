#!/bin/bash -e

which pyinstaller &>/dev/null
FOUND="$?"

if [ $FOUND != 0 ]; then
    echo "pyinstaller not found in path, please make sure you have pyinstaller by pip install pyinstaller"
    exit 1
fi
VER=$(git rev-parse --short HEAD)
echo "Making binary version"
pyinstaller instrument.spec
echo "After pyinstaller"
cd ../src/frameworks/
echo "Get latest framework"
./get_frameworks.sh
cd -
VER=$(python3 ./extract.py)
ARCH=$(uname)
if [ $ARCH == 'Darwin' ]; then
    ARCH='macos'
EXT=ios-$ARCH-$(uname -m)-$VER
mv dist/instrument dist/applitoolsify-$EXT
jf rt u dist/applitoolsify-$EXT nmg/ios/instrumentation/release/__/applitoolsify-$EXT
echo "Uploaded to nmg/ios/instrumentation/release/__/applitoolsify-$EXT"
