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
EXT=ios-$(uname)-$(uname -m)-$VER
cd ../src/frameworks/
echo "Get latest framework"
./get_frameworks.sh
cd -
VER=$(python3 ./extract.py)
mv dist/instrument dist/applitoolsify-$VER
jfrog rt u dist/applitoolsify-$VER nmg/ios/instrumentation/release/__/applitoolsify-$VER
echo "Uploaded to nmg/ios/instrumentation/release/__/applitoolsify-$VER "
