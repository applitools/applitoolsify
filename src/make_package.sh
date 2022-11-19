#!/bin/bash -e

pyinstaller --onefile ./instrument.py
mv dist/instrument applitoolsify-ios
