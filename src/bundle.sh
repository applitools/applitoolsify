#!/bin/bash -e

which pyinstaller &>/dev/null
FOUND="$?"

if [ $FOUND != 0 ]; then
    echo "pyinstaller not found in path, please make sure you have pyinstaller by pip install pyinstaller"
    exit 1
fi
VER=$(git rev-parse --short HEAD)
cd ../src/frameworks/
echo "Get latest framework"
./get_frameworks.sh
cd -
echo "Making binary version"
pyinstaller instrument.spec
echo "After pyinstaller"
VER=$(python3 ./extract.py)
ARCH=$(uname)
if [ $ARCH == 'Darwin' ]; then
    ARCH='macos'
fi
INJ_VER=$(git describe --tags)
EXT=ios-$ARCH-$(uname -m)
EXT_VER=$EXT-$VER
mv dist/instrument dist/applitoolsify-$EXT
jf rt u dist/applitoolsify-$EXT mobile/ios/applitoolsify/release/applitoolsify-$EXT
jf rt u dist/applitoolsify-$EXT mobile/ios/applitoolsify/$VER/$INJ_VER/applitoolsify-$EXT
echo "Uploaded to mobile/ios/applitoolsify/$VER/$INJ_VER/applitoolsify-$EXT"
echo "Uploaded to mobile/ios/applitoolsify/release/applitoolsify-$EXT"
