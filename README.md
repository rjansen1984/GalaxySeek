# GalaxySeek
Sends data files from a SEEK assay to a Galaxy server. The SEEK user will login to the SEEK server and goes to the assay where the data files are located. Click on the Run with Galaxy button to start sending the data files to Galaxy and start the workflow.

The filenames in the SEEK filestore will be copied to the temp folder and be renamed to the original filename. Please make sure that the labels in the Galaxy workflow are labeled correctly, the script will attach a data file to the input with a label with the same name as the data file or with the same extention.

## Dependencies
* Python 3.6 or higher
* Bioblend 0.11.0 or higher
* SEEK account
* Galaxy account

### Install dependencies
```bash
sudo apt install python3-pip
pip3 install bioblend
```

## SEEK
To use this script, please add the script to the SEEK project and pass the correct arguments to the script.

The following arguments are needed:
* Filepaths (comma seperated)
* A history name (assay name will be used by default)
* Galaxy server URL
* A Galaxy API key
* Original filenames (comma seperated)
* A Galaxy workflow id

## Galaxy
Make sure you have a Galaxy account and have the URL, API key and workflow id you want to use. Add this information to assay_controllers.rb

In future updates this should be an automatic procedure or the user should get the option to add this information from the assay page.

## How to run outside of SEEK
Create a filestore folder with a tmp folder in the same location as the Python script and enter the following command.
```bash
python3 galaxyseek.py file1,file2,file3 a-new-history-name GalaxyURL API-key originalname1,originalname2,originalname3 workflowid
```
