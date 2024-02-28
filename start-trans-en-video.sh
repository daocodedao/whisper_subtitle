#!/bin/bash
# 翻译英文视频 为 中文视频

workdir=/data/work/aishowos/whisper_subtitle/
cd $workdir

. colors.sh


venvBinDir=venv/bin/
pythonPath={$workdir}{$venvBinDir}python
echo "Python path:  $pythonPath"

echo "${YELLOW}source venv/bin/activate${NOCOLOR}"
source venv/bin/activate

helpFunction()
{
   echo ""
   echo "Usage: $0  -v videoPath -i processId -r role"
   echo -e "\t-v video path"
   echo -e "\t-i process id"
   echo -e "\t-r role"
   exit 1 # Exit script after printing help
}


jobName=generate-trans-tts-video.py 
echo "${YELLOW}check $jobName pid${NOCOLOR}"
echo "ps aux | grep "$jobName" | grep -v grep  | awk '{print $2}'"
TAILPID=`ps aux | grep "$jobName" | grep -v grep | awk '{print $2}'`  
if [[ "0$TAILPID" != "0" ]]; then
echo "${RED}kill process $TAILPID${NOCOLOR}"
sudo kill -9 $TAILPID
fi


while getopts "v:i:r:" opt
do
   case "$opt" in
      v ) videoPath="$OPTARG" ;;
      i ) processId="$OPTARG" ;;
      r ) role="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

[[ -z  $videoPath ]] &&  echo -e "${RED}videoPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $processId ]] &&  echo -e "${RED}processId is empty ${NOCOLOR}" &&  exit 1
[[ -z  $role ]] && role="he"

echo -e "${YELLOW}{$workdir}{$venvBinDir}python3 $jobName  -v \"$videoPath\"   -i \"$processId\"  -r \"$role\" ${NOCOLOR}"
{$workdir}{$venvBinDir}python3 $jobName  -v "$videoPath" -i "$processId" -r "$role"
