#TODO: Set output file time to same as original file time

import subprocess
import os
import sys

archive_size_rates={'hd1080':'5000k', 'hd720':'2500k', 'hd480':'1500k', 'vga':'1500k', '720x480':'1500k', 'hd360':'625k', 'hd240':'300k'}

class Encode(object):
    def __init__(self, filename=""):
        self.file_name(filename)
        self.out_extension = '.mp4'
        
        self.offset = None
        self.duration = None
        
        self.deinterlace = True
        self.vcodec = 'libx264'
        self.preset = 'slower'
        self.vid_size('720x480')
        self.pix_fmt = 'yuv420p'
        self.mp4_faststart = True
        self.twopass = False
      
        self.use_crf = True
        self.crf = '18'
        
        self.acodec = 'libvo_aacenc'
        self.arate = '256k'      
        
        self.test_run = False

    def vid_size(self, size):
        self.vsize = size
        self.vrate = archive_size_rates[size]
        
    def file_name(self, name):
        self.in_filename = name
        self.out_filename, old_extension = os.path.splitext(name)
    
    def encode(self):
        if not self.twopass:
	    self._single_pass()  
	else:
	    self._two_pass()

    def _add_infile(self):
        self.runline += '-i ' + '"' + self.in_filename + '" ' 	
        
    def _add_section(self):
        if self.offset:
            self.runline += '-ss ' + self.offset + ' '
        if self.duration:
	    self.runline += '-t ' + self.duration + ' '
        
    def _add_video(self):
        self.runline += '-c:v ' + self.vcodec + ' ' 
        if self.vcodec == 'libx264':
            self.runline += '-preset ' + self.preset + ' '
        self.runline += '-s ' + self.vsize + ' '
        if self.use_crf:
	    self.runline += '-crf ' + self.crf + ' '
	else:
	    self.runline += '-b:v ' + self.vrate + ' '
	    
        if self.deinterlace:
	    self.runline += '-deinterlace '

    def _add_audio(self):
        self.runline += '-c:a ' + self.acodec + ' '
        self.runline += '-b:a ' + self.arate + ' '
                        
    def _add_output(self):
        if self.out_extension == '.mp4' and self.mp4_faststart:
	    self.runline += '-movflags +faststart '
        
        filename = self.out_filename + self.out_extension
        self._delete_if_exists(filename)
        
        self.runline += '"' + filename + '"'
        
    def _delete_if_exists(self, filename):
        if os.path.isfile(filename):
           os.remove(filename)
	    
    def _single_pass(self):
        self.runline = 'ffmpeg '
        self._add_infile()
        self._add_section()
        self._add_video()
        self._add_audio()
        self._add_output()
        
        self._execute()
        
    def _two_pass(self):
        pass
        
    def _execute(self):
        print("running: " + self.runline)
        if not self.test_run:
	    self.ret_code = subprocess.call(self.runline, shell=True)
        
if __name__ == "__main__":
    proj = Encode(sys.argv[1])
    proj.encode()
        