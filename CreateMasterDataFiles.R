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
  mutate(ConNum=ifelse(Type == "Neutral", 1, NA),
    CondNum=ifelse(Type == "Negative", 2, Type))

names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MDF_Emotional.csv", quote=F, row.names=F)

RunSummary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(Acc=sum(ImageAcc)/n(),
    AllRt=sum(ImageRt)/n(),
    CorrectRt=sum(ImageRt[ImageAcc == 1])/sum(ImageAcc == 1),
    IncorrectRt=sum(ImageRt[ImageAcc == 0])/sum(ImageAcc == 0),
    NeutralAcc=sum(ImageAcc[ImageAnswer == "Neutral"])/sum(ImageAnswer == "Neutral"),
    NegativeAcc=sum(ImageAcc[ImageAnswer == "Negative"])/sum(ImageAnswer == "Negative"),
    NeutralRt=sum(ImageRt[ImageAnswer == "Neutral" & ImageAcc == 1])/sum(ImageAnswer == "Neutral" & ImageAcc == 1),
    NegativeRt=sum(ImageRt[ImageAnswer == "Negative" & ImageAcc == 1])/sum(ImageAnswer == "Negative" & ImageAcc == 1)
  )

write.csv(RunSummary, file="EmotionRunSummary.csv", quote=F, row.names=F)

ParSummary <- Data %>%
  group_by(Participant) %>%
  summarize(Acc=sum(ImageAcc)/n(),
    AllRt=sum(ImageRt)/n(),
    CorrectRt=sum(ImageRt[ImageAcc == 1])/sum(ImageAcc == 1),
    IncorrectRt=sum(ImageRt[ImageAcc == 0])/sum(ImageAcc == 0),
    NeutralAcc=sum(ImageAcc[ImageAnswer == "Neutral"])/sum(ImageAnswer == "Neutral"),
    NegativeAcc=sum(ImageAcc[ImageAnswer == "Negative"])/sum(ImageAnswer == "Negative"),
    NeutralRt=sum(ImageRt[ImageAnswer == "Neutral" & ImageAcc == 1])/sum(ImageAnswer == "Neutral" & ImageAcc == 1),
    NegativeRt=sum(ImageRt[ImageAnswer == "Negative" & ImageAcc == 1])/sum(ImageAnswer == "Negative" & ImageAcc == 1)
  )

write.csv(ParSummary, file="EmotionParSummary.csv", quote=F, row.names=F)

# do verbal memory now
FNamesA <- paste(Participants, "VerbalMemA.csv", sep="_")
FNamesA <- file.path(Converted, Participants, "VerbalMemA", FNamesA)
FNamesB <- paste(Participants, "VerbalMemB.csv", sep="_")
FNamesB <- file.path(Converted, Participants, "VerbalMemB", FNamesB)
ParFiles <- data.frame(Dirs=file.path(Converted, Participants), VerbalMemType=NA) 
#   mutate(VerbalMemType[file.exists(FNamesA)]="A",
#     VerbalMemType[file.exists(FNamesB)]="B")
