import os
import json
import subprocess
import sys
import time

from subprocess import call
from bioblend.galaxy import GalaxyInstance

files = sys.argv[1]  # List with data files to send to Galaxy.
assayname = sys.argv[2] # Name of the assay (used for Galaxy history).
url = sys.argv[3]  # URL of the Galaxy instance.
key = sys.argv[4]  # Galaxy API key.
filenames = sys.argv[5] # List of original filenames.
workflowid = sys.argv[6] # Name of the workflow to run.

def get_input_data():
    """Get input data based on the selected history.
    Find the number of uploaded files and return the id's of the files.

    Returns:
        A list of input files from the Galaxy history and
        the amount of input datasets in the history.
    """
    gi = get_galaxy_instance(url, key)
    historyid = get_history_id(url, key)
    hist_contents = gi.histories.show_history(historyid, contents=True)
    inputs = {}
    datasets = [dataset for dataset in hist_contents if not dataset['deleted']]
    for dataset in datasets:
        inputs[dataset['name']] = dataset['id']
    return inputs


def run_galaxy_workflow(historyid, workflowid, gi):
    """Run a Galaxy workflow.
    
    Arguments:
        historyid: Galaxy history id with the input data files.
        workflowid: The id of the Galaxy workflow.
        gi: The Galaxy instance.
    """
    datamap = dict()
    mydict = {}
    jsonwf = gi.workflows.export_workflow_json(workflowid)
    for i in range(len(jsonwf["steps"])):
        if jsonwf["steps"][str(i)]["name"] == "Input dataset":
            try:
                label = jsonwf["steps"][str(i)]["inputs"][0]["name"]
            except IndexError:
                label = jsonwf["steps"][str(i)]["label"]
            mydict[label] = gi.workflows.get_workflow_inputs(
                workflowid, label=label)[0]
    for k, v in mydict.items():
        datasets = get_input_data()
        for dname, did in datasets.items():
            if k in dname:
                datamap[v] = {'src': "hda", 'id': did}
    gi.workflows.run_workflow(
        workflowid, datamap, history_id=historyid)


def get_history_id(url, key):
    """Get the current Galaxy history ID

    Arguments:
        url: The Galaxy server URL.
        key: The Galaxy API key.

    Returns:
        The current Galaxy history ID from the logged in user.
    """
    gi = get_galaxy_instance(url, key)
    cur_hist = gi.histories.get_current_history()
    current = json.dumps(cur_hist)
    current_hist = json.loads(current)
    historyid = current_hist['id']
    return historyid


def send_data_files():
    """Create a new history with the SEEK assay name and 
    send the data files to the Galaxy server.
    """
    filelist = files.split(',')
    filenamelist = filenames.split(',')
    pathname = os.path.dirname(sys.argv[0])
    gi = get_galaxy_instance(url, key)
    new_hist_name = assayname
    gi.histories.create_history(name=new_hist_name)
    historyid = get_history_id(url, key)
    for nr in range(len(filelist)):
        newfile = os.path.abspath(pathname) + "/filestore/tmp/" + filenamelist[nr]
        call(["cp " + filelist[nr] + " " + newfile], shell=True)
        gi.tools.upload_file(newfile, historyid)
        call(["rm " + newfile], shell=True)


def get_galaxy_instance(url, key):
    """Create a new Galaxy instance.

    Arguments:
        url: The Galaxy URL.
        key: The Galaxy API key.

    Returns:
        The Galaxy instance.
    """
    gi = GalaxyInstance(
        key=key,
        url=url)
    return gi


if __name__ == "__main__":
    gi = get_galaxy_instance(url, key)
    send_data_files()
    historyid = get_history_id(url, key)
    get_input_data()
    run_galaxy_workflow(historyid, workflowid, gi)
