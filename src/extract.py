import plistlib
import zipfile
import os
archive = zipfile.ZipFile(f'.{os.sep}frameworks{os.sep}Applitools_iOS.xcframework.zip', 'r')
inner_loc = f"Applitools_iOS.xcframework/ios-arm64/Applitools_iOS.framework/Info.plist"
imgdata = archive.read(inner_loc)

pl = plistlib.loads(imgdata)

print(f"{pl['CFBundleShortVersionString']}.{pl['CFBundleVersion']}")
