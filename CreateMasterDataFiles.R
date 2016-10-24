library(dplyr)
library(stringr)

Converted <- "./ConvertedEprime"
Participants <- list.files(Converted, "I0.+0[^1]$|I0.+[1-9].")
MdfTemplate <- read.csv("./TaskTemplates.csv")

# do Emotional first
FNames <- Sys.glob("./ConvertedEprime/*/Emotional/*csv")
FNames <- grep("I0.+0[^1]/|I0.+[1-9]./", FNames, value=T)
FNamesSplit <- str_split(FNames, "/")
Data <- lapply(FNames, read.csv)
Data <- bind_rows(Data)

Tmp <- MdfTemplate %>%
  filter(Task == "emotion") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "Neutral", 1, NA),
    CondNum=ifelse(Condition == "Negative", 2, CondNum))
Tmp <- rep(list(Tmp), length(Participants))
Tmp <- Map(
  function(x, y) {
    x$Participant = y[3]
    x
  }, Tmp, FNamesSplit)
MDF <- bind_rows(Tmp)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Emotional.csv", quote=F, row.names=F, na="NaN")

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(TotalTrials=n(),
    NumNoResp=sum(is.na(ImageRt)),
    NumIncorrect=sum(ImageAcc == 0),
    AvgAcc=sum(ImageAcc)/n(),
    AvgAllRt=sum(ImageRt, na.rm=T)/n(),
    AvgCorrectRt=sum(ImageRt[ImageAcc == 1], na.rm=T)/sum(ImageAcc == 1),
    AvgIncorrectRt=sum(ImageRt[ImageAcc == 0], na.rm=T)/sum(ImageAcc == 0),
    AvgNeutralAcc=sum(ImageAcc[ImageAnswer == "Neutral"])/sum(ImageAnswer == "Neutral"),
    AvgNegativeAcc=sum(ImageAcc[ImageAnswer == "Negative"])/sum(ImageAnswer == "Negative"),
    AvgNeutralRt=sum(ImageRt[ImageAnswer == "Neutral" & ImageAcc == 1], na.rm=T)
      / sum(ImageAnswer == "Neutral" & ImageAcc == 1),
    AvgNegativeRt=sum(ImageRt[ImageAnswer == "Negative" & ImageAcc == 1], na.rm=T)
      / sum(ImageAnswer == "Negative" & ImageAcc == 1)
  )
write.csv(RunSummary, file="EprimeSummaries/EmotionRunSummary.csv", quote=F, row.names=F)

ParSummary <- Data %>%
  group_by(Participant) %>%
  summarize(TotalTrials=n(),
    NumNoResp=sum(is.na(ImageRt)),
    NumIncorrect=sum(ImageAcc == 0),
    AvgAcc=sum(ImageAcc)/n(),
    AvgAllRt=sum(ImageRt, na.rm=T)/n(),
    AvgCorrectRt=sum(ImageRt[ImageAcc == 1], na.rm=T)/sum(ImageAcc == 1),
    AvgIncorrectRt=sum(ImageRt[ImageAcc == 0], na.rm=T)/sum(ImageAcc == 0),
    AvgNeutralAcc=sum(ImageAcc[ImageAnswer == "Neutral"])/sum(ImageAnswer == "Neutral"),
    AvgNegativeAcc=sum(ImageAcc[ImageAnswer == "Negative"])/sum(ImageAnswer == "Negative"),
    AvgNeutralRt=sum(ImageRt[ImageAnswer == "Neutral" & ImageAcc == 1], na.rm=T)
      / sum(ImageAnswer == "Neutral" & ImageAcc == 1),
    AvgNegativeRt=sum(ImageRt[ImageAnswer == "Negative" & ImageAcc == 1], na.rm=T) 
      / sum(ImageAnswer == "Negative" & ImageAcc == 1)
  )
write.csv(ParSummary, file="EprimeSummaries/EmotionParSummary.csv", quote=F, row.names=F)

# do verbal memory now
FNames <- Sys.glob("./ConvertedEprime/*/Verbal*/*csv")
FNames <- grep("I0.+0[^1]/|I0.+[1-9]./", FNames, value=T)
FNamesSplit <- str_split(FNames, "/")
Data <- lapply(FNames, read.csv)
Data <- bind_rows(Data)

Tmp <- MdfTemplate %>%
  filter(Task == "verbal") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "AC", 1, NA),
    CondNum=ifelse(Condition == "UL", 2, CondNum))
Tmp <- rep(list(Tmp), length(FNamesSplit))
Tmp <- Map(
  function(x, y) {
    x$Participant = y[3]
    x$Task = y[4]
    x
  }, Tmp, FNamesSplit)
MDF <- bind_rows(Tmp)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Verbal.csv", quote=F, row.names=F, na="NaN")

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(VerbalType=VerbalType[1],
    TotalTrials=n(),
    NumNoResp=sum(is.na(RT)),
    NumIncorrect=sum(Acc == 0),
    AvgAcc=sum(Acc)/n(),
    AvgAllRt=sum(RT, na.rm=T)/n(),
    AvgCorrectRt=sum(RT[Acc == 1], na.rm=T)/sum(Acc == 1),
    AvgIncorrectRt=sum(RT[Acc == 0], na.rm=T)/sum(Acc == 0),
    AvgIdeaAcc=sum(Acc[BlockType == "Idea"])/sum(BlockType == "Idea"),
    AvgCaseAcc=sum(Acc[BlockType == "Case"])/sum(BlockType == "Case"),
    AvgIdeaRt=sum(RT[BlockType == "Idea" & Acc == 1], na.rm=T)
        / sum(BlockType == "Idea" & Acc == 1),
    AvgCaseRt=sum(RT[BlockType == "Case" & Acc == 1], na.rm=T)
        / sum(BlockType == "Case" & Acc == 1)
  )
write.csv(RunSummary, file="EprimeSummaries/VerbalRunSummary.csv", quote=F, row.names=F)

ParticipantSummary <- Data %>%
  group_by(Participant) %>%
  summarize(VerbalType=VerbalType[1],
    TotalTrials=n(),
    NumNoResp=sum(is.na(RT)),
    NumIncorrect=sum(Acc == 0),
    AvgAcc=sum(Acc)/n(),
    AvgAllRt=sum(RT, na.rm=T)/n(),
    AvgCorrectRt=sum(RT[Acc == 1], na.rm=T)/sum(Acc == 1),
    AvgIncorrectRt=sum(RT[Acc == 0], na.rm=T)/sum(Acc == 0),
    AvgIdeaAcc=sum(Acc[BlockType == "Idea"])/sum(BlockType == "Idea"),
    AvgCaseAcc=sum(Acc[BlockType == "Case"])/sum(BlockType == "Case"),
    AvgIdeaRt=sum(RT[BlockType == "Idea" & Acc == 1], na.rm=T)
        / sum(BlockType == "Idea" & Acc == 1),
    AvgCaseRt=sum(RT[BlockType == "Case" & Acc == 1], na.rm=T)
        / sum(BlockType == "Case" & Acc == 1)
  )
write.csv(ParticipantSummary, file="EprimeSummaries/VerbalParSummary.csv", quote=F, row.names=F)

# do visual memory now
FNames <- Sys.glob("./ConvertedEprime/*/VisualMem/*csv")
FNames <- grep("I0.+0[^1]/|I0.+[1-9]./", FNames, value=T)
FNamesSplit <- str_split(FNames, "/")
Data <- lapply(FNames, read.csv)
Data <- bind_rows(Data)

Tmp <- MdfTemplate %>%
  filter(Task == "visual") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "Match", 1, NA),
    CondNum=ifelse(Condition == "Delay1", 2, CondNum),
    CondNum=ifelse(Condition == "Delay4", 3, CondNum))
Tmp <- rep(list(Tmp), length(FNames))
Tmp <- Map(
  function(x, y) {
    x$Participant = y[3]
    x
  }, Tmp, FNamesSplit)
MDF <- bind_rows(Tmp)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Visual.csv", quote=F, row.names=F, na="NaN")    

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(TotalTrials=n(),
    NumNoResp=sum(is.na(ResponseRt)),
    NumIncorrect=sum(ResponseAcc == 0, na.rm=T),
    AvgAcc=sum(ResponseAcc)/n(),
    AvgAllRt=sum(ResponseRt, na.rm=T)/n(),
    AvgCorrectRt=sum(ResponseRt[ResponseAcc == 1], na.rm=T)/sum(ResponseAcc == 1),
    AvgIncorrectRt=sum(ResponseRt[ResponseAcc == 0], na.rm=T)/sum(ResponseAcc == 0),
    AvgMatchAcc=sum(ResponseAcc[Running == "MatchTrialList"])/sum(Running == "MatchTrialList"),
    AvgDelay1Acc=sum(ResponseAcc[Running == "DelayOneTrialList"])/sum(Running == "DelayOneTrialList"),
    AvgDelay4Acc=sum(ResponseAcc[Running == "DelayFourTrialList"])/sum(Running == "DelayFourTrialList"),
    AvgMatchRt=sum(ResponseRt[Running == "MatchTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "MatchTrialList" & ResponseAcc == 1),
    AvgDelay1Rt=sum(ResponseRt[Running == "DelayOneTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "DelayOneTrialList" & ResponseAcc == 1),
    AvgDelay4Rt=sum(ResponseRt[Running == "DelayFourTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "DelayFourTrialList" & ResponseAcc == 1)
  )
write.csv(RunSummary, file="EprimeSummaries/VisualParSummary.csv", quote=F, row.names=F)

RunSummary <- Data %>%
  group_by(Participant) %>%
  summarize(TotalTrials=n(),
    NumNoResp=sum(is.na(ResponseRt)),
    NumIncorrect=sum(ResponseAcc == 0, na.rm=T),
    AvgAcc=sum(ResponseAcc)/n(),
    AvgAllRt=sum(ResponseRt, na.rm=T)/n(),
    AvgCorrectRt=sum(ResponseRt[ResponseAcc == 1], na.rm=T)/sum(ResponseAcc == 1),
    AvgIncorrectRt=sum(ResponseRt[ResponseAcc == 0], na.rm=T)/sum(ResponseAcc == 0),
    AvgMatchAcc=sum(ResponseAcc[Running == "MatchTrialList"])/sum(Running == "MatchTrialList"),
    AvgDelay1Acc=sum(ResponseAcc[Running == "DelayOneTrialList"])/sum(Running == "DelayOneTrialList"),
    AvgDelay4Acc=sum(ResponseAcc[Running == "DelayFourTrialList"])/sum(Running == "DelayFourTrialList"),
    AvgMatchRt=sum(ResponseRt[Running == "MatchTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "MatchTrialList" & ResponseAcc == 1),
    AvgDelay1Rt=sum(ResponseRt[Running == "DelayOneTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "DelayOneTrialList" & ResponseAcc == 1),
    AvgDelay4Rt=sum(ResponseRt[Running == "DelayFourTrialList" & ResponseAcc == 1], na.rm=T)
        / sum(Running == "DelayFourTrialList" & ResponseAcc == 1)
  )
write.csv(RunSummary, file="EprimeSummaries/VisualRunSummary.csv", quote=F, row.names=F)
