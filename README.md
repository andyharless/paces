# paces

## The Problem

A project to estimate multiple musical tempos from an audio segment. For example, a song marked at ♩=160, in 4/4 time with secondary stress on beat 3 and a lot of ♫, could be timed as 40, 80, 160, or 320 bpm depending how you define a beat, and depending on the particular sound of the song, which may or may not lend itself to any or all of these timings.

Beat detection and tempo estimation are standard problems, for which (imperfect) solutions exist. But one thing I've found trying to jog to music is that a single tempo estimate (even if it's accurate) doesn't necessarily solve the relevant problem.  For example, if a song has ♩=105 but has a lot of 8th notes, you can jog with very quick steps (210 per minute) or with very slow steps (105). And a song compatible with a normal jogging pace (say 160) may not be recognizable as such from a single tempo estimate (e.g. maybe 80).

The problem is complicated by the fact that, while most songs have an even time signature (2 or 4), many have odd (usually 3), and some have both even and odd factors (6 or 12). So the relation of the official tempo to the possible alternatives differs from song to song.

I'm referring to this problem as the "pace compatibility" problem, or sometimes the "multiple tempo estimation" problem, because I don't know what it's supposed to be called or whether it even has a name or if anyone else has even thought to work on it.

## The Approach

1. Choose a set of songs with roughly constant tempos (except possibly at the beginning and the end).
2. Hand-label songs with compatible paces.  For example, The Beatles' _I'm Looking Through You_ works with either roughly 172 bpm or roughly 86 bpm. Some songs work with three different paces (Patti Smith's _Because the Night_ at 62, 123, or 246).  A few only work with one pace (Glenn Miller's _In The Mood_ at 176).  This is quite subjective, and others will disagree with many of my labels, but it's the best I've got.  (Acceptable tempos range from 40 to 320.)
3. Divide each song into segments of about 25 seconds each. Ignore the first and last segment of each song.
4. Using [LibROSA](https://librosa.github.io/librosa/), calculate a [tempogram](https://musicinformationretrieval.com/tempo_estimation.html) for each song segment, and find the peaks of the tempogram's time-averaged means.  Collect a set of all the peaks (rounded to nearest integer) from all the segments of each song.  Use these as "candidate tempos" for the song.
5. A candidate tempo is "correct" if it is within a certain tolerance (initially 5%) of one of the hand-labeled paces.  The rest are "incorrect."
6. For use in initial training data, generate the [Mel spectrogram](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum) (as a function of time, produced by LibROSA) for each song.
7. To generate each training case, 
     - choose a labeled song (at random or according to a process later to be decided), 
     - choose one of its candidate tempos (at random or...), 
     - take a random clip (with a specified length in _number of beats_ according to the candidate tempo, but without attempting to choose a phase relative to the beat) from the song (but not from the beginning or end of the song),
     - resample the spectrogram of the clip to make it a standard size,
     - reshape the spectrogram, adding a dimension, so that the time segment associated with each beat has a separate row, and
     - associate the result with the binary label as to whether the candidate tempo is correct for the song.
8. Train a binary classifier to distinguish correct and incorrect tempos.

## Notes

This repo includes the hand-labeled pace data but not most of the audio input data (because copyrights etc.).  Hopefully there is enough information for someone to reproduce the procedure using different audio data, supplying their own labels.

Terminological note: I have started using the word "megabatch" to refer to large files of cases (training, validation, or test, in separate files) ready to feed into the model.  Originally I used a data generator to generate batches on demand, but this proved too slow (since I wanted to look at model iterations in real time).  Since I'd already written the code to create batches, I just set the batch size to huge and created a file from a single "batch", which I call a "megabatch."  The generator then just samples cases from the megabatch files to create actual training batches etc..

## Files

`code/pace_params.py`: parameters used by other files   
`data/songs20190129.csv`: pace labels used for training and validation of initial ("Stage 0") model  
`code/SongsSliceDiceSetsWork2.ipynb` ([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/SongsSliceDiceSetsWork2.ipynb)): process each song into spectrogram and candidate tempos  
`code/get_training_data.py`: sample clips from songs and associate each clip with a candidate tempo  
`code/SaveMegabatch.ipynb`([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/SaveMegabatch.ipynb)): standardize clips for use as training/validation data and produce large files  
`code/BestStage0Model.ipynb`([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/BestStage0Model.ipynb)): train and validate the best model  

`code/eda.ipynb` ([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/eda.ipynb)): examine training data with an eye to preprocessing and visualization  
`data/small_sample.pkl.gz`: data sampled by eda.ipynb  
`data/medium_sample.pkl.gz`: data sampled by eda.ipynb  
`code/ModelExperiments.ipynb`([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/ModelExperiments.ipynb)): messy code to try versions of the model ("how the sausage is made")  
`code/inferential.ipynb`([jupyter view](https://nbviewer.jupyter.org/github/andyharless/paces/blob/master/code/inferential.ipynb)): some hypothesis tests  
`docs/Project proposal.pdf`: description of project (for Springboard)  
`docs/milestone.pdf` : report on initial phases of project (for Springboard)  
`docs/wrangling.pdf`: description of how data were prepared

 
## Results

Validation accuracy is about 91% for the best model so far, and it appears to be making a generally reasonable set of predictions (e.g. not heavily biased toward the modal category).  See [BestStage0Model.ipynb](BestStage0Model.ipynb).  Considering many cases are ambiguous, this is quite good performance, such as it is, but the usual caveats apply.  (The hyperparameters may have been overfit to the validation set; the validation set—different songs but some by the same artisits and in similar styles—may be too much like the training set; there may be particular types of songs with which the model has difficulty; yada, yada, yada.)  Real testing, including better performance measures, is still to come.

## What I Think Is Cool About This

- Same music can be interpreted as more than one tempo
- Data augmentation via phase sampling (same song, different data)
- Two-dimensional time
- Narrow convolutions
- Alternating batch normalization and dropout between successive convolutional layers

## Issues and Ideas

- Address class imbalance. Maybe re-create megabatch files with balanced classes and re-train.
- Procedure for incorporating new data. Maybe:
    - divide each new chunk of songs 60/20/20 for train/validate/test
    - create new megabatch files including both old and new data
    - re-train on training cases from new megabatch files
    - possibly adjust hyperparameters or network structure
    - look at test data results
    - keep notes on how much improvement comes from each data update
- Include metadata (e.g. music genre, the candidate tempo itself) in model by using branched network.
- Look at results per song. Subjectively, how does model do at getting correct paces? Are typical failures legitimately ambiguous cases, or is the model really missing something?
- Look at validation results to see if some music genres work better than others.  Do "active learning" by adding new training cases from more difficult genres.  Also time signatures.
- Balance training/validation/test data according to music genre. And artist. And time signature.
- Get more data for underrepresented genres (and time signatures). And a greater variety of artists.
- Get data from other human labelers.
- Revise model experiment code:
    - Run each model multiple times with different random seeds.
    - Generate network from lists of hyperparameters instead of manually revising network code for each experiment.
- Revise best model code:
    - Run multiple times with different random seeds, and combine results (how? mean? logit mean? median? ?).
    - Save fitted weights for future inference.
- (done) ~Add file descriptions to this readme.~
- Study how to combine models. (What works best? mean probability? logit mean? median? something else?)
- (partly done) Add analyses, descriptions, etc. to conform to Springboard requirements.
- (done) ~Add description of results to this readme.~
- Try adjusting tempo tolerance.
- Improve code documentation.
- Consider implementing [stochastic weight averaging](https://pechyonkin.me/stochastic-weight-averaging/) or a similar strategy.
- Consider using cross-validation (with a separate megabatch file for each fold) instead of holdout validation.
- Clean up code (e.g. so parameters are all in parameter file instead of some defined explicitly elsewhere)
- 3-d convolutions?
- Run with publicly available audio inputs (which need to be labeled first), so the project could be forked and run immediately by someone else.
- Try to come up with more sophisticated [preprocessing methods](https://www.linkedin.com/pulse/preprocessing-neural-network-inputs-andrew-harless)
