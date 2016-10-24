#!/bin/bash

OrigEprime=./eprime
ConvertedEprime=./ConvertedEprime
Python=/home/heffjos/Documents/anaconda3/bin/python

# conversion from unicode to utf-8
# Emotinal and Run are sometimes not eparated by an underscore
for OneTask in Emotional VerbalMemA VerbalMemB VisualMem
do
    for EprimeFile in ${OrigEprime}/*${OneTask}*txt
    do
        FName=`basename ${EprimeFile}`
        Subject=`echo ${EprimeFile} | awk -F- '{print $2}' | sed "s/^0*//g"`
        Subject=`printf I%05d ${Subject}`
        echo ${Subject}:${OneTask}

        OutDir=${ConvertedEprime}/${Subject}/${OneTask}
        if [ ! -d ${OutDir} ]
        then
            mkdir -p ${OutDir}
        fi

        if [ ! -f ${OutDir}/${FName} ]
        then
            iconv \
                --from-code=unicode \
                --to-code=utf-8 \
                --output=${OutDir}/${FName} \
                ${EprimeFile}

            # correct trial 20 for VerbalMemA
            if [[ ${OneTask} == VerbalMemA && ${EprimeFile} == *"Run3"* ]]
            then
                sed -i -e 's/myCase: 1/myCase: l/g' ${OutDir}/${FName}
            fi  
        fi
    done
done

# correct mislabeled subjects for all files
for Mislabeled in I00011
do
    for OneFile in ${ConvertedEprime}/${Mislabeled}/*/*txt
    do  
        sed -i -e 's/Subject: 009/Subject: 011/g' ${OneFile}
    done
done

# now parse eprime to csv
for OneDir in ${ConvertedEprime}/*/*
do
    Participant=`echo ${OneDir} | awk -F/ '{print $3}'`
    Task=`echo ${OneDir} | awk -F/ '{print $4}'`

    echo ${Participant} ${Task}

    ${Python} ./ParseEprimeEndopoid.py --participant=${Participant} \
        --task=${Task} \
        --outfile=${OneDir}/${Participant}_${Task}.csv \
        --infiles `echo ${OneDir}/*txt`

    echo 
done

mkdir MasterDataFiles EprimeSummaries AvailableRuns
    
    
        
    
