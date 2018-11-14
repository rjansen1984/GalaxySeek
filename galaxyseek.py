import json
import subprocess
import sys
import time

from subprocess import call
from bioblend.galaxy import GalaxyInstance

url = sys.argv[3]  # URL of the Galaxy instance
key = sys.argv[4]  # Galaxy API key


def get_input_data():
    """Get input data based on the selected history.
    Find the number of uploaded files and return the id's of the files.

    Arguments:
        galaxyemail: The Galaxy email address.
        galaxypass: The Galaxy password.
        server: The Galaxy server URL.

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
    hist = gi.histories.show_history(historyid)
    state = hist['state_ids']
    dump = json.dumps(state)
    status = json.loads(dump)
    # Stop process after workflow is done
    while (
            status['running'] or
            status['queued'] or
            status['new'] or
            status['upload']
    ):
        time.sleep(10)
        hist = gi.histories.show_history(historyid)
        state = hist['state_ids']
        dump = json.dumps(state)
        status = json.loads(dump)
        if (
                not status['running'] and
                not status['queued'] and
                not status['new'] and
                not status['upload']
        ):
            gi.workflows.run_workflow(
                workflowid, datamap, history_id=historyid)


def get_history_id(url, key):
    """Get the current Galaxy history ID

    Arguments:
        email: The Galaxy email address.
        password: The Galaxy password.
        url: The Galaxy server URL.

    Returns:
        The current Galaxy history ID from the logged in user.
    """
    gi = get_galaxy_instance(url, key)
    cur_hist = gi.histories.get_current_history()
    current = json.dumps(cur_hist)
    current_hist = json.loads(current)
    history_id = current_hist['id']
    return history_id


def send_data_files(assayname, file):
    """Create a new history with the assay name and 
    send the data files to the Galaxy server.

    Arguments:
        file: List of files to send to Galaxy.
        historyid: The history to send the files to.
    """
    file = file.split(',')
    gi = get_galaxy_instance(url, key)
    new_hist_name = assayname
    gi.histories.create_history(name=new_hist_name)
    historyid = get_history_id(url, key)
    for f in file:
        gi.tools.upload_file(f, historyid)


def get_galaxy_instance(url, key):
    """Create a new Galaxy instance.

    Arguments:
        url: The Galaxy URL.
        email: Email address used on the Galaxy server.
        password: Password used on the Galaxy server.

    Returns:
        The Galaxy instance.
    """
    gi = GalaxyInstance(
        key=key,
        url=url)
    return gi


if __name__ == "__main__":
    gi = get_galaxy_instance(url, key)
    file = sys.argv[1]  # List with data files to send to Galaxy.
    assayname = str(sys.argv[2])
    send_data_files(assayname, file)
    historyid = get_history_id(url, key)
    workflows = gi.workflows.get_workflows(name="TestCase_AML")
    print(workflows)
    for workflow in workflows:
        workflowid = workflow['id']
    run_galaxy_workflow(historyid, workflowid, gi)
