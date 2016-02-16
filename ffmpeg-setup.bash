#!/bin/bash
# Builds ffmpeg, libx264, libvpx from git repos

# Set version numbers here...use DIST to indicate that you aren't building it and to use the repo version
ffmpeg_version=3.0
x264_version=DIST # 40bb56814e56ed342040bdbf30258aab39ee9e89
x265_version=1.9
vpx_version=1.5.0
aacplus_version=2.0.2

# Pause between sections
#PAUSE=False
PAUSE=True

sudo echo "" # this will ask you for your password immediately, should cache it for the rest of the process
sys_ver=`lsb_release -c -s`

# Don't do this stuff for now (top unreachable block)
if [ "A" = "B" ] ; then
  echo none
fi # End of top unrachable block

# ----- First Time Setup -----
# Build Stuff
pkg_build="git-core mercurial checkinstall yasm build-essential cmake texi2html pkg-config autoconf automake libtool unzip"

# IO and Misc
pkg_io=
pkg_io=$pkg_io" libvdpau-dev" # HW Accel
pkg_io=$pkg_io" libva-dev" # HW Accel
pkg_io=$pkg_io" libx11-dev libxfixes-dev" # Grab X11
pkg_io=$pkg_io" libsdl1.2-dev" # Grab video framebuffer
pkg_io=$pkg_io" libdc1394-22-dev" # Firewire grabbing
pkg_io=$pkg_io" libopenal-dev" # Audio IO
pkg_io=$pkg_io" libpulse-dev" # Audio IO
pkg_io=$pkg_io" libjack-jackd2-dev" # Connections to/from JACK sound server
pkg_io=$pkg_io" libv4l-dev" # Video 4 Linux Grabber(?)
pkg_io=$pkg_io" libbluray-dev" # Read a bluray unencrypted disk
pkg_io=$pkg_io" vflib3-dev" # font rasterizer
pkg_io=$pkg_io" libfontconfig-dev" # Get system fonts
pkg_io=$pkg_io" flite1-dev" # Speech Synthesis
pkg_io=$pkg_io" libbz2-dev" # deflate compression
pkg_io=$pkg_io" zlib1g-dev" # deflate compression
pkg_io=$pkg_io" frei0r-plugins-dev" # Filtering
pkg_io=$pkg_io" libcv-dev" # Open CV Filters+
pkg_io=$pkg_io" libfftw3-dev" # Fast Fourier Transform?
pkg_io=$pkg_io" librtmp-dev" # Streams over RTMP
# TODO: OpenCL? VDA?

pkg_enc=
# Subtitles
pkg_enc=$pkg_enc" libass-dev" # SubStation Alpha Subtitles
# Audio
pkg_enc=$pkg_enc" libmp3lame-dev" # MP3
pkg_enc=$pkg_enc" libtwolame-dev" # MP2
pkg_enc=$pkg_enc" libfdk-aac-dev" # AAC - best
pkg_enc=$pkg_enc" libfaac-dev" # AAC - next best
pkg_enc=$pkg_enc" libvo-aacenc-dev" # AAC - worst
if [ "$aacplus_version" == "DIST" ]; then
  pkg_enc=$pkg_enc" libaacplus-dev" # AAC Plus (not currently available)
fi
pkg_enc=$pkg_enc" libvorbis-dev" # Vorbis
pkg_enc=$pkg_enc" libspeex-dev" # Speek
pkg_enc=$pkg_enc" libopus-dev" # Opus
pkg_enc=$pkg_enc" libopencore-amrnb-dev libopencore-amrwb-dev" # Adaptive Multi-Rate
pkg_enc=$pkg_enc" libvo-amrwbenc-dev"  # Adaptive Multi-Rate
pkg_enc=$pkg_enc" libgsm1-dev" # # GSM 06.10
pkg_enc=$pkg_enc" libmodplug-dev" # MOD format
# Video
pkg_enc=$pkg_enc" libtheora-dev" # Theora
pkg_enc=$pkg_enc" libopenjpeg-dev" # JPEG2000
pkg_enc=$pkg_enc" libschroedinger-dev" # Schroedinger Dirac
pkg_enc=$pkg_enc" libxvidcore-dev" # XVid
if [ "$x264_version" == "DIST" ]; then
  pkg_enc=$pkg_enc" libx264-dev" # H.264
fi
if [ "$x265_version" == "DIST" ]; then 
  pkg_enc=$pkg_enc" libx265-dev" # H.265 (not currently available)
fi
if [ "$vpx_version" == "DIST" ]; then
  pkg_enc=$pkg_enc" libvpx-dev" # VP8 & VP9 (not currently sufficient version)
fi

#ffmpeg config options
cfg_opts=$cfg_opts" --enable-gpl --enable-version3 --enable-nonfree"
cfg_opts=$cfg_opts" --enable-runtime-cpudetect"
cfg_opts=$cfg_opts" --enable-vdpau --enable-vaapi --enable-vda"
#cfg_opts=$cfg_opts" --enable-opencl"
# Grab/Compress
cfg_opts=$cfg_opts" --enable-x11grab --enable-libdc1394"
cfg_opts=$cfg_opts" --enable-openal"
cfg_opts=$cfg_opts" --enable-libpulse"
cfg_opts=$cfg_opts" --enable-libv4l2"
cfg_opts=$cfg_opts" --enable-libbluray"
cfg_opts=$cfg_opts" --enable-libflite"
cfg_opts=$cfg_opts" --enable-bzlib --enable-zlib"
# Filters/etc
cfg_opts=$cfg_opts" --enable-frei0r"
cfg_opts=$cfg_opts" --enable-libfreetype"
cfg_opts=$cfg_opts" --enable-fontconfig"
#cfg_opts=$cfg_opts" --enable-libopencv"
cfg_opts=$cfg_opts" --enable-librtmp"
#cfg_opts=$cfg_opts" --enable-gnutls"
#cfg_opts=$cfg_opts" --enable-openssl"
# Subtitles
cfg_opts=$cfg_opts" --enable-libass"
# Audio
cfg_opts=$cfg_opts" --enable-libmp3lame"
cfg_opts=$cfg_opts" --enable-libtwolame"
cfg_opts=$cfg_opts" --enable-libfdk-aac"
cfg_opts=$cfg_opts" --enable-libfaac"
cfg_opts=$cfg_opts" --enable-libvo-aacenc"
if [ "$aacplus_version" != "NONE" ]; then
  cfg_opts=$cfg_opts" --enable-libaacplus"
fi
cfg_opts=$cfg_opts" --enable-libvorbis"
cfg_opts=$cfg_opts" --enable-libspeex"
cfg_opts=$cfg_opts" --enable-libopus"
cfg_opts=$cfg_opts" --enable-libopencore-amrnb --enable-libopencore-amrwb"
cfg_opts=$cfg_opts" --enable-libvo-amrwbenc"
cfg_opts=$cfg_opts" --enable-libgsm"
cfg_opts=$cfg_opts" --enable-libmodplug"
# Video
cfg_opts=$cfg_opts" --enable-libtheora"
cfg_opts=$cfg_opts" --enable-libopenjpeg"
cfg_opts=$cfg_opts" --enable-libschroedinger"
cfg_opts=$cfg_opts" --enable-libxvid"
if [ "$x264_version" != "NONE" ]; then
  cfg_opts=$cfg_opts" --enable-libx264"
fi
if [ "$x265_version" != "NONE" ]; then
  cfg_opts=$cfg_opts" --enable-libx265"
fi
if [ "$vpx_version" != "NONE" ]; then
  cfg_opts=$cfg_opts" --enable-libvpx"
fi
cfg_opts=$cfg_opts" "

cfg_opts=$cfg_opts" --extra-libs=-ldl" # Dynamic libc?

# Don't add
# --enable-avisynth - Windows only, requires vfw32
# --enable-libaacplus - not available on ubuntu?
# --enable-libcdio - something isn't right about the ubutu version "libavdevice/libcdio.c:26:23: fatal error: cdio/cdda.h: No such file or directory"
# --enable-libnut - needs to be built from source on ubuntu, there is a good nut muxer built in, I believe;
# --enable-libxavs - ??
# --enable-openssl - What is this for?

echo sudo apt-get -y install $pkg_build $pkg_io $pkg_enc
sudo apt-get -y install $pkg_build $pkg_io $pkg_enc

if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi

##################################################
if [ "$x264_version" != "DIST" ] && [ "$x264_version" != "NONE" ]
then
  echo "Build + Install x264"
  sudo apt-get -y remove libx264-dev

  if [ ! -d "x264" ]; then
    git clone git://git.videolan.org/x264.git
  fi
  pushd x264
  make distclean
  git fetch --all 
  git checkout $x264_version

  ./configure --enable-static
  make
  sudo checkinstall --pkgname=libx264-dev --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --default --fstrans=no #" - fix highlighting
  sleep 2s
  if [ "$PAUSE" = "True" ] ; then
    read -p "Press any key to continue... " -n1 -s
  fi
  popd
fi

###################################################
if [ "$x265_version" != "DIST" ] && [ "$x265_version" != "NONE" ]
then
  echo "Build + Install x265"
  sudo apt-get -y remove libx265-dev

  if [ ! -d "x265" ]; then
    hg clone https://bitbucket.org/multicoreware/x265
  fi
  pushd x265/build/linux
  hg pull
  hg up --clean $x265_version
  
  ./make-Makefiles.bash
  make clean
  
  make
  sudo checkinstall --pkgname=libx265-dev --pkgversion="1" --backup=no --deldoc=yes --default --fstrans=no #" - fix highlighting
  sleep 2s
  if [ "$PAUSE" = "True" ] ; then
    read -p "Press any key to continue... " -n1 -s
  fi
  popd
fi

##################################################
if [ "$vpx_version" != "DIST" ] && [ "$vpx_version" != "NONE" ]
then 
  echo "Build + Install libvpx"
  sudo apt-get -y remove libvpx-dev

  if [ ! -d "libvpx" ]; then
    git clone http://git.chromium.org/webm/libvpx.git
  fi
  pushd libvpx

  make clean
  git fetch -all
  git checkout v$vpx_version
  ./configure
  make
  vpx_version_num=`git describe`
  sudo checkinstall --pkgname=libvpx-dev --pkgversion="5:${vpx_version_num#v}" --backup=no --default --deldoc=yes --fstrans=no
  sleep 2s
  if [ "$PAUSE" = "True" ] ; then
    read -p "Press any key to continue... " -n1 -s
  fi
  popd
fi

###################################################
if [ "$aacplus_version" != "DIST" ] && [ "$aacplus_version" != "NONE" ]
then
  echo "Build + Install aacplus"
  sudo apt-get -y remove libaacplus-dev

  if [ ! -d "libaacplus-$aacplus_version" ]; then
    wget http://tipok.org.ua/downloads/media/aacplus/libaacplus/libaacplus-$aacplus_version.tar.gz
    #wget http://ffmpeg.gusari.org/uploads/libaacplus-$aacplus_version.tar.gz
    tar -xzf libaacplus-$aacplus_version.tar.gz
  fi
  pushd libaacplus-$aacplus_version
  ./autogen.sh --enable-shared --enable-static
  make
  sudo checkinstall --pkgname=libaacplus-dev --pkgversion="$aacplus_version" --backup=no --deldoc=yes --default --fstrans=no #" - fix highlighting
  sleep 2s
  if [ "$PAUSE" = "True" ] ; then
    read -p "Press any key to continue... " -n1 -s
  fi
  popd
fi

##################################################
echo "Build + Install ffmpeg"
sudo apt-get -y remove ffmpeg 

if [ ! -d "ffmpeg" ]; then  
  #git clone git://git.ffmpeg.org/ffmpeg.git
  #git clone git://git.videolan.org/ffmpeg.git
  git clone git://source.ffmpeg.org/ffmpeg.git
  #git clone git://git.libav.org/libav.git ffmpeg
fi 

pushd ffmpeg

make distclean
git fetch --all
git checkout n$ffmpeg_version

# Config options set at top of file
echo ./configure $cfg_opts
./configure $cfg_opts
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
make
sudo checkinstall --pkgname=ffmpeg --pkgversion="5:$ffmpeg_version" --backup=no --deldoc=yes --fstrans=no --default #" - fix highlighting
hash -r # Clears bash's paths to existing executables
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi

echo "qt-faststart seperate package"
make tools/qt-faststart
sudo checkinstall --pkgname=qt-faststart --pkgversion="$ffmpeg_version" --backup=no --deldoc=yes --fstrans=no --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart #" - fix highlighting
sleep 2s
if [ "$PAUSE" = "True" ] ; then
  read -p "Press any key to continue... " -n1 -s
fi
cd ..

# Make libraries live
sudo ldconfig

##################################################
echo "Re-Install ffmpeg, x264, or libvpx dependant stuff"
echo sudo apt-get install k9copy kdenlive recorditnow xvst

# Don't do this stuff for now (bottom unreachable block)
if [ "A" = "B" ] ; then

	echo none
fi # End of bottom unreachable block
