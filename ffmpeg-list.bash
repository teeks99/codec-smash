repo=$1
ver=`lsb_release -c -s`
dir=ffmpeg-features-$ver-$repo

if [ "$repo" == "" ]; then
    echo Need to input the repo type/name as an argument
else
    

mkdir $dir
ffmpeg 2> $dir/header.txt
ffmpeg -formats > $dir/formats.txt
ffmpeg -codecs > $dir/codecs.txt
ffmpeg -bsfs > $dif/bsfs.txt
ffmpeg -protocols > $dir/protocols.txt
ffmpeg -filters > $dir/filters.txt
ffmpeg -pix_fmts > $dir/pix_fmts.txt

fi
