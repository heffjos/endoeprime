import os
import re
import glob
from collections import namedtuple

ParRuns = namedtuple('ParRuns', ['Name', 'Runs'])

def ListParticipants(MasterDir):
    Contents = os.listdir(MasterDir)
    Participants = [x for x in Contents if re.match('abs13(ins|end)[0-9]+_[0-9]+', x)]
    Participants.sort()
    return(Participants)

def ListTaskRuns(MasterDir, Participant, Task):
    if Task == "emotion" or Task == "verbal":
        Expected = ["run_01", "run_02", "run_03", "run_04"]
    else:
        Expected = ["run_01", "run_02", "run_03"]
   
    RunNums = []
    Runs = glob.glob(os.path.join(MasterDir, Participant, 'func', Task, 'run*'))
    Runs = [os.path.basename(x) for x in Runs]
    for Idx, Run in enumerate(Expected):
        if Run in Runs:
            RunNums.append(Idx+1)
        else:
            RunNums.append("NA")
    return(RunNums)

def PrintRuns(Participants, Task, OutFile):
    with open(OutFile, 'w') as Out:
        for OnePar in Participants:
            print("{},".format(OnePar.Name), file=Out, end='')
            NumRuns = len(OnePar.Runs)
            print(" [", file=Out, end='')
            for RunIdx in range(NumRuns-1):
                print("{} ".format(OnePar.Runs[RunIdx]), file=Out, end='')
            print("{}]\n".format(OnePar.Runs[NumRuns-1]), file=Out, end='')

if __name__ == "__main__":
    Tasks = ["emotion", "visual", "verbal"]
    MasterDir = "/nfs/turbo/berent-lab/metabolic/Endopoid/Data/"

    Emotion = []
    for OnePar in ListParticipants(MasterDir):
        Emotion.append(
            ParRuns(OnePar, ListTaskRuns(MasterDir, OnePar, 'emotion'))
        )
    PrintRuns(Emotion, 'emotion', 'AvailableRuns/Emotion.csv')
   
    Visual = []
    for OnePar in ListParticipants(MasterDir):
        Visual.append(
            ParRuns(OnePar, ListTaskRuns(MasterDir, OnePar, 'visual'))
        ) 
    PrintRuns(Visual, 'visual', 'AvailableRuns/Visual.csv')

    Verbal = []
    for OnePar in ListParticipants(MasterDir):
        Verbal.append(
            ParRuns(OnePar, ListTaskRuns(MasterDir, OnePar, 'verbal'))
        )
    PrintRuns(Verbal, 'verbal', 'AvailableRuns/Verbal.csv')

    

    

    
    
        
