export KWS_SERVICE_AZ=HB2AZ1 #或HB2AZ2 #取决于机器所在位置
export KWS_SERVICE_REGION=HB2
export KWS_SERVICE_DC=WLF1 #或 WLF2 #取决于机器所在位置
export KWS_SERVICE_NAME=ai-platform-dense-server
export KWS_SERVICE_CATALOG=ai-platform.ksnserver.dense-server
export KWS_SERVICE_STAGE=PROD
infn=$1
outfn=$2
jobnum=$3
version=$4 #gpt4 or gpt3.5
num_lines=`cat $infn |wc -l`
nl=$((num_lines / jobnum + 1))
split -l $nl $infn ${infn}_ -d -a 2
for i in `seq -w 0 $((jobnum-1))` ; do (
  echo ${infn}_${i}
	#python gpt4_client.py ${infn} $outfn $version 
	python gpt4_client_askzhendui.py ${infn} $outfn $version 
) & 
done
wait
rm ${infn}_*
