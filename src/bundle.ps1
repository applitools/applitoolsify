# jfrog identifier, passed in from caller
$apiKey = $args[0]
echo "Installing pyinstaller"
# Import jfrog config so we can upload our artifacts later
jfrog config import $apiKey
# Install pyinstaller
pip install pyinstaller
# Handle frameworks for standalone mode
cd ..\src\frameworks\
echo "Get latest framework"
.\get_frameworks.ps1
cd -
# Get injection version with g prefix for binary
$VER = $(python3 ./extract.py)
$ARCH = 'win'
echo "Making binary version"
pyinstaller instrument.spec
echo "After pyinstaller"
# Construct artifact filename
$INJ_VER=$(git describe --tags)
$EXT = "ios-$ARCH-x86_64.exe"
$EXT_VER = "$EXT-$VER.exe"

echo "Upload release binary"
jfrog rt u "dist/applitoolsify-$EXT" "mobile/ios/applitoolsify/release/applitoolsify-$EXT"
jfrog rt u "dist/applitoolsify-$EXT" "mobile/ios/applitoolsify/$VER/$INJ_VER/applitoolsify-$EXT"

echo "artifact: $ARTIFACT"
echo "tgt_artifact: $TGT_ARTIFACT"
echo "URL: https://applitools.jfrog.io/artifactory/$TGT_ARTIFACT"
