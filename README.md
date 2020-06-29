## Azure Maps Creator Tools

## Features

This project framework provides the following features:

* Uploads DWG files to Azure Maps Creator

## Getting Started

### **Please Note**: This script works with Python3

# Installation

1. Download Python3.6 via this [link](https://www.python.org/ftp/python/3.6.0/python-3.6.0-amd64.exe).

2. Run the downloaded installer. When the installer opens, remember to select the checkbox to add **Python to PATH**

3. Once done, open **PowerShell** / **Command Line** and run the command `pip install requests`

# Upload DWG Zip file

To upload your zipped `DWG` files to Azure Maps Creator, simply download and run the PowerShell script `DWGZipUploader.py` and parse the following arguments as seen below.

```
python DWGZipUploader.py --subscriptionKey YOUR_SUBSCRIPTION_KEY --zipFile PATH_TO_YOUR_ZIP_FILE
```

You should see a log like the one below if the process completes succesfully without errors.

```
Reading zip file...
Uploading DWG Zip file...
DWG Upload accepted.
Checking upload status...
DWG upload successful.
Obtaining UDID...
UDID obtained.
Converting DWG...
DWG Conversion started...
DWG conversion successful
Dataset generation started...
Dataset generated successfully.
Tileset generation started...
Tileset generated successfully.
Generated Map data saved to 'AzureMapData.json'
Generated Map saved to 'Map.html'
```

Once done, the process will save a `AzureMapsData.json` and `Maps.html` in the same folder as the script. To view the generated Map, simply open `Maps.html` in the browser. All the values returned by the Azure Maps Creator API is contained in the `AzureMapsData.json`

