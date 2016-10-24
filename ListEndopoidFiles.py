import os
import re
import glob

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
   
    ParRuns = glob.glob(os.path.join(MasterDir, Participant, 'func', Task))
    ParRuns = [os.path.basename(x) for x in Runs]
    for Run, Idx in enumerate(Expected):
        if Run in ParRuns:
            RunNums.append(Idx)
        else:
            RunNums.append("NA")
    return(RunNums)

def PrintRuns(Participants, Task, OutFile):
    with open(OutFile, 'w') as Out:
        for OnePar in Participants:
            print("{},".format(OnePar[0]), file=Out)
            for RunIdx in range(len(OnePar[1])-1):
                print("{},".format(OnePar[1][RunIdx]))
            print("{}\n".format(OnePar[1][len(OnePar[1])-1))

if __name__ == "__main_":
    Tasks = ["emotion", "visual", "verbal"]
    MasterDir = "/nfs/turbo/berent-lab/metabolic/Endopoid/Data/"

    Emotion = ([], [])
    Visual = ([], [])
    Verbal = ([], [])

    Emotion[0].extend(ListParticipants(MasterDir))
    for OnePar in Emotion[0]:
        Emotion[1].append(ListTaskRuns(MasterDir, OnePar, 'emotion'))
    PrintRuns(Emotion, 'emotion', 'AvailableRuns/Emotion.csv')
    
    Visual[0].extend(ListParticipants(MasterDir))
    for OnePar in Visual[0]:
        Visual[1].append(ListTaskRuns(MasterDir, OnePar, 'visual'))
    PrintRuns(Visual, 'visual', 'AvailableRuns/Visual.csv')

    Verbal[0].extend(ListParticipants(MasterDir))
    for OnePar in Verbal[0]:
        Verbal[1].append(ListTaskRuns(MasterDir, OnePar, 'verbal'))
    PrintRuns(Verbal, 'verbal', 'AvailableRuns/Verbal.csv')

    

    

    
    
        
