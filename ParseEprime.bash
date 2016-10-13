#!/bin/bash

OrigEprime=./eprime
ConvertedEprime=./ConvertedEprime

# conversion from unicode to utf-8
# Emotinal and Run are sometimes not eparated by an underscore
for OneTask in Emotional VerbalMemA VerbalMemB VisualMem
do
    for EprimeFile in ${OrigEprime}/*${OneTask}*txt
    do
        FName=`basename ${EprimeFile}`
        Subject=`echo ${EprimeFile} | awk -F- '{print $2}' | sed "s/^0*//g"`
        Subject=`printf I%05d ${Subject}`
        echo ${Subject}

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
        fi
    done
done
        
    
