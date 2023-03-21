import numpy as np

def calc_featvec(ps, df, freqs, band_width=0.4, num_harmonics=1):
    featvec = [0]*len(freqs)
    for i,f in enumerate(freqs):
        for h in np.arange(num_harmonics)+1:
            f_low = f*h - band_width
            f_high = f*h + band_width
            f_low_idx = int(f_low / df)
            f_high_idx = int(f_high / df)
            f_band = ps[f_low_idx: f_high_idx]
            featvec[i] += np.mean(f_band)
    return featvec

def pick_freq(featvec, freqs):
    max_ind = np.argmax(featvec)
    return freqs[max_ind]