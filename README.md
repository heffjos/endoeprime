# endoeprime
This repository contains a collection of scripts for parsing/summarizing endopoid eprime task files. Here is a description of the most useful scripts:

### CreateMasterDataFile.R
* Creates task master data files using all available participant folders in data location. Using all folder names is not a problem, because only those listed in the master data file will be processed.
* Emotion - (Neutral:1, Negative:2)
* Verbal - (AC:1, UL:2)
* Vsiual - (Match:1, Delay1:2, Delay4:3)

### CreateSummaries.R
* Summarizes task data from the eprime files at the participant and run level.
* Incomplete participants are filtered out before summary.

### ListEndopoidFiles.py
* Lists all available participants and task runs availbe in data location (Endopoid/Data).
* Prints output into Available runs as input into master data file.

### ParseEprime.bash
* Does *not* edit original eprime files.
* Converts task (Emotional, VerbalMemA, VerbalMemB, VisualMem) eprime files created on a Windows environment from unicode to utf-8.
* Puts converted files in _./ConvertedEprime/[Partcipant]/[Task]_.
* Participant number is stripped from eprime file. Participant output directory is number with at least 5 leading digits and I.
* Does not overwrite already converted eprime files.
* Corrects mislabeled trial 20 in VerbalMemA from 1 to l.
* Corrects mislabeled participant 11 from wrong label of 9 in the eprime file itself.
* Parse eprime files to csv. The important parsed information is trial type, reaction time, and accuracy.
* Saves csv files into same directory as converted eprime files. All runs are put into one csv file.

### TaskTemplates.csv
* Holds the onsets and durations for each task of all runs. These are identical across all participants.





