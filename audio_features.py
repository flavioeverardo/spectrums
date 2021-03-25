#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base code implemented by Ajin Tom to read wav files and calculate the average spectrum.
Taken from https://github.com/ajintom/auto-spatial/blob/master/final/my_algo-Ajin%E2%80%99s%20MacBook%20Pro.ipynb

ERB implementation and modification to use with Answer Set Programming (ASP) by Flavio Everardo
flavio.everardo@cs.uni-potsdam.de
"""

## Imports
import numpy as np
from librosa import load, stft, magphase
import erb as erb
from math import ceil, log, sqrt
import os
import matplotlib
from sys import platform
if platform == "linux" or platform == "linux2":
    # Linux
    matplotlib.use('agg')
elif platform == "darwin":
    # OS X
    matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


"""
Load wav file and get spectral information
"""
def get_spectrum(track_name, sr, N, M, H):
    W  = np.hanning(M) # Window Type
    ## Load WAV File
    track,sr = load(track_name+'.wav', sr = sr, mono = 'False')
    ## Perform Short Term Fourier Transform
    stft_ = stft(y = track, n_fft = N,win_length=M, hop_length=H, window = 'hann')
    ## Magnitudes (excluding phase)
    magnitude, _ = magphase(stft_)
    magnitude = magnitude / np.sum(W) #normalising STFT output
    ## Spectrum Average
    spec_avg = np.average(magnitude,axis=1) 
    spec_avg = spec_avg/np.max(spec_avg)
    len_signal = spec_avg.shape[0] # filter bank length

    return spec_avg, len_signal

"""
Build ERB bands wrt the spectral information
"""
def get_erb_bands(spec_avg, len_signal, sr, B, low_lim, high_lim):
    # Equivalent Rectangular Bandwidth
    # Create an instance of the ERB filter bank class
    erb_bank = erb.EquivalentRectangularBandwidth(len_signal, sr, B, low_lim, high_lim)
    
    # Get ERB Bands and convert them to integer
    erb_bands = erb_bank.erb_bands
    erb_bands = list(map(int, erb_bands))

    # Get frequencies indexes
    freqs_index = erb_bank.freq_index
    # Get range of frequencies
    freqs = erb_bank.freqs.tolist()
    # Get frequency bandwidths
    bandwidths = erb_bank.bandwidths
    # Get center frequencies
    center_freqs = erb_bank.center_freqs
    # Get the filters
    filters = erb_bank.filters

    # Get amplitudes wrt the ERB/Center Freq
    erb_amp = []
    for i in range(len(freqs_index)):
        erb_amp.append(spec_avg[freqs_index[i]])

    ## Normalize ERBs amplitude
    max_erb_amp = max(erb_amp)
    erb_amp = erb_amp/max_erb_amp

    return erb_amp, bandwidths, freqs, center_freqs, filters

"""
Plot and save graphics
"""
def build_graphics(freqs, spec_avg, project_path, project_name, erbs, B, filters, tracks, show_plot):
    
    ## Plot
    plt.figure(figsize=(12,7))
#    plt.subplot(311)
#    plt.grid(True)
#    plt.plot(freqs,filters[:, 1:-1])
#    plt.title("%s Auditory filters"%B)
#    plt.xlabel('Frequencies (Hz)')
#    plt.ylabel('Power Ratio [0-1]')

    plt.subplot(2,1,1)
    plt.grid(True)
    for i in range(len(spec_avg)):
        plt.plot(freqs,spec_avg[i], label=tracks[i])
    plt.title(project_name+" Spectrums (Normalized)")
    plt.xlabel('Frequency')
    plt.xlim(xmin=20)
    plt.ylabel('Linear Amplitude [0-1]')
    plt.xscale('log')
    plt.legend()
    
    plt.subplot(2,1,2)
    plt.grid(True)
    for i in range(len(erbs)):
        erbs[i] = np.insert(erbs[i], 0, 0)
        plt.plot(erbs[i], label=tracks[i])
    plt.title(project_name+" ERB Scale (Normalized)")
    plt.xlabel('ERB Numbers (1-%s)'%B)
    plt.ylabel('Linear Amplitude [0-1]')
    plt.legend()
    
    plt.tight_layout()

    plt.subplots_adjust(wspace=2.5)
    plt.savefig('%s/%s.png'%(project_path, project_name))
    if show_plot:
        plt.show()
