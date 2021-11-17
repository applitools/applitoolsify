# Applitoolsify
Add Applitools SDKs to `ipa` and `app` iOS apps.

## Install
There two options to install. One is from PyPi or second with direct download. 

### PyPi
`pip install applitoolsify`

### Direct download
`curl -O https://raw.githubusercontent.com/applitools/applitoolsify/main/applitoolsify/applitoolsify.py`


## Usage
### PyPi
`python -m applitoolsify <path-to-app> <sdk-to-patch> <optional certificate name> <optional provisioning profile>`

### Direct download
`python applitoolsify.py <path-to-app> <sdk-to-patch> <optional certificate name> <optional provisioning profile>`