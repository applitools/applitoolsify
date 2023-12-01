#!/bin/bash -e

cd frameworks
./get_frameworks.sh
cd -
cd ..
loc=$(pwd)
PATH=$(basename $loc)
cd ..
/usr/bin/zip -r "applitoolsify.zip" "$PATH"
