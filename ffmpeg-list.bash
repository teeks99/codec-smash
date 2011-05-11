repo=$1
ver=`lsb_release -c -s`

if [ "$repo" == "" ]; then
    echo Need to input the repo type/name as an argument
else
    
ffmpeg 2> ffmpeg-header-$ver-$repo.txt
ffmpeg -formats > ffmpeg-formats-$ver-$repo.txt
ffmpeg -codecs > ffmpeg-codecs-$ver-$repo.txt
ffmpeg -bsfs > ffmpeg-bsfs-$ver-$repo.txt
ffmpeg -protocols > ffmpeg-protocols-$ver-$repo.txt
ffmpeg -filters > ffmpeg-filters-$ver-$repo.txt
ffmpeg -pix_fmts > ffmpeg-pix_fmts-$ver-$repo.txt

fi
