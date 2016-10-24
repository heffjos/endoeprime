library(dplyr)

Converted <- "./ConvertedEprime"
Participants <- list.files(Converted, "I0.+0[^1]$|I0.+[1-9].")

# do Emotional first
FNames <- paste(Participants, "Emotional.csv", sep="_")
ParFiles <- file.path(Converted, Participants, "Emotional", FNames)
Data <- lapply(ParFiles, read.csv)
Data <- bind_rows(Data)
MDF <- Data %>%
  group_by(Participant, Run, Block) %>%
  summarize(Type=ImageAnswer[1], 
    Onset=ImageOnset[1], 
    Duration=sum(ImageDur+DelayDur)
  ) %>%
  mutate(CondNum=ifelse(Type == "Neutral", 1, NA),
    CondNum=ifelse(Type == "Negative", 2, CondNum))

names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Emotional.csv", quote=F, row.names=F, na="NaN")

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(AvgAcc=sum(ImageAcc)/n(),
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
  summarize(AvgAcc=sum(ImageAcc)/n(),
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
Data <- lapply(FNames, read.csv)
Data <- bind_rows(Data)
MDF <- Data %>%
  group_by(Participant, Run, Block) %>%
  summarize(VerbalType=VerbalType[1],
    Condition=BlockType[1],
    Onset=Onset[1],
    Duration=36
  ) %>%
  mutate(CondNum=ifelse(Condition == "Idea", 1, NA),
    CondNum=ifelse(Condition == "Case", 2, CondNum))

names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Verbal.csv", quote=F, row.names=F, na="NaN")

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(AvgAcc=sum(Acc)/n(),
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
  summarize(AvgAcc=sum(Acc)/n(),
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

# # do visual memory now
# FNames <- Sys.glob("./ConvertedEprime/*/Visual/*csv")
# FNames <- grep("I0.+0[^1]/|I0.+[1-9]./", FNames, value=T)
# Data <- lapply(FNames, read.csv)
# Data <- bind_rows(Data)
# MDF <- Data %>%
#     group_by(Participant, Run, Block) %>%
#     summarize(Condition=Running[1],
#       Onset=Onset[1],
      
