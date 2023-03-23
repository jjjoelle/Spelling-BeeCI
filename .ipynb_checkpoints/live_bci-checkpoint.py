from preprocessing import filter_eeg, power_spectrum
from classify import * 
import pandas as pd
from scipy.signal import periodogram
col_names = ['Fp1', 'O1', 'O2','C3','C4','P3','P4','Pz']
freqs = np.arange(8.4,16,0.8)

def classify_freq(samp_list,vote=True):
    eeg = sample_to_df(samp_list)
    filt = filter_eeg(eeg, Fs=250, low=6, high=32)
    #O1 = list(filt['O1'])
    #f, Pxx = periodogram(O1,250)
    #df = f[1]-f[0]
    power = power_spectrum(filt,250)
    flist = list(power['freqs'])
    df = flist[1]-flist[0]
    pred_list = []
    for chan in ['O1','O2','Pz']:
        chan_power = list(power[chan])
        fv = calc_featvec(chan_power, df, freqs, band_width=0.4, num_harmonics=2)
        pred = pick_freq(fv,freqs)
        pred_list.append(round(pred,1))
    if vote:
        return sorted(pred_list)[1]
    else:
        return pred_list[0]
    
def sample_to_df(samp_list):
    samp_arr = np.array(samp_list)
    data = pd.DataFrame()
    for i,chan in enumerate(col_names):
        data[chan] = samp_arr[:,i]
    return data