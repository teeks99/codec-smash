#!/bin/bash
# Builds ffmpeg, libx264, libvpx from git repos

# Choose which repo set to use
#repoLocation=none # Already setup
repoLocation=canonical # The authoritive sources
#repoLocation=jp2-s1
#repoLocation=YourServerName.com

# Pause between sections
PAUSE=False
#PAUSE=True

sudo echo "" # this will ask you for your password immediately, should cache it for the rest of the process
sys_ver=`lsb_release -c -s`

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
case $sys_ver in
  lucid)
    echo none
  ;;
  maverick | natty | oneiric)
    sudo apt-get -y install librtmp-dev libva-dev
    # OpenCV
    sudo apt-get -y install libcv2.1 libcv-dev libcvaux2.1 libcvaux-dev libhighgui2.1 libhighgui-dev opencv-doc python-opencv
  ;;
  precise)
    sudo apt-get -y install librtmp-dev libva-dev libjack-jackd2-dev libass4 libass-dev  libmodplug1 libmodplug-dev libvo-aacenc0 libvo-aacenc-dev libvo-amrwbenc0 libvo-amrwbenc-dev libopenal1 libopenal-dev
    sudo apt-get -y install libcv2.3
  ;;
  quantal | raring | saucy)
    sudo apt-get -y install librtmp-dev libva-dev libjack-jackd2-dev libass4 libass-dev  libmodplug1 libmodplug-dev libvo-aacenc0 libvo-aacenc-dev libvo-amrwbenc0 libvo-amrwbenc-dev libopenal1 libopenal-dev yasm
    sudo apt-get -y install libcv2.3
    sudo apt-get -y install libbluray-dev libbluray1 libv4l-0 libv4l-dev flite1-dev libflite1 libopus-dev libopus0 libtwolame-dev libtwolame0 
esac

if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi



case $repoLocation in

  canonical)
echo "Setup repos from canocial sources"
git clone git://git.videolan.org/x264.git
#git clone git://review.webmproject.org/libvpx.git
git clone http://git.chromium.org/webm/libvpx.git
#git clone git://git.ffmpeg.org/ffmpeg.git
#git clone git://git.videolan.org/ffmpeg.git
git clone git://source.ffmpeg.org/ffmpeg.git
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
cd x264;   git checkout d6b4e63d2ed8d444b77c11b36c1d646ee5549276; cd .. # Macroblock tree overhaul/optimization
cd libvpx; git checkout v1.3.0; cd ..
cd ffmpeg; git checkout n2.2.1; cd ..

sleep 5s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi

##################################################
echo "Build + Install x264"
cd x264
./configure --enable-static
make
case $sys_ver in
  lucid)
sudo checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --default #" - fix highlighting
  ;;
  maverick | natty | oneiric | precise | quantal | raring | saucy)
sudo checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --default --fstrans=no #" - fix highlighting
  ;;
esac
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
cd ..

##################################################
echo "Build + Install libvpx"
cd libvpx
./configure
make
case $sys_ver in
  lucid)
sudo checkinstall --pkgname=libvpx --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --default --deldoc=yes
  ;;
  maverick | natty | oneiric | precise | quantal | raring | saucy)
sudo checkinstall --pkgname=libvpx --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --default --deldoc=yes --fstrans=no
  ;;
esac
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
cd ..

##################################################
echo "Build + Install ffmpeg"
cd ffmpeg
#cd libav

#ffmpeg config options
config_options=$config_options" --enable-gpl --enable-version3 --enable-nonfree --enable-x11grab --enable-vdpau --enable-runtime-cpudetect"
config_options=$config_options" --enable-bzlib --enable-frei0r --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libdc1394 --enable-libfaac --enable-libfreetype --enable-libgsm --enable-libmp3lame --enable-libopenjpeg --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libxvid --enable-zlib"
case $sys_ver in
  lucid)
echo nothing
  ;;
  maverick | natty)
    config_options=$config_options" --enable-vaapi --enable-librtmp" #Temp disable opencv --enable-libopencv"
  ;;
  oneiric)
    config_options=$config_options" --enable-vaapi --enable-librtmp --enable-libopencv"
  ;;
  precise)
    config_options=$config_options" --enable-vaapi --enable-vda"  
    config_options=$config_options" --enable-gnutls --enable-libass --enable-libmodplug --enable-libpulse --enable-librtmp --enable-libvo-aacenc --enable-libvo-amrwbenc --enable-openal" #--enable-libopencv
  ;;
  quantal | raring | saucy)
    config_options=$config_options" --enable-vaapi --enable-vda"  
    config_options=$config_options" --enable-fontconfig --enable-gnutls --enable-libass --enable-libbluray --enable-libflite --enable-libmodplug --enable-libopus --enable-libpulse --enable-librtmp --enable-libtwolame --enable-libv4l2 --enable-libvo-aacenc --enable-libvo-amrwbenc --enable-openal" #--enable-libopencv
    config_options=$config_options" --extra-libs=-ldl"
  ;;
esac
# Stuff to add? --enable-libvo-aacenc --enable-libvo-amrwbenc ...in natty???
# Don't add 
# --enable-avisynth - Windows only, requires vfw32
# --enable-libaacplus - not available on ubuntu?
# --enable-libcdio - something isn't right about the ubutu version "libavdevice/libcdio.c:26:23: fatal error: cdio/cdda.h: No such file or directory"
# --enable-libnut - needs to be built from source on ubuntu, there is a good nut muxer built in, I believe; 
# --enable-libxavs - ??
# --enable-openssl - What is this for?

echo ./configure $config_options
./configure $config_options
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
make
case $sys_ver in
  lucid)
sudo checkinstall --pkgname=ffmpeg --pkgversion="5:$(./version.sh)" --backup=no --deldoc=yes --default #" - fix highlighting
  ;;
  maverick | natty | oneiric | precise | quantal | raring | saucy)
sudo checkinstall --pkgname=ffmpeg --pkgversion="5:$(./version.sh)" --backup=no --deldoc=yes --fstrans=no --default #" - fix highlighting
  ;;
esac
hash x264 ffmpeg ffplay ffprobe
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi

echo "qt-faststart seperate package"
make tools/qt-faststart
case $sys_ver in
  lucid)
sudo checkinstall --pkgname=qt-faststart --pkgversion="$(./version.sh)" --backup=no --deldoc=yes --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart  #" - fix highlighting
  ;;
  maverick | natty | oneiric | precise | quantal | raring | saucy)
sudo checkinstall --pkgname=qt-faststart --pkgversion="$(./version.sh)" --backup=no --deldoc=yes --fstrans=no --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart #" - fix highlighting
  ;;
esac
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
cd ..

##################################################
echo "Re-Install ffmpeg, x264, or libvpx dependant stuff"
echo sudo apt-get install k9copy kdenlive recorditnow xvst

# Don't do this stuff for now (bottom unreachable block)
if [ "A" = "B" ] ; then

	echo none
fi # End of bottom unreachable block
