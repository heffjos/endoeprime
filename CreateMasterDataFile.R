library(dplyr)


MasterDir <- '/nfs/turbo/berent-lab/metabolic/Endopoid/Data/'
Participants <- list.files(MasterDir, pattern="abs13(ins|end)[0-9]+_[0-9]+")
MdfTemplate <- read.csv("./TaskTemplates.csv")

Emotion <- MdfTemplate %>%
  filter(Task == "emotion") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "Neutral", 1, NA),
    CondNum=ifelse(Condition == "Negative", 2, CondNum))
Emotion <- rep(list(Emotion), length(Participants))
Emotion <- Map(
  function(x, y) {
    x$Participant = y
    x
  }, Emotion, Participants)
MDF <- bind_rows(Emotion)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Emotional.csv", quote=F, row.names=F, na="NaN")

Verbal <- MdfTemplate %>%
  filter(Task == "verbal") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "AC", 1, NA),
    CondNum=ifelse(Condition == "UL", 2, CondNum))
Verbal <- rep(list(Verbal), length(Participants))
Verbal <- Map(
  function(x, y) {
    x$Participant = y
    x
  }, Verbal, Participants)
MDF <- bind_rows(Verbal)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Verbal.csv", quote=F, row.names=F, na="NaN")

Visual <- MdfTemplate %>%
  filter(Task == "visual") %>%
  select(Participant, Task, Condition, Run, TimeOnset, DurationTime) %>%
  mutate(CondNum=ifelse(Condition == "Match", 1, NA),
    CondNum=ifelse(Condition == "Delay1", 2, CondNum),
    CondNum=ifelse(Condition == "Delay4", 3, CondNum))
Visual <- rep(list(Visual), length(FNames))
Visual <- Map(
  function(x, y) {
    x$Participant = y
    x
  }, Visual, Participants)
MDF <- bind_rows(Visual)
names(MDF)[1] <- "#Participant"
write.csv(MDF, file="MasterDataFiles/MDF_Visual.csv", quote=F, row.names=F, na="NaN")    
