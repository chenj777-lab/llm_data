export KWS_SERVICE_AZ=HB2AZ1 #或HB2AZ2 #取决于机器所在位置
export KWS_SERVICE_REGION=HB2
export KWS_SERVICE_DC=WLF1 #或 WLF2 #取决于机器所在位置
export KWS_SERVICE_NAME=ai-platform-dense-server
export KWS_SERVICE_CATALOG=ai-platform.ksnserver.dense-server
export KWS_SERVICE_STAGE=PROD
infn=$1
outfn=$2
python3 landing_page.py $infn $outfn
