from enum import Enum

class EndoError(Exception):
    """Base class for exception in this module."""
    pass

class EndoParseError(EndoError):
    """Exception raised if parsing error occurs for verbal eprime files.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, Message):
        self.Message = Message

class EndoTransitionError(EndoError):
    """Raised when an operation attempts a state transistion that is not 
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        expected -- expected state
        message -- explanation of why the specific transition is not allowed
    """
    def __init__(self, LineNo, FoundStr, ExpectedStr):
        self.LineNo = LineNo
        self.FoundStr = FoundStr
        self.ExpectedStr = ExpectedStr

class VerbalMemState(Enum):
    Stim = 0
    Abst = 1
    Case = 2
    Onset = 3
    Rt = 4
    Resp = 5
    Cresp = 6
    Dur = 7
    FixOnset = 8
    RunLists = 9
    TrialNum = 10  # only used for indexing trials

class EmotionalState(Enum):
    ImageDis = 0    # str
    ImageAns = 1    # str
    ImageOnset = 2  # float
    ImageDur = 3    # float
    ImageAcc = 4    # int
    ImageRt = 5     # float
    ImageResp = 6   # int
    ImageCrep = 7   # int
    DelayOnset = 8  # float
    DelayDur = 9    # float
    

def ParseVerbalMem(FileName, Participant):
    TruePeriodDurations = (32000, 44000, 44000, 44000, 44000, 32000)

    DataText = ["myStimulus:",
        "conAbst:",
        "myCase:",
        "Probe.OnsetTime:",
        "Probe.RT:",
        "Probe.RESP:",
        "Probe.CRESP:",
        "Probe.OnsetToOnsetTime:",
        "fixation.OnsetTime:",
        "Run1Lists:"]

    Trials = [[] for _ in range(VerbalMemState.TrialNum.value + 1)]

    # read all lines
    Lines = []
    with open(FileName, 'r') as F:
        for Line in F:
            Lines.append(Line)

    # check subject is same as input
    for Line in Lines:
        if "Subject:" in Line:
            ColIdx = Line.find(':')
            FileParticipant = Line[ColIdx+1:].strip().lstrip('0')
            break
    if FileParticipant != Participant:
        raise EndoParseError(
            " * * * PARTICIPANT MISMATCH * * *\n" +
            "File Participant: {}".format(FileParticipant))

    # check for timings consistency
    PeriodDurations = []
    for Line in Lines:
        if "PeriodDuration:" in Line:
            ColIdx = Line.find(':')
            PeriodDurations.append(int(Line[ColIdx+1:].strip()))
    if PeriodDurations != list(TruePeriodDurations):
        raise EndoParseError(
            " * * * UNEXPECTED PERIOD DURATIONS * * *\n" +
            "True period durations:     {}\n".format(TruePeriodDurations) +
            "Expected period durations: {}".format(PeriodDurations))

    # find baseline time
    BaselineTime = -1
    for Line in Lines:
        if "myDisDaqs.OnsetTime" in Line:
            ColIdx = Line.find(':')
            BaselineTime = float(Line[ColIdx+1:].strip())
            break
    if BaselineTime == -1:
        raise EndoVerbelParseError(" * * * myDisDaqs.OnsetTime NOT FOUND * * *")

    # grab block lines  
    BlockLines = []
    for LineNo, Line in enumerate(Lines):
        if "Run1Lists:" in Line:
            BlockLines.append((Line, LineNo+1))
    if not BlockLines:
        raise(EndoParseError("* * * BlockLines list EMPTY * * *"))

    # grab data lines
    DataLines = []
    BlockIndex = 0
    for LineNo, Line in enumerate(Lines):
        for TextNo, OneText in enumerate(DataText):
            if OneText in Line:
                if TextNo != VerbalMemState.RunLists.value:
                    DataLines.append((Line, LineNo+1))
                else:
                    BlockIndex += 1
                if TextNo == VerbalMemState.FixOnset.value:
                    DataLines.append(BlockLines[BlockIndex])
                break

    CurState = VerbalMemState.Stim
    TrialCounter = 1
    for Pairs in DataLines:
        if CurState == VerbalMemState.Stim:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = VerbalMemState.Abst
        elif CurState == VerbalMemState.Abst:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            tmp = Pairs[0][ColLoc+1:].strip()
            if tmp == "a":
                Trials[CurState.value].append("Abstract")
            elif tmp == "c":
                Trials[CurState.value].append("Concrete")
            else:
                raise EndoParseError("* * * UNEXPECTED IDEA: {} * * *".format(tmp))
            CurState = VerbalMemState.Case
        elif CurState == VerbalMemState.Case:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            tmp = Pairs[0][ColLoc+1:].strip()
            if tmp == "l":
                Trials[CurState.value].append("Lower")
            elif tmp == "u":
                Trials[CurState.value].append("Upper")
            else:
                raise EndoParseError("* * * UNEXPECTED CASE: {} * * *".format(tmp))
            CurState = VerbalMemState.Onset
        elif CurState == VerbalMemState.Onset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VerbalMemState.Rt
        elif CurState == VerbalMemState.Rt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:].strip()) / 1000)
            CurState = VerbalMemState.Resp
        elif CurState == VerbalMemState.Resp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VerbalMemState.Cresp
        elif CurState == VerbalMemState.Cresp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VerbalMemState.Dur
        elif CurState == VerbalMemState.Dur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:].strip()) / 1000)
            CurState = VerbalMemState.FixOnset
        elif CurState == VerbalMemState.FixOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VerbalMemState.RunLists
        elif CurState == VerbalMemState.RunLists:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[VerbalMemState.RunLists.value].append(int(Pairs[0][ColLoc+1:].strip()))
            Trials[VerbalMemState.TrialNum.value].append(TrialCounter)
            TrialCounter += 1
            CurState = VerbalMemState.Stim

    if CurState != VerbalMemState.Stim:
        raise EndoParseError("Bad verbal Termination: {} {}".format(
            DataText[VerbalMemState.Stim], DataText[CurState.value]))

    return Trials

def PrintVerbalMem(OutFile, Trials, Participant):
    pass

def ParseEmotional(FileName, Participant):
    # let's assume the first trial is "baseline (time = 0)"
    # this is a reasonable guess because from Run5-037 we have
    # first onset:      30530
    # last offset:     190525
    # total duraiton:  160000
    # 190525 - 30530 = 159995
    DataText = [
        "MyImage:",
        "Answer:",
        "ImageDisplay1.OnsetTime:",
        "ImageDisplay1.Duration:",
        "ImageDisplay1.ACC:",
        "ImageDisplay1.RT:",
        "ImageDisplay1.RESP:",
        "ImageDisplay1.CRESP:",
        "ShortDelay.OnsetTime:",
        "ShortDelay.Duration"
    ]

    Trials = [[] for _ in range(EmotionalState.DelayDur + 1)]

    # read all lines
    Lines = []
    with open(FileName, 'r') as F:
        for Line in F:
            Lines.append(Line)

    # check subject is same as input
    for Line in Lines:
        if "Subject:" in Line:
            ColIdx = Line.find(':')
            FileParticipant = Line[ColIdx+1:].strip().lstrip('0')
            break
    if FileParticipant != Participant:
        raise EndoParseError(
            " * * * PARTICIPANT MISMATCH * * *\n" +
            "File Participant: {}".format(FileParticipant))

    # find baseline time
    BaselineTime = -1
    for Line in Lines:
        if "ImageDisplay1.OnsetTime" in Line:
            ColIdx = Line.find(':')
            BaselineTime = float(Line[ColIdx+1:].strip())
            break
    if BaselineTime == -1:
        raise EndoParseError(" * * * ImageDisplay1.OnsetTime NOT FOUND * * *")

    # grab data lines
    DataLines = []
    BlockIndex = 0
    for LineNo, Line in enumerate(Lines):
        for TextNo, OneText in enumerate(DataText):
            if OneText in Line:
                DataLines.append((Line, LineNo+1))
                break

    CurState = EmotionalState.ImageDis
    TrialCounter = 1
    for Pairs in DataLines:
        if CurState == EmotionalState.ImageDis:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = EmotionalState.ImageAns
        elif CurState == EmotionalState.ImageAns:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = EmotionalState.ImageOnset
        elif CurState == EmotionalState.ImageOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = (float(Pairs[0][ColLoc+1:]) - BaselineTime) / 1000
            CurState = EmotionalState.ImageDur
        elif CurState == EmotinoalState.ImageDur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = float(Pairs[0][ColLoc+1:])/1000
            CurState = EmotionalState.ImageAcc
        elif CurState == EmotionalState.ImageAcc:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = int(Pairs[0][ColLoc+1:])
            CurState = EmotionalState.ImageRt
        elif CurState == EmotionalState.ImageRt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = float(Pairs[0][ColLoc+1:])/1000
            CurState = EmotionalState.ImageResp
        elif CurState == EmotionalState.ImageResp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = int(Pairs[0][ColLoc+1:])/1000
            CurState = EmotionalState.ImageCresp
        elif CurState == EmotionalState.ImageCresp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = int(Pais[0][ColLoc+1:])/1000
            CurState = EmotionalState.DelayOnset
        elif CurState == EmotionalState.DelayOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = (float(Pairs[0][ColLoc+1:]) - BaselineTime) / 1000
            CurState = EmotionalState.DelayDur
        elif CurState == EmotionalState.DelayDur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value])
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value] = float(Pairs[0][ColLoc+1:])/1000
            CurState = EmotionalState.ImageDis

    if CurState != EmotionalState.ImageDis:
        raise EndoParseError("Bad emotional Termination: {} {}".format(
            DataText[EmotionalState.ImageDis], DataText[CurState.value])

    return Trials


    
    
def TestVerbalMem():
    try:
        FileName = '/home/heffjos/Documents/ForOthers/Endopoid/EprimeScripts/ConvertedEprime/I00020/VerbalMemA/endopoid_VerbalMemA_Run1-20-1.txt'
        Participant = '20'
        Trials = ParseVerbalMem(FileName, Participant)
    except EndoTransitionError as err:
        print("LineNo:    {}\n".format(err.LineNo) +
              "Found :    {}\n".format(err.FoundStr) +
              "Expected : {}".format(err.ExpectedStr))
    except EndoParseError as err:
        print("{}".format(err.Message))
    except:
        print("Unexpected error")
        raise

    return Trials
    

        
            
                    
            
                    
    
    

            
        
        
    
    
