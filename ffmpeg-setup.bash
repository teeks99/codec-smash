#!/bin/bash
# Builds ffmpeg, libx264, libvpx from git repos
sudo echo "" # this will ask you for your password immediately, should cache it for the rest of the process
ver=`lsb_release -c -s`

# Don't do this stuff for now (top unreachable block)
if [ "A" = "B" ] ; then
  echo none
fi # End of top unrachable block

# ----- First Time Setup -----
echo "build pre-reqs"
sudo apt-get -y install git-core checkinstall yasm texi2html libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libsdl1.2-dev libtheora-dev libvorbis-dev libx11-dev libxfixes-dev libxvidcore-dev zlib1g-dev
echo "other lib pre-reqs"
sudo apt-get -y install frei0r-plugins-dev libdc1394-22 libdc1394-22-dev libgsm1 libgsm1-dev libopenjpeg-dev libschroedinger-1.0-0 libschroedinger-dev libschroedinger-doc libspeex-dev libvdpau-dev vflib3-dev
echo "version specific pre-reqs"
case $ver in
  lucid)
    echo none
  ;;
  maverick | natty | oneiric)
    sudo apt-get -y install librtmp-dev libva-dev
    # OpenCV
    sudo apt-get -y install libcv2.1 libcv-dev libcvaux2.1 libcvaux-dev libhighgui2.1 libhighgui-dev opencv-doc python-opencv
  ;;
esac

repoLocation=none # Already setup
#repoLocation=canonical # The authoritive sources
#repoLocation=jp2-s1

# Choose which repo set to use
case $repoLocation in

  canonical)
echo "Setup repos from canocial sources"
git clone git://git.videolan.org/x264.git
#git clone git://review.webmproject.org/libvpx.git
git clone http://git.chromium.org/webm/libvpx.git
#git clone git://git.ffmpeg.org/ffmpeg.git
git clone git://git.videolan.org/ffmpeg.git
#git clone git://git.libav.org/libav.git
  ;;

  jp2-s1)
echo "Setup repos from jp2-s1"
git clone http://jp2-s1/src/x264.git
git clone http://jp2-s1/src/libvpx.git
git clone http://jp2-s1/src/ffmpeg.git
#git clone http://jp2-s1/src/libav.git
  ;;

  none)
echo "no git clone commands"
  ;;
esac

# ----- Each Time -----
echo "Cleanup from last time, or remove repo versions"
sudo apt-get -y remove ffmpeg 
sudo apt-get -y remove x264 
sudo apt-get -y remove libx264-dev 
sudo apt-get -y remove libvpx 
sudo apt-get -y remove libvpx-dev

echo "Cleanup any source trees that have been built before"
cd x264;   make distclean; git checkout master; git pull; cd ..
cd libvpx; make clean;     git checkout master; git pull; cd ..
cd ffmpeg; make distclean; git checkout master; git pull; cd ..
#cd libav; make distclean; git checkout master; git pull; cd ..

echo "Go to the correct GIT Versions"
# Sixth Version - Feb 9, 2012
cd x264;   git checkout da19765d723b06a1fa189478e9da61a1c18490f8; cd .. # TBM, AVX2, FMA3, BMI1, and...
cd libvpx; git checkout v1.0.0; cd .. #2b0aee4b5def280d4e27c11d1b95ecd8545eed34 # Update CHANGEL...
cd ffmpeg; git checkout n0.10; cd .. #7e16636995fd6710164f7622cd77abc94c27a064 # doc: remove doc/f...


sleep 5s

##################################################
echo "Build + Install x264"
cd x264
./configure --enable-static
make
case $ver in
  lucid)
sudo checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --default 
  ;;
  maverick | natty | oneiric)
sudo checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --default --fstrans=no
  ;;
esac
sleep 2s
cd ..

##################################################
echo "Build + Install libvpx"
cd libvpx
./configure
make
case $ver in
  lucid)
sudo checkinstall --pkgname=libvpx --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --default --deldoc=yes
  ;;
  maverick | natty | oneiric)
sudo checkinstall --pkgname=libvpx --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --default --deldoc=yes --fstrans=no
  ;;
esac
sleep 2s
cd ..

##################################################
echo "Build + Install ffmpeg"
cd ffmpeg
#cd libav

#ffmpeg config options, missing --enable-libopencv
config_options="--enable-gpl --enable-version3 --enable-nonfree --enable-postproc --enable-x11grab --enable-vdpau --enable-bzlib --enable-pthreads --enable-zlib --enable-runtime-cpudetect --enable-frei0r --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libdc1394 --enable-libfaac --enable-libfreetype --enable-libgsm --enable-libmp3lame --enable-libopenjpeg --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libxvid"
case $ver in
  lucid)
echo nothing
  ;;
  maverick | natty)
config_options=$config_options" --enable-vaapi --enable-librtmp" #Temp disable opencv --enable-libopencv"
  ;;
  oneiric)
config_options=$config_options" --enable-vaapi --enable-librtmp --enable-libopencv"
  ;;
esac
# Stuff to add? --enable-libvo-aacenc --enable-libvo-amrwbenc ...in natty???
# Don't add 
# --enable-avisynth - Windows only, requires vfw32
# --enable-libnut - needs to be built from source on ubuntu, there is a good nut muxer built in, I believe; 

./configure $config_options
make
case $ver in
  lucid)
sudo checkinstall --pkgname=ffmpeg --pkgversion="5:$(./version.sh)" --backup=no --deldoc=yes --default
  ;;
  maverick | natty | oneiric)
sudo checkinstall --pkgname=ffmpeg --pkgversion="5:$(./version.sh)" --backup=no --deldoc=yes --fstrans=no --default
  ;;
esac
hash x264 ffmpeg ffplay ffprobe
sleep 2s

echo "qt-faststart seperate package"
make tools/qt-faststart
case $ver in
  lucid)
sudo checkinstall --pkgname=qt-faststart --pkgversion="$(./version.sh)" --backup=no --deldoc=yes --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart  
  ;;
  maverick | natty | oneiric)
sudo checkinstall --pkgname=qt-faststart --pkgversion="$(./version.sh)" --backup=no --deldoc=yes --fstrans=no --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart
  ;;
esac
sleep 2s
cd ..

##################################################
echo "Re-Install ffmpeg, x264, or libvpx dependant stuff"
echo sudo apt-get install dvdrip k9copy kdenlive

# Don't do this stuff for now (bottom unreachable block)
if [ "A" = "B" ] ; then

	echo none
fi # End of bottom unreachable block
