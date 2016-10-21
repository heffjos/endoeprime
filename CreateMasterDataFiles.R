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
  mutate(TypeNum=ifelse(Type == "Neutral", 1, NA),
    TypeNum=ifelse(Type == "Negative", 2, TypeNum))

names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MDF_Emotional.csv", quote=F, row.names=F)

Summary <- Data %>%
  group_by(Participant, Run) %>%
  summarize(Acc=sum(ImageAcc)/n(),
    Rt=sum(ImageRt)/n(),
    CorrectRt=sum(ImageRt[ImageAcc==1])/sum(ImageAcc==1),
    IncorrectRt=sum(ImageRt[ImageAcc==0])/sum(ImageAcc==0))
    
    
