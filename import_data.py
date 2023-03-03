import numpy as np
import pandas as pd

def read_file(file_name, col_names):
    eeg = pd.read_csv(file_name,header=None)
    eeg.columns = col_names
    return eeg

def read_openbci_file(file_path):
    """
    Reads an OpenBCI data file and returns a pandas DataFrame containing the EEG data.

    The OpenBCI data file should have the following format:
    - The first four lines should be ignored
    - The fifth line should contain a comma-separated list of electrode names
    - The sixth and onwards lines should contain the EEG data, with each row representing a sample time point
      and each column representing the EEG data from one electrode.

    Args:
        file_path (str): The path and filename of the OpenBCI data file.

    Returns:
        data (pandas.DataFrame): A pandas DataFrame containing the EEG data.
    """
    with open(file_path, 'r') as f:
        f.readline()
        num_channels = int(f.readline().split('=')[1].strip())
        Fs = f.readline().split('=')[1].strip()
        Fs = int(Fs.split()[0])
        f.readline()
        all_names = f.readline().strip().split(',')
        column_names = all_names[:9] + [all_names[22], all_names[24]]

    # Read the EEG data into a pandas DataFrame
    usecols = [0,1,2,3,4,5,6,7,8,22,24]
    data = pd.read_csv(file_path, header=None, skiprows=5, usecols=usecols, names=column_names)

    return data, num_channels, Fs, column_names