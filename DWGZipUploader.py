import os
import requests
import time
import json
import argparse
from zipfile import ZipFile


ap = argparse.ArgumentParser() 

ap.add_argument("-s", "--subscriptionKey", required=True,
    help="Your subscription key")
ap.add_argument("-z", "--zipFile", required=True,
    help="Path to zip file")
args = vars(ap.parse_args())


class MapsPipeline:
    def __init__(self, subcriptionKey):
        self.base_url = "https://us.atlas.microsoft.com/"
        self.subcriptionKey = subcriptionKey
        self.ResultUploadOperationsLocation = None
        self.ResultUploadAzureMapRegion = None
        self.ResultUploadDateTime = None
        self.ResultUploadOperationId = None
        self.ResultUploadStatus = None
        self.ResultUploadResourceLocation = None
        self.ResultUploadUDID = None
        self.ResultUploadMapDataLocation = None
        self.ResultUploadSizeInBytes = None

        self.ResultConvertOperationsLocation = None
        self.ResultConvertAzureMapsRegion = None
        self.ResultConvertDateTime = None
        self.ResultConvertStatus = None
        self.ResultConvertOperationId = None
        self.ResultConvertResourceLocation = None
        self.ResultConvertCreated = None
        self.ResultConvertId = None
        self.ResultConvertDescription = None
        self.ResultConvertFeatureCounts = None

        self.ResultDatasetOperationsLocation = None
        self.ResultDatasetAzureMapsRegion = None
        self.ResultDatasetDateTime = None
        self.ResultDatasetOperationId = None
        self.ResultDatasetResourceLocation = None
        self.ResultDatasetStatus = None
        self.ResultDatasetCreated = None
        self.ResultDatasetId = None

        self.ResultTilesetOperationsLocation = None
        self.ResultTilesetAzureMapsRegion = None
        self.ResultTilesetDateTime = None
        self.ResultTilesetStatus = None
        self.ResultTilesetOperationId = None
        self.ResultTilesetCreatedDateTime = None
        self.ResultTilesetResourceLocation = None
        self.ResultTilesetId = None
        self.ResultConvertDiagnosticLocation = None

# ============== UPLOAD FUNCTIONS ================

def upload_dwg(pipeline, filepath):
    upload_url = pipeline.base_url + "mapData/upload?api-version=1.0&dataFormat=zip&subscription-key=" + pipeline.subcriptionKey
    data = open(filepath, 'rb').read()
    response = requests.post(url= upload_url ,
                        data=data,
                        headers={'Content-Type': 'application/octet-stream'})
    
    if response.status_code == 202:
        pipeline.ResultUploadOperationsLocation = response.headers["Location"].replace("atlas.", "us.atlas.")
        print("DWG Upload accepted.")
    else:
        print("Upload failed with status code: ", response.status_code)
        exit()

    return pipeline

def get_upload_status(pipeline):
    response = requests.get(pipeline.ResultUploadOperationsLocation + "&subscription-key=" + pipeline.subcriptionKey)
    response_json = response.json()

    if response_json["status"] == "Succeeded":
        pipeline.ResultUploadResourceLocation = response_json["resourceLocation"].replace("atlas.", "us.atlas.")
        print("DWG upload successful.")
    elif response_json["status"] == "Failed":
        print("DWG Upload process failed.")
        exit()
    else:
        time.sleep(1)
        get_upload_status(pipeline)
    return pipeline


def get_udid(pipeline):
    response = requests.get(pipeline.ResultUploadResourceLocation + "&subscription-key=" + pipeline.subcriptionKey)
    response_json = response.json()

    pipeline.ResultUploadUDID = response_json["udid"]
    print("UDID obtained.")

    return pipeline


# ============== CONVERSION FUNCTIONS ================

def convert_dwg(pipeline):
    convert_url = pipeline.base_url + "conversion/convert?subscription-key=" + pipeline.subcriptionKey + "&api-version=1.0&udid=" + pipeline.ResultUploadUDID + "&inputType=DWG" 
    response = requests.post(url = convert_url ,
                        data={})
    
    if response.status_code == 202:
        pipeline.ResultConvertOperationsLocation = response.headers["Location"].replace("atlas.", "us.atlas.")
        print("DWG Conversion started...")
    else:
        print("Request to convert failed with status code: ", response.status_code)
        exit()

    return pipeline

def get_conversion_status(pipeline):
    response = requests.get(pipeline.ResultConvertOperationsLocation + "&subscription-key=" + pipeline.subcriptionKey)
    response_json = response.json()

    if response_json["status"] == "Succeeded":
        pipeline.ResultConvertResourceLocation = response_json["resourceLocation"].replace("atlas.", "us.atlas.")
        pipeline.ResultConvertId = response_json["resourceLocation"].replace("https://atlas.microsoft.com/conversion/", "").replace("?api-version=1.0", "")
        
        if "warning" in response_json:
            pipeline.ResultConvertDiagnosticLocation = response_json["properties"]["diagnosticPackageLocation"].replace("https://atlas.microsoft.com/conversion/", "") + "&subscription-key=" + pipeline.subcriptionKey
            with open('ConversionWarnings.json', 'w') as fp:
                json.dump(response_json["warning"], fp)
            print("DWG conversion successful with warnings! Find warnings in 'ConversionWarnings.json'")

            diagnosticText = """
                // Copy the link below and paste it into the browser to download the Diagnosis of your converion 
                // Once downloaded, unzip the file. It contains a 'ConversionWarningsAndErrors.json' file and a 'VisualizationTool.zip' file 
                // Unzip the Visualization tool and open the 'index.html' contained in it in the browser. 
                // Then drag and drop the 'ConversionWarningsAndErrors.json' into the file upload section of the web page in the browser 
                ==============================================
                ###
            """.replace("###", pipeline.ResultConvertDiagnosticLocation)

            with open("ConversionDiagnosis.txt", "w") as fp:
                fp.write(diagnosticText)
            print("Open 'ConversionDiagnosis.txt' on instructions to visualize the warnings")
        else:
            print("DWG conversion successful.")

    elif response_json["status"] == "Failed":
        print("DWG conversion process failed.")
        exit()

    else:
        time.sleep(1)
        get_conversion_status(pipeline)
    return pipeline



# ============== DATASET FUNCTIONS ================

def generate_dataset(pipeline):
    url = pipeline.base_url + "dataset/create?subscription-key=" + pipeline.subcriptionKey + "&api-version=1.0&conversionId=" + pipeline.ResultConvertId + "&type=facility" 
    response = requests.post(url = url ,
                        data={})
    
    if response.status_code == 202:
        pipeline.ResultDatasetOperationsLocation = response.headers["Location"].replace("atlas.", "us.atlas.")
        print("Dataset generation started...")
    else:
        print("Request to generate dataset failed with status code: ", response.status_code)
        exit()

    return pipeline

def get_dataset_status(pipeline):
    response = requests.get(pipeline.ResultDatasetOperationsLocation + "&subscription-key=" + pipeline.subcriptionKey)
    response_json = response.json()

    if response_json["status"] == "Succeeded":
        pipeline.ResultDatasetResourceLocation = response_json["resourceLocation"].replace("atlas.", "us.atlas.")
        pipeline.ResultDatasetId = response_json["resourceLocation"].replace("https://atlas.microsoft.com/dataset/", "").replace("?api-version=1.0", "")
        print("Dataset generated successfully.")
    elif response_json["status"] == "Failed":
        print("Dataset generation failed.")
        exit()

    else:
        time.sleep(1)
        get_dataset_status(pipeline)
    return pipeline



# ============== TILESET FUNCTIONS ================

def generate_tileset(pipeline):
    url = pipeline.base_url + "tileset/create/vector?subscription-key=" + pipeline.subcriptionKey + "&api-version=1.0&datasetId=" + pipeline.ResultDatasetId 
    response = requests.post(url = url ,
                        data={})
    
    if response.status_code == 202:
        pipeline.ResultTilesetOperationsLocation = response.headers["Location"].replace("atlas.", "us.atlas.")
        print("Tileset generation started...")
    else:
        print("Request to generate tileset failed with status code: ", response.status_code)
        exit()

    return pipeline

def get_tileset_status(pipeline):
    response = requests.get(pipeline.ResultTilesetOperationsLocation + "&subscription-key=" + pipeline.subcriptionKey)
    response_json = response.json()

    if response_json["status"] == "Succeeded":
        pipeline.ResultTilesetResourceLocation = response_json["resourceLocation"].replace("atlas.", "us.atlas.")
        pipeline.ResultTilesetId = response_json["resourceLocation"].replace("https://atlas.microsoft.com/tileset/", "").replace("?api-version=1.0", "")
        
        print("Tileset generated successfully.")
    elif response_json["status"] == "Failed":
        print("Tileset generation failed.")
        exit()

    else:
        time.sleep(1)
        get_tileset_status(pipeline)
    return pipeline


# ============== MAP DATA AND HTML FUNCTIONS ================

def save_map_data(pipeline):
    map_data = dict()

    map_data["Upload"] = { "OperationsLocations": pipeline.ResultUploadOperationsLocation,
                            "ResourceLocation": pipeline.ResultUploadResourceLocation,
                            "UDID": pipeline.ResultUploadUDID}
    
    map_data["Convert"] = { "OperationsLocations": pipeline.ResultConvertOperationsLocation,
                            "ResourceLocation": pipeline.ResultConvertResourceLocation,
                            "ConvertId": pipeline.ResultConvertId}

    map_data["Dataset"] = { "OperationsLocations": pipeline.ResultDatasetOperationsLocation,
                            "ResourceLocation": pipeline.ResultDatasetResourceLocation,
                            "DatasetId": pipeline.ResultDatasetId}

    map_data["Tileset"] = { "OperationsLocations": pipeline.ResultTilesetOperationsLocation,
                            "ResourceLocation": pipeline.ResultTilesetResourceLocation,
                            "TilesetId": pipeline.ResultTilesetId}

    with open('AzureMapData.json', 'w') as fp:
        json.dump(map_data, fp)
        print("Generated Map data saved to 'AzureMapData.json'")


def save_map_html(pipeline):
    longitude = 0
    latitude = 0

    with open(os.path.join("dataset", "manifest.json")) as manifest_file:
        manifest_data = json.load(manifest_file)
        latitude = manifest_data["georeference"]["lat"]
        longitude = manifest_data["georeference"]["lon"]


    map_text = """
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, user-scalable=no" />
    <title>Indoor Maps App</title>
    
    <link rel="stylesheet" href="https://us.atlas.microsoft.com/sdk/javascript/mapcontrol/2/atlas.min.css" type="text/css" />
    <link rel="stylesheet" href="https://us.atlas.microsoft.com/sdk/javascript/indoor/0.1/atlas-indoor.min.css" type="text/css"/>

    <script src="https://us.atlas.microsoft.com/sdk/javascript/mapcontrol/2/atlas.min.js"></script>
    <script src="https://us.atlas.microsoft.com/sdk/javascript/indoor/0.1/atlas-indoor.min.js"></script>
      
    <style>
      html,
      body {
        width: 100%;
        height: 100%;
        padding: 0;
        margin: 0;
      }

      #map-id {
        width: 100%;
        height: 100%;
      }
    </style>
  </head>

  <body>
    <div id="map-id"></div>
    <script>
      const subscriptionKey = "subscription_key";
      const tilesetId = "tileset_id";

      const map = new atlas.Map("map-id", {
        //use your facility's location
        center: [longitude, latitude],
        //or, you can use bounds: [# west, # south, # east, # north] and replace # with your Map bounds
        style: "blank",
        view: 'Auto',
        authOptions: { 
            authType: 'subscriptionKey',
            subscriptionKey: subscriptionKey
        },
        zoom: 19,
      });

      const levelControl = new atlas.control.LevelControl({
        position: "top-right",
      });

      const indoorManager = new atlas.indoor.IndoorManager(map, {
        levelControl, //level picker
        tilesetId,
      });

      if (statesetId.length > 0) {
        indoorManager.setDynamicStyling(true);
      }

      map.events.add("levelchanged", indoorManager, (eventData) => {
        //put code that runs after a level has been changed
        console.log("The level has changed:", eventData);
      });

      map.events.add("facilitychanged", indoorManager, (eventData) => {
        //put code that runs after a facility has been changed
        console.log("The facility has changed:", eventData);
      });
    </script>
  </body>
</html>
    """.replace("tileset_id", pipeline.ResultTilesetId).replace("subscription_key", pipeline.subcriptionKey).replace("longitude", str(longitude)).replace("latitude", str(latitude))
    with open('Map.html', 'w') as fp:
        fp.write(map_text)
        print("Generated Map saved to 'Map.html'")


def unzip_dataset(zip_file_path):
    with ZipFile(zip_file_path, 'r') as zipObj:
        zipObj.extractall('dataset')



def main():
    pipeline = MapsPipeline(subcriptionKey= args["subscriptionKey"])

    print("Reading zip file...")
    unzip_dataset(args["zipFile"])

    print("Uploading DWG Zip file...")
    pipeline = upload_dwg(pipeline, args["zipFile"])
    
    print("Checking upload status...")
    pipeline = get_upload_status(pipeline)

    print("Obtaining UDID...")
    pipeline = get_udid(pipeline)

    print("Converting DWG...")
    pipeline = convert_dwg(pipeline)

    pipeline = get_conversion_status(pipeline)

    pipeline = generate_dataset(pipeline)
    
    pipeline = get_dataset_status(pipeline)

    pipeline = generate_tileset(pipeline)

    pipeline = get_tileset_status(pipeline)

    save_map_data(pipeline)
    save_map_html(pipeline)

if __name__ == "__main__":
    main()
