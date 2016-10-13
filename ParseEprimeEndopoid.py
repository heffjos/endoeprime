
class EndoError(Exception):
    """Base class for exception in this module."""
    pass

class EndoVerbalParseError(EndoError):
    """Exception raised if parsing error occurs for verbal eprime files.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, Message):
        self.Message = Message

class EndoParticipantError(EndoError):
    """Exception raised for mismatching file and input subjects.

    Attributes:
        filesubject -- found subject name for file
        inputsubject -- input subject name
        message -- explanation of the error
    """
    def __init__(self, filesubject, inputsubject, message):
        self.filesubject = filesubject
        self.inputsubject = inputsubject
        self.message = message

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

class EndoPeriodDurationError(EndoError):
    """Exception raised when period durations within text file do not match
    expected durations.

    Attributes:
        expecteddurations -- the expected durations
        founddurations -- the durations parsed from the text file
        message -- explanation of why this error is raised
    """
    def __init__(self, expecteddurations, founddurations, message):
        self.expecteddurations = expecteddurations
        self.founddurations = founddurations
        self.message = message

class EndoBaselineTimeError(EndoError):
    """Exception raised when no baseline time is found.

    Attributes:
        message -- explanation of why this error is raised
    """
    def __init__(self, message):
        self.message = message
    

def ParseVerbalMem(FileName, Participant):
    TruePeriodDurations = (32000, 44000, 44000, 44000, 44000, 32000)
    STATE_STIM = "myStimulus"
    STATE_ABST = "conAbst"
    STATE_CASE = "myCase"
    STATE_ONSET = "Probe.OnsetTime"
    STATE_RT = "Probe.RT:"
    STATE_RESP = "Probe.RESP"
    STATE_CRESP = "Probe.CRESP"
    STATE_DUR = "Probe.OnsetToOnsetTime"
    STATE_FIX_ONSET = "fixation.OnsetTime"
    STATE_RUN_LISTS = "Run1Lists:"
    State = {
        STATE_STIM: 0,          # nmeonic for stimulus
        STATE_ABST: 1,          # signals concrete or abstract word
        STATE_CASE: 2,          # signals upper or lower case
        STATE_ONSET: 3,         # probe onset time
        STATE_RT: 4,            # participant reaction time for probe
        STATE_RESP: 5,          # participatn response
        STATE_CRESP: 6,         # indicates correct response
        STATE_DUR: 7,           # indicates probe duration
        STATE_FIX_ONSET: 8,     # fixation onset time
        STATE_RUN_LISTS: 9      # indicates run list
    }
    StateNames = dict(zip(State.values(), State.keys()))

    TRIALS_STIM = "Stimulus"
    TRIALS_IDEA = "Idea"
    TRIALS_CASE = "Case"
    TRIALS_ONSET = "ProbeOnsetTime"
    TRIALS_RT = "ProbeRT"
    TRIALS_RESP = "ProbeRESP"
    TRIALS_CRESP = "ProbeCRESP"
    TRIALS_DUR = "ProbeDuration"
    TRIALS_FIX_ONSET = "FixationOnsetTime"
    TRIALS_BLOCK_NUM = "BlockNumber"
    TRIALS_TRIAL_NUM = "TrialNum"
    Trials = {
        TRIALS_STIM: [],
        TRIALS_IDEA: [],
        TRIALS_CASE: [],
        TRIALS_ONSET: [],
        TRIALS_RT: [],
        TRIALS_RESP: [],
        TRIALS_CRESP: [],
        TRIALS_DUR: [],
        TRIALS_FIX_ONSET: [],
        TRIALS_BLOCK_NUM: [],
        TRIALS_TRIAL_NUM: []
    }

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
        raise EndoVerbalParseError(
            " * * * PARTICIPANT MISMATCH * * *\n" +
            "File Participant: {}".format(FileParticipant))

    # check for timings consistency
    PeriodDurations = []
    for Line in Lines:
        if "PeriodDuration:" in Line:
            ColIdx = Line.find(':')
            PeriodDurations.append(int(Line[ColIdx+1:].strip()))
    if PeriodDurations != list(TruePeriodDurations):
        raise EndoVerbalParseError(
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

    CurState = State[STATE_STIM]
    BlockTrialCounter = 0
    LineNo = 1
    TrialCounter = 1
    for Line in Lines:
        if STATE_STIM in Line:
            if CurState != State[STATE_STIM]:
                raise EndoTransitionError(LineNo, STATE_STIM, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_STIM].append(Line[ColLoc+1:].strip())
            CurState = State[STATE_ABST]
        elif STATE_ABST in Line:
            if CurState != State[STATE_ABST]:
                raise EndoTransitionError(LineNo, STATE_ABST, StateNames[CurState])
            ColLoc = Line.find(":")
            tmp = Line[ColLoc+1:].strip()
            if tmp == "a":
                Trials[TRIALS_IDEA].append("Abstract")
            elif tmp == "c":
                Trials[TRIALS_IDEA].append("Concrete")
            else:
                raise EndoVerbalParseError("* * * UNEXPECTED IDEA: {} * * *".format(tmp))
            CurState = State[STATE_CASE]
        elif STATE_CASE in Line:
            if CurState != State[STATE_CASE]:
                raise EndoTransitionError(LineNo, STATE_CASE, StateNames[CurState])
            ColLoc = Line.find(":")
            tmp = Line[ColLoc+1:].strip()
            if tmp == "l":
                Trials[TRIALS_CASE].append("Lower")
            elif tmp == "u":
                Trials[TRIALS_CASE].append("Upper")
            else:
                raise EndoVerbalParseError("* * * UNEXPECTED CASE: {} * * *".format(tmp))
            CurState = State[STATE_ONSET]
        elif STATE_ONSET in Line:
            if CurState != State[STATE_ONSET]:
                raise EndoTransitionError(LineNo, STATE_ONSET, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_ONSET].append((float(Line[ColLoc+1:].strip()) - BaselineTime) / 1000)
            CurState = State[STATE_RT]
        elif STATE_RT in Line:
            if CurState != State[STATE_RT]:
                raise EndoTransitionError(LineNo, STATE_RT, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_RT].append(float(Line[ColLoc+1:].strip()) / 1000)
            CurState = State[STATE_RESP]
        elif STATE_RESP in Line:
            if CurState != State[STATE_RESP]:
                raise EndoTransitionError(LineNo, STATE_RESP, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_RESP].append(int(Line[ColLoc+1:].strip()))
            CurState = State[STATE_CRESP]
        elif STATE_CRESP in Line:
            if CurState != State[STATE_CRESP]:
                raise EndoTransitionError(LineNo, STATE_CRESP, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_CRESP].append(int(Line[ColLoc+1:].strip()))
            CurState = State[STATE_DUR]
        elif STATE_DUR in Line:
            if CurState != State[STATE_DUR]:
                raise EndoTransitionError(LineNo, STATE_DUR, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_DUR].append(float(Line[ColLoc+1:].strip()) / 1000)
            CurState = State[STATE_FIX_ONSET]
        elif STATE_FIX_ONSET in Line:
            if CurState != State[STATE_FIX_ONSET]:
                raise EndoTransitionError(LineNo, STATE_FIX_ONSET, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_FIX_ONSET].append((float(Line[ColLoc+1:].strip()) - BaselineTime) / 1000)
            Trials[TRIALS_TRIAL_NUM].extend([TrialCounter] * 9)
            CurState = State[STATE_STIM]
            BlockTrialCounter += 1
        elif STATE_RUN_LISTS in Line:
            if CurState != State[STATE_STIM]:
                raise EndoTransitionError(LineNo, STATE_RUN_LISTS, StateNames[CurState])
            ColLoc = Line.find(":")
            Trials[TRIALS_BLOCK_NUM].extend([int(Line[ColLoc+1:].strip())] * BlockTrialCounter)
            BlockTrialCounter = 0
            CurState = State[STATE_STIM]
        LineNo += 1

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
    STATE_IMAGE = "MyImage"
    STATE_ANSWER = "Answer"
    STATE_IMAGE_ONSET = "ImageDisplay1.OnsetTime"
    STATE_IMAGE_DURATION = "ImageDisplay1.Duration"
    STATE_IMAGE_ACC = "ImageDisplay1.ACC"
    STATE_IMAGE_RT = "ImageDisplay1.RT"
    STATE_IMAGE_RESP = "ImageDisplay1.RESP"
    STATE_IMAGE_CRESP = "ImageDisplay1.CRESP"
    STATE_DELAY_ONSET = "ShortDelay.OnsetTime"
    STATE_DELAY_DURATION = "ShortDelay.Duration"
    
    State = {
        STATE_IMAGE: 0,
        STATE_ANSWER: 1,
        STATE_IMAGE_ONSET: 2,
    
    

def main():
    try:
        FileName = '/home/heffjos/Documents/ForOthers/Endopoid/EprimeScripts/ConvertedEprime/I00020/VerbalMemA/endopoid_VerbalMemA_Run1-20-1.txt'
        Participant = '20'
        Trials = ParseVerbalMem(FileName, Participant)
    except EndoTransitionError as err:
        print("LineNo:    {}\n".format(err.LineNo) +
              "Found :    {}\n".format(err.FoundStr) +
              "Expected : {}".format(err.ExpectedStr))
    except EndoVerbalParseError as err:
        print("{}".format(err.Message))

    return Trials
    

        
            
                    
            
                    
    
    

            
        
        
    
    
