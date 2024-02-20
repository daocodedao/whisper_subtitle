#!/bin/bash

workdir=/data/work/aishowos/whisper_subtitle
cd $workdir

. colors.sh


echo "${YELLOW}source venv/bin/activate${NOCOLOR}"
source venv/bin/activate

helpFunction()
{
   echo ""
   echo "Usage: $0 -l language -v videoPath -o outPath"
   echo -e "\t-l language, zh en"
   echo -e "\t-v video path"
   echo -e "\t-o outPath"
   echo -e "\t-t audio Text"
   exit 1 # Exit script after printing help
}


jobName=generate-subtitle.py 
echo "${YELLOW}check $jobName pid${NOCOLOR}"
echo "ps aux | grep "$jobName" | grep -v grep  | awk '{print $2}'"
TAILPID=`ps aux | grep "$jobName" | grep -v grep | awk '{print $2}'`  
if [[ "0$TAILPID" != "0" ]]; then
echo "${RED}kill process $TAILPID${NOCOLOR}"
sudo kill -9 $TAILPID
fi


while getopts "l:v:o:" opt
do
   case "$opt" in
      l ) language="$OPTARG" ;;
      v ) videoPath="$OPTARG" ;;
      o ) outPath="$OPTARG" ;;
      t ) audotText="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

[[ -z  $videoPath ]] &&  echo -e "${RED}videoPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $outPath ]] &&  echo -e "${RED}outPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $language ]] &&  language="zh"
[[ -z  $audotText ]] &&  audotText="zh"


echo -e "${YELLOW}python3 $jobName  -v \"$videoPath\"  -l \"$language\" -o \"$outPath\"  -t \"$audotText\" ${NOCOLOR}"
python3 $jobName  -v "$videoPath" -l "$language" -o "$outPath" -t "$audotText"
