import plistlib
import zipfile
import os

archive = zipfile.ZipFile(f'.{os.sep}frameworks{os.sep}UFG_lib.xcframework.zip', 'r')
inner_loc = f"UFG_lib.xcframework{os.sep}ios-arm64{os.sep}UFG_lib.framework{os.sep}Info.plist"
imgdata = archive.read(inner_loc)

pl = plistlib.loads(imgdata)

print(f"{pl['CFBundleShortVersionString']}.{pl['CFBundleVersion']}")
