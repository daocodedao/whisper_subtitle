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
   echo "Usage: $0  -v videoPath -i processId -r role -b add -t 'translate' -c "noCartoon""
   echo -e "\t-v video path"
   echo -e "\t-i process id"
   echo -e "\t-r role"
   echo -e "\t-b is add bgMusic"
   echo -e "\t-t is need translate"
   echo -e "\t-c is need cartoon"
   echo -e "\t-u is need cut no human voice parts"
   exit 1 # Exit script after printing help
}


jobName=generateTransTtsVideo.py 
echo "${YELLOW}check $jobName pid${NOCOLOR}"
echo "ps aux | grep "$jobName" | grep -v grep  | awk '{print $2}'"
TAILPID=`ps aux | grep "$jobName" | grep -v grep | awk '{print $2}'`  
if [[ "0$TAILPID" != "0" ]]; then
echo "${RED}kill process $TAILPID${NOCOLOR}"
sudo kill -9 $TAILPID
fi


while getopts "v:i:r:b:t:c:u:" opt
do
   case "$opt" in
      v ) videoPath="$OPTARG" ;;
      i ) processId="$OPTARG" ;;
      r ) role="$OPTARG" ;;
      b ) isAddBgMusic="$OPTARG" ;;
      t ) isNeedTranslate="$OPTARG" ;;
      c ) isNeedCartoon="$OPTARG" ;;
      u ) cutNoHumanVoiceThreshold="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

[[ -z  $videoPath ]] &&  echo -e "${RED}videoPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $processId ]] &&  echo -e "${RED}processId is empty ${NOCOLOR}" &&  exit 1
[[ -z  $role ]] && role="he"
[[ -z  $isAddBgMusic ]] && isAddBgMusic="add"
[[ -z  $isNeedTranslate ]] && isNeedTranslate="translate"
[[ -z  $isNeedCartoon ]] && isNeedCartoon="noCartoon"
[[ -z  $cutNoHumanVoiceThreshold ]] && cutNoHumanVoiceThreshold=0


echo -e "${YELLOW}${pythonPath} $jobName  -v '$videoPath'   -i '$processId'  -r '$role' -b '$isAddBgMusic'   -t '$isNeedTranslate' -c '$isNeedCartoon' -u '$cutNoHumanVoiceThreshold' ${NOCOLOR}"
${pythonPath} $jobName  -v "$videoPath" -i "$processId" -r "$role"  -b "$isAddBgMusic" -t "$isNeedTranslate" -c "$isNeedCartoon" -u "$cutNoHumanVoiceThreshold"
