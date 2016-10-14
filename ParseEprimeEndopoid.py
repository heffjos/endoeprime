from enum import Enum
import argparse

class EndoError(Exception):
    """Base class for exception in this module."""
    pass

class EndoParseError(EndoError):
    """Exception raised if parsing error occurs for verbal eprime files.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, Message, Participant, InFile):
        self.Message = Message
        self.InFile = InFile
        self.Participant = Participant
    

class EndoTransitionError(EndoError):
    """Raised when an operation attempts a state transistion that is not 
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        expected -- expected state
        message -- explanation of why the specific transition is not allowed
    """
    def __init__(self, LineNo, FoundStr, ExpectedStr, Participant, InFile):
        self.LineNo = LineNo
        self.FoundStr = FoundStr
        self.ExpectedStr = ExpectedStr
        self.InFile = InFile
        self.Participant = Participant

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
    ImageCresp = 7   # int
    DelayOnset = 8  # float
    DelayDur = 9    # float
    DelayRt = 10    # float
    TrialNum = 11   # only used for indexing, int
    Block = 12      # only used for indexing, int

class VisualMemState(Enum):
    Task = 0            # int
    Answer = 1          # int
    MatchLocation = 2   # str
    Running = 3         # str
    ResponseOnset = 4   # float
    ResponseOffset = 5  # float
    ResponseAcc = 6     # int
    ResponseRt = 7      # float
    ResponseResp = 8    # int
    ResponseCresp = 9   # int
    RunLists = 10       # int
    TrialNum = 11       # only used for indexing trials
    

def ParseVerbalMem(FileName, Participant, Run):
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
        "Run{}Lists:".format(Run)]

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
            "File Participant: {}".format(FileParticipant),
            Participant=Participant, InFile=FileName)

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
            "Expected period durations: {}".format(PeriodDurations),
            Participant=Participant, InFile=FileName)

    # find baseline time
    BaselineTime = -1
    for Line in Lines:
        if "myDisDaqs.OnsetTime" in Line:
            ColIdx = Line.find(':')
            BaselineTime = float(Line[ColIdx+1:].strip())
            break
    if BaselineTime == -1:
        raise EndoVerbelParseError(" * * * myDisDaqs.OnsetTime NOT FOUND * * *",
            Participant=Participant, InFile=FileName)

    # grab block lines  
    BlockLines = []
    for LineNo, Line in enumerate(Lines):
        if "Run{}Lists:".format(Run) in Line:
            BlockLines.append((Line, LineNo+1))
    if not BlockLines:
        raise EndoParseError("* * * BlockLines list EMPTY * * *",
            Participant=Participant, InFile=FileName)

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
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = VerbalMemState.Abst
        elif CurState == VerbalMemState.Abst:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            tmp = Pairs[0][ColLoc+1:].strip()
            if tmp == "a":
                Trials[CurState.value].append("Abstract")
            elif tmp == "c":
                Trials[CurState.value].append("Concrete")
            else:
                raise EndoParseError("* * * UNEXPECTED IDEA: {} * * *".format(tmp),
                    Participant=Participant, InFile=FileName)
            CurState = VerbalMemState.Case
        elif CurState == VerbalMemState.Case:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            tmp = Pairs[0][ColLoc+1:].strip()
            if tmp == "l":
                Trials[CurState.value].append("Lower")
            elif tmp == "u":
                Trials[CurState.value].append("Upper")
            else:
                raise EndoParseError("* * * UNEXPECTED CASE: {} * * *".format(tmp),
                    Participant=Participant, InFile=FileName)
            CurState = VerbalMemState.Onset
        elif CurState == VerbalMemState.Onset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VerbalMemState.Rt
        elif CurState == VerbalMemState.Rt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:].strip()) / 1000)
            CurState = VerbalMemState.Resp
        elif CurState == VerbalMemState.Resp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VerbalMemState.Cresp
        elif CurState == VerbalMemState.Cresp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VerbalMemState.Dur
        elif CurState == VerbalMemState.Dur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:].strip()) / 1000)
            CurState = VerbalMemState.FixOnset
        elif CurState == VerbalMemState.FixOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VerbalMemState.RunLists
        elif CurState == VerbalMemState.RunLists:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[VerbalMemState.RunLists.value].append(int(Pairs[0][ColLoc+1:].strip()))
            Trials[VerbalMemState.TrialNum.value].append(TrialCounter)
            TrialCounter += 1
            CurState = VerbalMemState.Stim

    if CurState != VerbalMemState.Stim:
        raise EndoParseError("Bad verbal Termination: {} {}".format(
            DataText[VerbalMemState.Stim], DataText[CurState.value]),
            Participant=Participant, InFile=FileName)

    return Trials

def PrintVerbalMemShort(OutFile, RunTrials, Participant):
    with open(OutFile, 'w') as Out:
        # print header
        print("Participant,Run,TrialNum," 
              + "Block,Stimulus,Idea," 
              + "Case,Onset,RT," 
              + "Response,CResponse,TrialDuration,"
              + "FixOnset", file=Out)

        # print out data
        for RunNum, Trials in enumerate(RunTrials, 1):
            for Idx in range(len(Trials[0])):
                print("{},{},{},".format(Participant, RunNum, Trials[10][Idx])
                    + "{},{},{},".format(Trials[9][Idx], Trials[0][Idx], Trials[1][Idx])
                    + "{},{},{},".format(Trials[2][Idx], Trials[3][Idx], Trials[4][Idx])
                    + "{},{},{},".format(Trials[5][Idx], Trials[6][Idx], Trials[7][Idx])
                    + "{}".format(Trials[8][Idx]), file=Out)

def ParseEmotional(FileName, Participant):
    # let's assume the first trial is "baseline (time = 0)"
    # this is a reasonable guess because from Run5-037 we have
    # volumes = (80 * 2) = 160
    # first onset:      30530
    # last offset:     190525
    # total duraiton:  160000
    # StartScanner.OnsetTime = 16453
    # (190525 - 30530)/1000 = 159.995
    # (190525 - 16453)/1000 = 174.072
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
        "ShortDelay.Duration:",
        "ShortDelay.RT:"
    ]

    Trials = [[] for _ in range(EmotionalState.Block.value + 1)]

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
            " * * * PARTICIPANT MISMATCH * * *\n" 
            + "File Participant: {}".format(FileParticipant),
            Participant=Participant, InFile=FileName)

    # find baseline time
    BaselineTime = -1
    for Line in Lines:
        if "ImageDisplay1.OnsetTime" in Line:
            ColIdx = Line.find(':')
            BaselineTime = float(Line[ColIdx+1:].strip())
            break
    if BaselineTime == -1:
        raise EndoParseError(" * * * ImageDisplay1.OnsetTime NOT FOUND * * *",
            Participant=Participant, InFile=FileName)

    # grab data lines
    DataLines = []
    BlockIndex = 0
    for LineNo, Line in enumerate(Lines):
        for TextNo, OneText in enumerate(DataText):
            if OneText in Line and "MyAnswer" not in Line:
                DataLines.append((Line, LineNo+1))
                break

    CurState = EmotionalState.ImageDis
    TrialCounter = 1
    BlockCounter = 1
    for Pairs in DataLines:
        if CurState == EmotionalState.ImageDis:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = EmotionalState.ImageAns
        elif CurState == EmotionalState.ImageAns:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            if TrialCounter != 1:
                tmp = Trials[CurState.value]
                if tmp[TrialCounter-1] != tmp[TrialCounter-2]:
                    BlockCounter += 1
            CurState = EmotionalState.ImageOnset
        elif CurState == EmotionalState.ImageOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:]) - BaselineTime) / 1000)
            CurState = EmotionalState.ImageDur
        elif CurState == EmotionalState.ImageDur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:])/1000)
            CurState = EmotionalState.ImageAcc
        elif CurState == EmotionalState.ImageAcc:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:]))
            CurState = EmotionalState.ImageRt
        elif CurState == EmotionalState.ImageRt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:])/1000)
            CurState = EmotionalState.ImageResp
        elif CurState == EmotionalState.ImageResp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:]))
            CurState = EmotionalState.ImageCresp
        elif CurState == EmotionalState.ImageCresp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:]))
            CurState = EmotionalState.DelayOnset
        elif CurState == EmotionalState.DelayOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:]) - BaselineTime) / 1000)
            CurState = EmotionalState.DelayDur
        elif CurState == EmotionalState.DelayDur:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:])/1000)
            CurState = EmotionalState.DelayRt
        elif CurState == EmotionalState.DelayRt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:])/1000)
            Trials[EmotionalState.TrialNum.value].append(TrialCounter)
            TrialCounter += 1
            Trials[EmotionalState.Block.value].append(BlockCounter)
            CurState = EmotionalState.ImageDis
        
    if CurState != EmotionalState.ImageDis:
        raise EndoParseError("Bad emotional Termination: {} {}".format(
            DataText[EmotionalState.ImageDis], DataText[CurState.value]),
            Participant=Participant, InFile=FileName)

    return Trials

def PrintEmotionalShort(OutFile, RunTrials, Participant):
    with open(OutFile, "w") as Out:
        # print header
        print("Participant,Run,TrialNum,"
            + "Block,ImageDis,ImageAnswer,"
            + "ImageOnset,ImageDur,ImageAcc,"
            + "ImageRt,ImageResp,ImageCresp,"
            + "DelayOnset,DelayDur,DelayRt", file=Out)

        # print out data
        for RunNum, Trials in enumerate(RunTrials, 1):
            for Idx in range(len(Trials[0])):
                print("{},{},{},".format(Participant, RunNum, Trials[11][Idx])
                    + "{},{},{},".format(Trials[12][Idx], Trials[0][Idx], Trials[1][Idx])
                    + "{},{},{},".format(Trials[2][Idx], Trials[3][Idx], Trials[4][Idx])
                    + "{},{},{},".format(Trials[5][Idx], Trials[6][Idx], Trials[7][Idx])
                    + "{},{},{}".format(Trials[8][Idx], Trials[9][Idx], Trials[10][Idx]), file=Out)

def ParseVisualMem(FileName, Participant, Run):
    # 21 1
    # first onset: 52768
    # last onset:  409831
    # volumes: 180 * 2 = 360s
    # time difference (409831 - 52768)/1000 = 358.036
    #
    # OnsetTime: 283460 - 286435,
    #            293450 - 296435,
    #            303457 - 306435,
    #            313464 - 316335
    #            
    # this has period durations and RunLists
    TruePeriodDurations = (40000, 40000, 40000, 40000, 40000, 40000, 40000, 40000, 40000)

    DataText = [
        "Task:",
        "Answer:",
        "MatchLocation:",
        "Running:",
        "Response.OnsetTime:",
        "Response.OffsetTime:",
        "Response.ACC:",
        "Response.RT:",
        "Response.RESP:",
        "Response.CRESP:",
        "RunList{}:".format(Run)
    ]

    Trials = [[] for _ in range(VisualMemState.TrialNum.value + 1)]

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
            "File Participant: {}".format(FileParticipant),
            Participant=Participant, InFile=FileName)

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
            "Expected period durations: {}".format(PeriodDurations),
            Participant=Participant, InFile=FileName)

    # find baseline time
    BaselineTime = -1
    for Line in Lines:
        if "ClearScreen.OnsetTime:" in Line:
            ColIdx = Line.find(':')
            BaselineTime = float(Line[ColIdx+1:].strip())
            break
    if BaselineTime == -1:
        raise EndoVerbelParseError(" * * * ClearScreen.OnsetTime NOT FOUND * * *",
            Participant=Participant, InFile=FileName)

    # grab block lines  
    BlockLines = []
    for LineNo, Line in enumerate(Lines):
        if DataText[VisualMemState.RunLists.value] in Line:
            BlockLines.append((Line, LineNo+1))
    if not BlockLines:
        raise EndoParseError("* * * BlockLines list EMPTY * * *",
            Participant=Participant, InFile=FileName)

    # grab data lines
    DataLines = []
    BlockIndex = 0
    for LineNo, Line in enumerate(Lines):
        for TextNo, OneText in enumerate(DataText):
            if (OneText in Line and "PeriodList" not in Line and
                "IFISBlockList" not in Line):
                if TextNo != VisualMemState.RunLists.value:
                    DataLines.append((Line, LineNo+1))
                else:
                    BlockIndex += 1
                if TextNo == VisualMemState.ResponseCresp.value:
                    DataLines.append(BlockLines[BlockIndex])
                break

    # do work here
    CurState = VisualMemState.Task
    TrialCounter = 1
    for Pairs in DataLines:
        if CurState == VisualMemState.Task:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VisualMemState.Answer
        elif CurState == VisualMemState.Answer:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VisualMemState.MatchLocation
        elif CurState == VisualMemState.MatchLocation:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = VisualMemState.Running
        elif CurState == VisualMemState.Running:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(Pairs[0][ColLoc+1:].strip())
            CurState = VisualMemState.ResponseOnset
        elif CurState == VisualMemState.ResponseOnset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VisualMemState.ResponseOffset
        elif CurState == VisualMemState.ResponseOffset:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append((float(Pairs[0][ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = VisualMemState.ResponseAcc
        elif CurState == VisualMemState.ResponseAcc:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VisualMemState.ResponseRt
        elif CurState == VisualMemState.ResponseRt:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(float(Pairs[0][ColLoc+1:].strip())/1000)
            CurState = VisualMemState.ResponseResp
        elif CurState == VisualMemState.ResponseResp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VisualMemState.ResponseCresp
        elif CurState == VisualMemState.ResponseCresp:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            CurState = VisualMemState.RunLists
        elif CurState == VisualMemState.RunLists:
            if DataText[CurState.value] not in Pairs[0]:
                raise EndoTransitionError(Pairs[1], Pairs[0], DataText[CurState.value],
                    Participant=Participant, InFile=FileName)
            ColLoc = Pairs[0].find(":")
            Trials[CurState.value].append(int(Pairs[0][ColLoc+1:].strip()))
            Trials[VisualMemState.TrialNum.value].append(TrialCounter)
            TrialCounter += 1
            CurState = VisualMemState.Task

    if CurState != VisualMemState.Task:
        raise EndoParseError("Bad visual termination: {} {}".format(
            DataText[VisualMemState.Task], DataText[CurState.value]),
            Participant=Participant, InFile=FileName)

    return Trials

def PrintVisualMemShort(OutFile, RunTrials, Participant):
    with open(OutFile, "w") as Out:
        # print header first
        print("Participant,Run,TrialNum,"
            + "BlockNum,Task,Answer,"
            + "MatchLocation,Running,ResponseOnset,"
            + "ResponseOffset,ResponseAcc,ResponseRt,"
            + "ResponseResp,ResponseCresp", file=Out)

        # now print out data
        for RunNum, Trials in enumerate(RunTrials, 1):
            for Idx in range(len(Trials[0])):
                print("{},{},{},".format(Participant, RunNum, Trials[11][Idx])
                    + "{},{},{},".format(Trials[10][Idx], Trials[0][Idx], Trials[1][Idx])
                    + "{},{},{},".format(Trials[2][Idx], Trials[3][Idx], Trials[4][Idx])
                    + "{},{},{},".format(Trials[5][Idx], Trials[6][Idx], Trials[7][Idx])
                    + "{},{}".format(Trials[8][Idx], Trials[9][Idx]), file=Out)
    
def TestVerbalMem():
    try:
        FileName = '/home/heffjos/Documents/ForOthers/Endopoid/EprimeScripts/ConvertedEprime/I00020/VerbalMemA/endopoid_VerbalMemA_Run1-20-1.txt'
        Participant = '20'
        Trials = ParseVerbalMem(FileName, Participant, 1)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse endopoid eprime files.')
    parser.add_argument('--task', required=True, help="task for eprime files",
        choices=["verbal", "visual", "emotional"])
    parser.add_argument('--participant', required=True, help="participant name")
    parser.add_argument('--outfile', required=True, help="output csv file")
    parser.add_argument('--infiles', required=True, help="input eprime files",
        nargs='+')
    args = parser.parse_args()

    try:
        RunTrials = []
        if args.task == "verbal":
            for RunNum, OneFile in enumerate(args.infiles, 1):
                RunTrials.append(ParseVerbalMem(OneFile, args.participant, RunNum))
            PrintVerbalMemShort(args.outfile, RunTrials, args.participant)
        elif args.task == "visual":
            for RunNum, OneFile in enumerate(args.infiles, 1):
                RunTrials.append(ParseVisualMem(OneFile, args.participant, RunNum))
            PrintVisualMemShort(args.outfile, RunTrials, args.participant)
        elif args.task == "emotional":
            for RunNum, OneFile in enumerate(args.infiles, 1):
                RunTrials.append(ParseEmotional(OneFile, args.participant))
            PrintEmotionalShort(args.outfile, RunTrials, args.participant)
    except EndoParseError as err:
        print(" * * * PARSE ERROR * * *\n" 
            + "Participant: {}\n".format(err.Participant)
            + "File       : {}\n".format(err.InFile)
            + err.Message)
    except EndoTransitionError as err:
        print(" * * * TRANSITION ERROR * * *\n"
            + "Participant: {}\n".format(err.Participant)
            + "File       : {}\n".format(err.InFile)
            + "LinNo      : {}\n".format(err.LineNo)
            + "Found      : {}\n".format(err.FoundStr)
            + "Expected   : {}".format(err.ExpectedStr))
    except:
        raise

def tmp():
    print("asdf\n"
        + "qwerty")

    for Idx, OneNum in enumerate([0, 1, 2, 3, 4], 1):
        print("Idx:{} OneNum:{}".format(Idx, OneNum))
            

