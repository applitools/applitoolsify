FOR /F "tokens=*" %%g IN ('git rev-parse --short HEAD') do (SET VER=%%g)
echo "Making binary version"
pyinstaller --onefile ./instrument.py
SET EXT=ios-windows-%VER%
move dist\instrument.exe dist\applitoolsify-%EXT%.exe
jf rt u dist\applitoolsify-%EXT%.exe nmg/android/instrumentation/applitoolsify-%EXT%.exe
echo "Uploaded to Testrepo/nmg/android/instrumentation/applitoolsify-%EXT%.exe"
