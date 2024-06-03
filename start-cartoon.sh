#!/bin/bash
# 翻译英文视频 为 中文视频

workdir=/data/work/aishowos/whisper_subtitle/
cd $workdir

. colors.sh


venvBinDir=venv/bin/
pythonPath=${workdir}${venvBinDir}python
echo "Python path:  $pythonPath"

echo "${YELLOW}source ${venvBinDir}activate${NOCOLOR}"
source ${venvBinDir}activate

helpFunction()
{
   echo ""
   echo "Usage: $0  -v videoPath -i processId -a noadd -u noupload"
   echo -e "\t-v video path"
   echo -e "\t-i process id"
   echo -e "\t-a add voice, value: add, noadd"
   echo -e "\t-u upload cloud, value: upload, noupload"
   exit 1 # Exit script after printing help
}


jobName=utilCartoon.py 
echo "${YELLOW}check $jobName pid${NOCOLOR}"
echo "ps aux | grep "$jobName" | grep -v grep  | awk '{print $2}'"
TAILPID=`ps aux | grep "$jobName" | grep -v grep | awk '{print $2}'`  
if [[ "0$TAILPID" != "0" ]]; then
echo "${RED}kill process $TAILPID${NOCOLOR}"
sudo kill -9 $TAILPID
fi


while getopts "v:i:a:u:" opt
do
   case "$opt" in
      v ) videoPath="$OPTARG" ;;
      i ) processId="$OPTARG" ;;
      a ) addVoice="$OPTARG" ;;
      u ) uploadTos="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

[[ -z  $videoPath ]] &&  echo -e "${RED}videoPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $processId ]] &&  echo -e "${RED}processId is empty ${NOCOLOR}" &&  exit 1
[[ -z  $addVoice ]] &&  addVoice="noAdd"
[[ -z  $uploadTos ]] &&  uploadTos="noUpload"


echo -e "${YELLOW}${pythonPath} $jobName  -v '$videoPath' -i '$processId' -a '$addVoice'  -u '$uploadTos'${NOCOLOR}"
${pythonPath} $jobName  -v "$videoPath" -i "$processId" -a "$addVoice"  -u "$uploadTos"

