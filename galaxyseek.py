import json
import subprocess
import sys

from subprocess import call
from bioblend.galaxy import GalaxyInstance

url = input("Ënter the Galaxy server URL: ")  # URL of the Galaxy instance
key = input("Enter Galaxy API key: ") # Galaxy API key


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
    gi = get_galaxy_instance(url, key)
    new_hist_name = assayname
    gi.histories.create_history(name=new_hist_name)
    historyid = get_history_id(url, key)
    gi.tools.upload_file(file, historyid)


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
    file = sys.argv[1] # List with data files to send to Galaxy.
    assayname = str(sys.argv[2])
    send_data_files(assayname, file)
