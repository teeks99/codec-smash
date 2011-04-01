#!/bin/python
'''This will run tests of various ffmpeg codecs, bitrates, options, etc

This will iterate through multiple tests with multiple different codecs and options and give you 
retults.html when you're done.

This test is strictly single threaded, as some of the codecs will utilize multiple processors if they are available, thus we want to only run one test at a time (so we don't get two multi-processor tests at the same time, competing for CPU).
'''

#TODO:
# - Load inputs as JSON
# - Command line arguments
# - CPU time
# - Allow for cropping of images
# - Put images together into a video (write the name of the file on each image)
# - Concatenate all the videos for each test into one with text between clips (reach goal)
# - Option to skip conversion (output file must already be in place)
# - Write pretty sizes of files

# Here you can enter files that you want to test out
# For some you may want to specify a seperate video and audio file to both be processed.  Follow the sintel example for that.
# You can also specify points in the output file (in seconds) to record a png image, so quality can be looked at without running each video.
test_input_files=[
{"name":"PieTest","files":["PieTest.mkv"],"image_points":[{'sec':"3",'w':'640','h':'480','x':'480','y':'100'},{'sec':"12",'w':'640','h':'480','x':'480','y':'100'}]}
#, {"name":"sintel_clip","files":["sintel_clip.y4m","sintel_clip.flac"],"image_points":["2","5","7","9.560"]}
#, {"name":"sintel_trailer","files":["sintel_trailer-video.y4m", "sintel_trailer-audio.flac"], "image_points":["3","15"]}
]

# Here's some variables that can be used in the tests section
thirteen_rates=["100", "250", "500", "750", "1000", "2000", "3000", "5000", "7500", "10000", "12500", "15000", "20000"]
five_rates=["750", "1000", "3000", "5000", "10000"]
two_rates=["1000", "5000"]
standard_rates=two_rates
default_audio="-acodec libfaac -ab 192k"
low_audio="-acodec libvorbis -ab 64k"
no_audio="-an"

seven_audio_rates=["64", "96", "128", "192", "256", "320", "512"]
three_audio_rates=["128", "192", "256"]
standard_audio_rates=three_audio_rates
default_video="-vcodec mpeg4 -b 500k"
low_video="-vcodec mpeg4 -b 100k"
no_video="-vn"

manual_threads=str(4) # -threads 0 doesn't work for some codecs like libx264

# Here you may enter tests.  Each test may have additional variables that will be iterated over to create sub-tests.  
#INPUT_FILES is the group of files to be added in "-i name1 -i name2" format
#INPUT_NAME is a special variable, from test_input_files[x]["name"], please no spaces
tests=[
{"title":"original","commands":
["ffmpeg INPUT_FILES -vcodec copy -acodec copy INPUT_NAME-original.mkv"],
"output":"INPUT_NAME-original.mkv"},

{"title":"x264-2p-rates","commands":
["ffmpeg INPUT_FILES -pass 1 -vcodec libx264 -vpre PRESET_firstpass -b RATEk -bt RATEk -an -threads " + manual_threads + " -f rawvideo -y /dev/null", 
"ffmpeg INPUT_FILES -pass 2 -vcodec libx264 -vpre PRESET -b RATEk -bt RATEk " + default_audio + " -threads " + manual_threads + " INPUT_NAME-x264-PRESET-RATE-2p.mkv"],
"output":"INPUT_NAME-x264-PRESET-RATE-2p.mkv",
"variables":[
{"name":"PRESET","values":["medium", "slow", "fast"]},
{"name":"RATE","values":thirteen_rates}
]},

{"title":"x264-2p-fancy_presets","commands":
["ffmpeg INPUT_FILES -pass 1 -vcodec libx264 -vpre PRESET_firstpass -b RATEk -bt RATEk -an -threads " + manual_threads + " -f rawvideo -y /dev/null", 
"ffmpeg INPUT_FILES -pass 2 -vcodec libx264 -vpre PRESET -b RATEk -bt RATEk " + default_audio + " -threads " + manual_threads + " INPUT_NAME-x264-PRESET-RATE-2p.mkv"],
"output":"INPUT_NAME-x264-PRESET-RATE-2p.mkv",
"variables":[
{"name":"PRESET","values":["faster", "slower", "superfast", "ultrafast", "veryfast", "veryslow"]},
{"name":"RATE","values":two_rates}
]},

{"title":"x264-1p-rates","commands":
["ffmpeg INPUT_FILES -vcodec libx264 -vpre PRESET -b RATEk -bt RATEk " + default_audio + " -threads " + manual_threads + " INPUT_NAME-x264-PRESET-RATE-1p.mkv"],
"output":"INPUT_NAME-x264-PRESET-RATE-1p.mkv",
"variables":[
{"name":"PRESET","values":["medium", "slow", "fast"]},
{"name":"RATE","values":thirteen_rates}
]},

{"title":"x264-1p-fancy_presets","commands":
["ffmpeg INPUT_FILES -vcodec libx264 -vpre PRESET -b RATEk -bt RATEk " + default_audio + " -threads " + manual_threads + " INPUT_NAME-x264-PRESET-RATE-1p.mkv"],
"output":"INPUT_NAME-x264-PRESET-RATE-1p.mkv",
"variables":[
{"name":"PRESET","values":["faster", "slower", "superfast", "ultrafast", "veryfast", "veryslow"]},
{"name":"RATE","values":two_rates}
]},

{"title":"x264-lossless","commands":
["ffmpeg INPUT_FILES -vcodec libx264 -vpre PRESET " + default_audio + " -threads " + manual_threads + " INPUT_NAME-x264-PRESET.mkv"],
"output":"INPUT_NAME-x264-PRESET.mkv",
"variables":[
{"name":"PRESET","values":["lossless_fast", "lossless_max", "lossless_medium", "lossless_slower", "lossless_slow", "lossless_ultrafast"]}
]},


# snow doesn't seem to work with the Pie or Sintel clips.  It complains about pixel formats and gives up.
# msmpeg4v1 looks like it works, but all the files only have audio in them (no video)
# h263 has limited size options: 128x96, 176x144, 352x288, 704x576, and 1408x1152, none of which we're using here.  It refers to H.263+, but I'm not sure what that is.
# wmv2 fails 2-pass because bitrate (even 10MB/s) is too low
# libxvid works for the Pie but not for Sintel, says it has a bad pixel ratio 0/1
{"title":"simple-1p","commands":
["ffmpeg INPUT_FILES -vcodec CODEC -b RATEk " + default_audio + " -threads 0 INPUT_NAME-CODEC-RATE-1p.mkv"],
"output":"INPUT_NAME-CODEC-RATE-1p.mkv",
"variables":[
{"name":"CODEC","values":["flv", "h263", "libschroedinger", "libtheora", "libvpx", "libxvid", "mjpeg", "mpeg2video", "mpeg4", "msmpeg4", "msmpeg4v1", "msmpeg4v2", "snow", "wmv2" ]},
{"name":"RATE","values":five_rates}]},

{"title":"simple-2p","commands":
["ffmpeg INPUT_FILES -pass 1 -vcodec CODEC -b RATEk -bt RATEk -an -threads 0 -f rawvideo -y /dev/null",
"ffmpeg INPUT_FILES -pass 2 -vcodec CODEC -b RATEk " + default_audio + " -threads 0 INPUT_NAME-CODEC-RATE-2p.mkv"],
"output":"INPUT_NAME-CODEC-RATE-2p.mkv",
"variables":[
{"name":"CODEC","values":["flv", "h263", "libschroedinger", "libtheora", "libvpx", "libxvid", "mjpeg", "mpeg2video", "mpeg4", "msmpeg4", "msmpeg4v1", "msmpeg4v2", "wmv2" ]},
{"name":"RATE","values":five_rates}]},

{"title":"lossless","commands":
["ffmpeg INPUT_FILES -vcodec CODEC " + default_audio + " -threads 0 INPUT_NAME-CODEC-lossless.mkv"],
"output":"INPUT_NAME-CODEC-lossless.mkv",
"variables":[
{"name":"CODEC","values":["ffv1", "ffvhuff", "huffyuv"]}
]},

# aac causes the application to crap out so it has been removed
# vorbis cause the application to crap out so it has been removed
{"title":"audio","commands":
["ffmpeg INPUT_FILES " + no_video + " -acodec CODEC -ab RATEk -threads 0 INPUT_NAME-CODEC-RATE.mkv"],
"output":"INPUT_NAME-CODEC-RATE.mkv",
"variables":[
{"name":"CODEC","values":["ac3", "libfaac", "libmp3lame", "libvorbis", "wmav2"]},
{"name":"RATE","values":seven_audio_rates}]},

{"title":"low-rate-audio","commands":
["ffmpeg INPUT_FILES " + no_video + " -acodec CODEC -ar 8000 -ac 1 -ab RATEk -threads 0 INPUT_NAME-CODEC-low_rate-RATE.mkv"],
"output":"INPUT_NAME-CODEC-low_rate-RATE.mkv",
"variables":[
{"name":"CODEC","values":["g722", "g726", "libgsm", "libgsm_ms", "libmp3lame", "libopencore_amrnb", "libvorbis"]},
{"name":"RATE","values":["6.7", "12.2", "13", "32", "48", "64"]}]},

{"title":"lossless-audio","commands":
["ffmpeg INPUT_FILES " + no_video + " -acodec CODEC -threads 0 INPUT_NAME-CODEC-lossless.mkv"],
"output":"INPUT_NAME-CODEC-lossless.mkv",
"variables":[
{"name":"CODEC","values":["flac", "pcm_s16be"]} #pcm_s16be is CD-audio format
]},

# This needs to be sepearted out to use the m4a container, since it won't work in mkv (why not???)
{"title":"lossless-audio-alac","commands":
["ffmpeg INPUT_FILES " + no_video + " -acodec CODEC -threads 0 INPUT_NAME-CODEC-lossless.m4a"],
"output":"INPUT_NAME-CODEC-lossless.m4a",
"variables":[
{"name":"CODEC","values":["alac"]}
]}
]

import os.path
from subprocess import call
import time
import shlex

def variable_combinations(variables):
    """ Finds all possible combinations of the variables
    
    Input format is a list with dictionaries for each variable (which contains a list of all
    possible values) of the format:
    [{'name':'name1','values':['value1','value2','etc.']},
    {'name':'name2','values':['value1','value2','etc.']},
    {'name':'name3','values':['value1','value2','etc.']}]

    This will run recursively to match up all the possible combinations of variables, and 
    return them in a list of dictionaries with "name":"value" pairs for each variable in 
    each dictionary. 
    The returned format will be:
    [{'name1':'value1','name2':'value1','name3':'value1'},
    {'name1':'value1','name2':'value1','name3':'value2'},
    ...
    {'name1':'value1','name2':'value1','name3':'valueX'},
    {'name1':'value1','name2':'value2','name3':'value1'},
    ...
    {'name1':'valueX','name2':'valueX','name3':'valueX'}]


    testcase
    input: [{'values': ['1', '2'], 'name': 'v1'}, {'values': ['3', '4'], 'name': 'v2'}, {'values': ['5', '6'], 'name': 'v3'}]
    output: [{'v1': '1', 'v2': '3', 'v3': '5'}, {'v1': '1', 'v2': '3', 'v3': '6'}, {'v1': '1', 'v2': '4', 'v3': '5'}, {'v1': '1', 'v2': '4', 'v3': '6'}, {'v1': '2', 'v2': '3', 'v3': '5'}, {'v1': '2', 'v2': '3', 'v3': '6'}, {'v1': '2', 'v2': '4', 'v3': '5'}, {'v1': '2', 'v2': '4', 'v3': '6'}]

    """
    combo = []
    if variables:
        var = variables[0]
        next_vars = variables[1:]
        next_combo = variable_combinations(next_vars)
        for val in var['values']:
            if next_combo:
               for c in next_combo:
                    tc = c.copy() # Othewise this would be overwritten in the next loop
                    tc[var['name']]=val
                    combo.append(tc)
            else:
                c={var['name']:val}
                combo.append(c)
    return combo

class TestPoints():
    def __init__(self, points, test_name):
        cmd = "mkdir -p img thumb frames"
        call(shlex.split(cmd))

        self.tp = {}
        self.test_name = test_name
        
        for point in points:
            if point.__class__ == "".__class__: # If points is just a list of strings for times
                self.tp[point] = {'sec':point}
                crop = {'w':'0','h':'0'}
                self.setup(self.tp[point], point, crop, test_name)
            elif point.__class__ == {}.__class__:
                pt = point['sec'] 
                self.tp[pt] = {"sec":pt}
                crop = {'w':point['w'],'h':point['h'],'x':point['x'],'y':point['y']}
                self.setup(self.tp[pt], pt, crop, test_name)

    def setup(self, p, point, crop, test_name):
        p['crop'] = crop
        p['title'] = test_name + "_" + point +  "s"
        p['file_name'] = p['title'] + ".html"

        p['file'] = open(p['file_name'], "w")

        p['file'].write("<html>\n<head><title>" + p['title'] + "</title></head>\n")
        p['file'].write("<body>\n")
        
    def html_segment(self):
        snip = ""
        for point,info in self.tp.items():
            snip += '<a href="' + self.test_name + "_" + point + 's.html">' + self.test_name + "_" + point + 's</a><br />\n'
        return snip

    def grab_points(self, video_file):
        thumbs = []
        for point in self.tp.values():
            # Use ffmpeg to make a single frame png
            cmd = 'ffmpeg -i ' + video_file + ' -an -ss ' + point['sec'] + ' -an -r 1 -vframes 1 -y %d.png' 
            call(shlex.split(cmd))

            img = 'img/' + video_file + "-" + point['sec'] + 's.png'
            # Move the output file to an appropriately named file in the img/ directory
            cmd = 'mv 1.png ' + img
            call(shlex.split(cmd))
            # Keep the full frame in the frames dir
            frm = 'frames/'  + video_file + "-" + point['sec'] + 's.png'
            cmd = 'cp ' + img + ' ' + frm
            call(shlex.split(cmd))

            # Make the img actually the cropped version
            try:
                w = point['crop']['w']
                h = point['crop']['h']
                if w!='0' and h!='0':
                    x = 0
                    y = 0
                    try:
                        x = point['crop']['x']
                    except KeyError:
                        pass
                    try:
                        y = point['crop']['y']
                    except KeyError:
                        pass
                cmd = 'mogrify -crop ' + w+'x'+h+'+'+x+'+'+y+' ' + img 
                call(shlex.split(cmd))
            except KeyError:
                pass

            thumb = 'thumb/' + video_file + "-" + point['sec'] + 's.png'
            # Create a thumbnail image in the thumb/ directory
            cmd = 'convert ' + img + ' -resize 100x100 ' + thumb
            call(shlex.split(cmd))

            thumbs.append({'img':img,'thumb':thumb})

            point['file'].write("<p>" + video_file + "<br />\n")
            point['file'].write('<img src="' + img + '">\n</p>')
            point['file'].flush()
        return thumbs

    def close(self):
        for point in self.tp.values():
            point['file'].write("</body>\n")
            point['file'].write("</html>\n")
            point['file'].close()

class FFMpegTester():
    def __init__(self):
        self.run_number = 0

    def run(self):
        self.run_tests()

    def start_html(self, name):
        self.results = open(name + ".html", "w")

        self.results.write("<html>\n<head><title>FFMpegTester Results</title></head>\n")
        self.results.write("<body>\n") 
        self.results.write("<p>\n")

        self.results.write(self.tps.html_segment())

        self.results.write("</p>\n")
        self.results.write('<table style="text-align: left; width: 100%;" border="1" ')
        self.results.write('cellpadding="2" cellspacing="2"><tbody>\n')
        self.results.write('  <tr>\n')
        self.results.write("   <td><b>No.</b></td>\n")
        self.results.write("   <td><b>Test Title</b></td>\n")
        self.results.write("   <td><b>Output</b></td>\n")
        self.results.write("   <td><b>Elapsed Time (wall clock)</b></td>\n")
        self.results.write("   <td><b>CPU Time</b></td>\n")
        self.results.write("   <td><b>File Size</b></td>\n")
        self.results.write("   <td><b>Example Images</b></td>\n")
        self.results.write("  </tr>\n")

    def finish_html(self):
        self.results.write("</tbody></table>\n</body>\n</html>\n")
        self.results.close()

    def run_tests(self):
        for infile in test_input_files:
            self.tps = TestPoints(infile['image_points'], infile['name'])
            self.start_html(infile['name'])
            self.current_input_file = infile
            input_name = infile['name']
            input_files = ""
            for item in infile['files']:
                input_files = input_files + " -i " + item
            for test in tests:
                self.current_test = test
                vc = ""
                try:
                    vc = variable_combinations(test['variables'])
                except KeyError:
                    vc = [{"":""}]
                for combo in vc:
                    self.current_combo = combo
                    # Append the special (and fixed) variables
                    combo['INPUT_NAME'] = input_name
                    combo['INPUT_FILES'] = input_files
                    cmds = test['commands'][:]
                    output = test['output']
                    for name, value in combo.items():
                        output = output.replace(name, value)
                        for val in range(len(cmds)):
                            cmds[val] = cmds[val].replace(name, value)
                    self.run_test_version(cmds, output)
            self.tps.close()
            self.finish_html()

    def run_test_version(self, cmds, output):
        print "Starting: " + output
        self.results.write("  <tr>\n")
        self.run_number += 1
        self.results.write("   <td>" + str(self.run_number) + "</td>\n")
        self.results.write("   <td>" + self.current_test['title'] + "</td>\n")
        self.results.write("   <td>\n")
        self.results.write("    <a href=\"" + output + "\">" + output + "</a><br>\n") #Jumping the gun a bit
        # TODO start CPU timer...is it possible?
        start = time.time()
        for cmd in cmds:
            c = shlex.split(cmd)
            print cmd
            self.results.write("    " + cmd + "<br>\n") 
            call(c)
        stop = time.time()
        elapsed = stop - start
        self.results.write("   </td>\n")
        self.results.write("   <td>" + str(elapsed) + "s</td>\n")
        self.results.write("   <td></td>\n")

        # Get size of output file
        size = os.path.getsize(output)
        self.results.write("   <td>" + str(size) + "B</td>\n")

        # Create Image for each image point
        self.results.write("   <td>")
        thumbs = self.tps.grab_points(output)
        for thumb in thumbs:
            self.results.write('    <a href="' + thumb['img'] + '"><img src="' + thumb['thumb'] + '"></a>\n')
        self.results.write("   </td>\n")
        self.results.write("  </tr>\n")
        self.results.flush()

if __name__ == '__main__':
    t = FFMpegTester()
    t.run()
