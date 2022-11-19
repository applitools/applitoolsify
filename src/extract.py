import plistlib
import zipfile
archive = zipfile.ZipFile('./frameworks/UFG_lib.xcframework.zip', 'r')
inner_loc = "UFG_lib.xcframework/ios-arm64/UFG_lib.framework/Info.plist"
imgdata = archive.read(inner_loc)

pl = plistlib.loads(imgdata)

print(f"{pl['CFBundleShortVersionString']}.{pl['CFBundleVersion']}")
