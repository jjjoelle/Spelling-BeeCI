from preprocessing import filter_eeg
from classify import * 
import pandas as pd
from scipy.signal import periodogram
col_names = ['Fp1', 'O1', 'O2','C3','C4','P3','P4','Pz']
freqs = np.arange(8.4,16,0.8)

def classify_freq(samp_list):
    eeg = sample_to_df(samp_list)
    filt = filter_eeg(eeg, Fs=250, low=6, high=32)
    O1 = list(filt['O1'])
    f, Pxx = periodogram(O1,250)
    df = f[1]-f[0]
    fv = calc_featvec(Pxx, df, freqs, band_width=0.4, num_harmonics=2)
    pred = pick_freq(fv,freqs)
    return pred
    
def sample_to_df(samp_list):
    samp_arr = np.array(samp_list)
    data = pd.DataFrame()
    for i,chan in enumerate(col_names):
        data[chan] = samp_arr[:,i]
    return data