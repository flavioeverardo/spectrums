"""
Display differences between spectrums
"""

# Imports
import sys
import argparse
import textwrap
import random
import datetime
import os
import contextlib
import audio_features as af

""" 
Parse Arguments 
"""
def parse_params():
    parser = argparse.ArgumentParser(prog='spectrums-diff.py',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
Tool for displaying differences between audio spectrums.
Default command-line: python spectrums_diff.py --project="695mixes" --samples=32768 --erb=40
                                     '''),

                                     epilog=textwrap.dedent('''\
Get help/report bugs via : flavio.everardo@cs.uni-potsdam.de
                                     '''),)

    ## Input related to uniform solving and sampling
    basic_args = parser.add_argument_group("Basic Options")

    parser.add_argument("--project", type=str, default="695mixes",
                        help="Name of the project where all the stems are stored.")
    parser.add_argument("--samples", type=int, default=32768,
                        help="FFT size or number of samples (1000-32768). Default: 32768.")
    parser.add_argument("--erb", type=int, default=43,
                        help="Number of ERB bands (10-100). Default: 43.")
    parser.add_argument("--file", type=str, default="spectrums",
                        help="Name of the spectrums graph.")

    return parser.parse_args()


"""
Checks consistency wrt. related command line args.
"""
def check_input(arguments):
    
    ## Check for errors
    if arguments.project == "":
        raise ValueError("""A project name must be given.""")
    if arguments.samples < 1000 or arguments.samples > 32768:
        raise ValueError("""Number of samples requested is out of bounds""")
    if arguments.erb < 10 or arguments.erb > 100:
        raise ValueError("""Number of erb bands requested is out of bounds""")
        
""" 
Main function
Extract audio features, parse to ERB and plot
"""
def main():

    ## Parse input data
    args = parse_params()
    ## Check for input errors
    check_input(args)

    # Input data
    ## STFT parameters
    sr = 44100.0       # Sample Rate
    N  = args.samples  # FFT size or Number of Samples
    M  = N             # Window size 
    H  = int(M/64)     # Hop size
    B  = args.erb      # ERB Bands
    low_lim = 20       # centre freq. of lowest filter
    high_lim = sr / 2  # centre freq. of highest filter
    fileName = args.file
    
    ## ASP variables
    project = args.project #project name
    models = [] # answer sets
    tracks = []
    tracks_duration = []

    ## Read wav files from project
    for fl in os.listdir("projects/%s/"%project):
        if fl.endswith(".wav"):
            tracks.append(os.path.splitext(fl)[0])

    ## for each track
    frequencies = []
    spectrums = []
    erbs = []
    filters = []
    for track in tracks:
        print("Analyzing track: %s"%track)
        ## Get spectrum and signal size
        spectrum, len_signal = af.get_spectrum("projects/%s/%s"%(project,track), sr, N, M, H)

        # Equivalent Rectangular Bandwidth
        erb_bands, bandwidths, frequencies, center_fr, filters = af.get_erb_bands(spectrum, len_signal, sr, B, low_lim, high_lim)

        # Save data for plotting
        spectrums.append(spectrum)
        erbs.append(erb_bands)

    # Build mixdown graphics
    af.build_graphics(frequencies, spectrums, "projects/%s"%(project), fileName, erbs, B, filters, tracks, True)

"""
Main function
"""
if __name__ == '__main__':
    sys.exit(main())					      
