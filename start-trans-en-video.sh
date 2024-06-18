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


while getopts "v:i:r:b:t:c:u:k:" opt
do
   case "$opt" in
      v ) videoPath="$OPTARG" ;;
      i ) processId="$OPTARG" ;;
      r ) role="$OPTARG" ;;
      b ) isAddBgMusic="$OPTARG" ;;
      t ) isNeedTranslate="$OPTARG" ;;
      c ) isNeedCartoon="$OPTARG" ;;
      u ) cutNoHumanVoiceThreshold="$OPTARG" ;;
      k ) replaceKeyWorkTxtFilePath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

cmd="${pythonPath} $jobName"

[[ -z  $videoPath ]] &&  echo -e "${RED}videoPath is empty ${NOCOLOR}" &&  exit 1
[[ -z  $processId ]] &&  echo -e "${RED}processId is empty ${NOCOLOR}" &&  exit 1
cmd="${cmd} -v $videoPath -i $processId "

[[ -z  $role ]] && role="he"
cmd="${cmd} -r $role "

[[ -z  $isAddBgMusic ]] && isAddBgMusic="add"
cmd="${cmd} -b $isAddBgMusic "

[[ -z  $isNeedTranslate ]] && isNeedTranslate="translate"
cmd="${cmd} -t $isNeedTranslate "

[[ -z  $isNeedCartoon ]] && isNeedCartoon="noCartoon"
cmd="${cmd} -c $isNeedCartoon "

[[ -z  $cutNoHumanVoiceThreshold ]] && cutNoHumanVoiceThreshold=0
cmd="${cmd} -u $cutNoHumanVoiceThreshold "

[[ -n $replaceKeyWorkTxtFilePath ]] && cmd="${cmd} -k $replaceKeyWorkTxtFilePath "



echo -e "${YELLOW}${cmd}${NOCOLOR}"
${cmd}

# echo -e "${YELLOW}${pythonPath} $jobName  -v '$videoPath'   -i '$processId'  -r '$role' -b '$isAddBgMusic'   -t '$isNeedTranslate' -c '$isNeedCartoon' -u '$cutNoHumanVoiceThreshold' ${NOCOLOR}"
# ${pythonPath} $jobName  -v "$videoPath" -i "$processId" -r "$role"  -b "$isAddBgMusic" -t "$isNeedTranslate" -c "$isNeedCartoon" -u "$cutNoHumanVoiceThreshold"
