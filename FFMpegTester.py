#!/bin/python
'''This will run tests of various ffmpeg codecs, bitrates, options, etc

This will iterate through multiple tests with multiple different codecs and options and give you 
retults.html when you're done.

This test is strictly single threaded, as some of the codecs will utilize multiple processors if 
they are available, thus we want to only run one test at a time (so we don't get two multi-processor 
tests at the same time, competing for CPU).
'''

#TODO:
# - Load inputs as JSON
#   - Test input(s)
#   - Test case(s)
#   - Test variable shortcuts? (find/replace...use FILL_XXXX notation)
#   - Strip off # to end of line, to enable comments?
# - Command line arguments
#   - Option to skip conversion (output file must already be in place)
#   - Number of threads
#   - JSON Files
#   - Basic input
#   - basic test? default test?
#   - Zoom in on cropped images???  (640x480 video pixels shows up as a 1280x960 image)
# - Put images together into a video
#   - Show each image for X seconds
#   - Use image magick to put the name of the video in the bottom corner of each image
# - Concatenate all the videos for each test into one with text between clips (long-range goal)
# - Javascript image comparison browser (allow flashing between any two selections)
# - Log command output to a text file for each trial


import os
import os.path
from subprocess import call
import time
import shlex
import math
import cStringIO
import tokenize
import json

# This function will remove comments starting with # from a string
# See: http://code.activestate.com/recipes/576704/ for any details, I removed the docstring part
def remove_comments(source):
    io_obj = cStringIO.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        if token_type == tokenize.COMMENT:
            pass
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out

def filesize_format(size_in_bytes,base=1000):
    byteunits = ()
    if base == 1000:
        byteunits = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    elif base == 1024:
        byteunits = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB')
    exponent = int(math.log(size_in_bytes, base))
    return float(size_in_bytes) / pow(base, exponent), byteunits[exponent]

def round_sigfigs(value, significant):
    return round(value, int(significant - math.ceil(math.log10(abs(value)))))

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
            call(shlex.split(str(cmd)))

            img = 'img/' + video_file + "-" + point['sec'] + 's.png'
            # Move the output file to an appropriately named file in the img/ directory
            cmd = 'mv 1.png ' + img
            call(shlex.split(str(cmd)))
            # Keep the full frame in the frames dir
            frm = 'frames/'  + video_file + "-" + point['sec'] + 's.png'
            cmd = 'cp ' + img + ' ' + frm
            call(shlex.split(str(cmd)))

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
            call(shlex.split(str(cmd)))

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

        # Hard coded options (change in future)
        self.threads_var = 0
        self.run_conversion = True
        self.crop_zoom_multiplier = 1
        
        self.json_file = "test.json"
        f = open(self.json_file,'r')
        fstring = f.read()
        f.close()
        no_comment_string = remove_comments(fstring)
        data = json.loads(no_comment_string)  # Really just need the vars
        trim_data = {}
        trim_data['input'] = data['input']
        trim_data['tests'] = data['tests']
        data_string = json.dumps(trim_data)
        replaced_string = self.apply_variables(data_string, data['external_vars'])
        self.data = json.loads(replaced_string)
        self.data['external_vars'] = data['external_vars']
        
    def apply_variables(self, data, variables):
        for k,v in variables.items():
            data = data.replace(k,v)
        return data

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
        self.results.write("   <td><b>Command(s)</b></td>\n")
        self.results.write("   <td><b>Elapsed Time (wall clock)</b></td>\n")
        self.results.write("   <td><b>CPU Time</b></td>\n")
        self.results.write("   <td><b>File Size</b></td>\n")
        self.results.write("   <td><b>Example Images</b></td>\n")
        self.results.write("  </tr>\n")

    def finish_html(self):
        self.results.write("</tbody></table>\n</body>\n</html>\n")
        self.results.close()

    def run_tests(self):
        for infile in self.data['input']:
            self.tps = TestPoints(infile['image_points'], infile['name'])
            self.start_html(infile['name'])
            self.current_input_file = infile
            input_name = infile['name']
            input_files = ""
            for item in infile['files']:
                input_files = input_files + " -i " + item
            for test in self.data['tests']:
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
        os_start = os.times()
        for cmd in cmds:
            print cmd
            self.results.write("    " + cmd + "<br>\n") 
            c = shlex.split(str(cmd))
            call(c)
        os_stop = os.times()
        stop = time.time()
        elapsed = stop - start
        os_elapsed = os_stop[2] - os_start[2] + os_stop[3] - os_stop[3]
        self.results.write("   </td>\n")
        self.results.write("   <td>" + str(round_sigfigs(elapsed,4)) + "s</td>\n")
        self.results.write("   <td>" + str(round_sigfigs(os_elapsed,4)) + "s</td>\n")

        # Get size of output file
        s = os.path.getsize(output)
        size, units = filesize_format(s)
        size = round_sigfigs(size, 3)
        self.results.write("   <td>" + str(size) + units + "</td>\n")

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

