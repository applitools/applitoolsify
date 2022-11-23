#!/bin/bash -e

pyinstaller ./instrument.spec
mv dist/instrument applitoolsify-ios
