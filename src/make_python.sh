#!/bin/bash -e

cd frameworks
./get_frameworks.sh
cd -
cd ..
loc=$(pwd)
CWD=$(basename $loc)
cd ..
/usr/bin/zip -r "applitoolsify-ios.zip" "$CWD"
