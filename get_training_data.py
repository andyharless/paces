from pace_params import *

import numpy as np
import pandas as pd
import pickle
import gzip
import math
import random


with open(LABEL_FILE_PATH, 'rb') as fp:
    song_dict = pickle.load(fp)
songs = list(song_dict.keys())
nsongs = len(songs)

ntrain = int(TRAIN_FRACTION*nsongs)


def choose_song(validation=False):
    if validation:
        song = songs[random.randint(ntrain, nsongs-1)]
    else:
        song = songs[random.randint(0, ntrain-1)]
    return(song)


def choose_tempo(song):
    tempo, compatible = random.sample(song_dict[song], 1)[0]
    tempo = min(tempo, 320)
    return(tempo, compatible)


def get_cliplen( beats_per_minute ):
    nbeats = NBEATS
    samples_per_second = 22050
    seconds_per_minute = 60
    samples_per_hop = 256
    beats_per_second = beats_per_minute / seconds_per_minute
    hops_per_second = samples_per_second / samples_per_hop
    hops_per_beat = hops_per_second / beats_per_second
    return(nbeats*int(hops_per_beat))


def choose_clip(song, tempo):
    cliplen = get_cliplen(tempo)
    melspec_path = MELSPEC_BASEPATH + song + '_melspec.pkl.gz'
    with gzip.open(melspec_path,'rb') as fp:
        ms = pickle.load(fp)
    clip_start = random.randint(0, ms.shape[1]-cliplen-1)
    clip = ms[:,clip_start:clip_start+cliplen]
    return(clip)


def get_training_case():
    song = choose_song()
    tempo, compatible = choose_tempo(song)
    raw_clip = choose_clip(song, tempo)
    return(song, tempo, compatible, raw_clip)


def get_validation_case():
    song = choose_song(validation=True)
    tempo, compatible = choose_tempo(song)
    raw_clip = choose_clip(song, tempo)
    return(song, tempo, compatible, raw_clip)


def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


def resample_clip(raw_clip):  # Resample clip so time dimension has length NBEATS*INPUTS_PER_BEAT

    initial_length = raw_clip.shape[1]
    final_length = NBEATS*INPUTS_PER_BEAT

    # Will first upsample to common multiple of lengths, then downsample to final length
    maximum_length = lcm(initial_length, final_length)
    
    # Normalize time scale to make each observation at maximum_length equal one (pseudo-)second
    ticks_per_pseudo_second = 10**9  # conversion factor from integer to pandas seconds
    max_time = maximum_length*ticks_per_pseudo_second
    clip_time = pd.to_datetime(np.arange(0, max_time, max_time/initial_length))
    
    # Convert data to pandas time series
    df = pd.DataFrame(raw_clip.transpose(), index=clip_time)
    
    # Frequency corresponding to output length, given time normalizatoin
    outfreq = str(int(maximum_length/final_length))+'S'
    
    # Upsample, then downsample
    df = df.resample('S').interpolate().resample(outfreq).mean()
    
    # Convert back to numpy format
    clip = df.values.transpose()

    return(clip)


def clip_to_tf_input(clip):  # Convert resampled clip to channels-last CNN input format
    return(clip.transpose().reshape(INPUTS_PER_BEAT, NBEATS, NCHANNELS))
