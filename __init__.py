"""
skill laugh

Copyright (C) 2018 JarbasAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

"""

from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.audio import wait_while_speaking, is_speaking
from mycroft.util import play_wav, play_mp3, play_ogg
from os import listdir
from os.path import join, abspath, dirname
import random
from datetime import timedelta, datetime
from mycroft.util.parse import match_one, normalize, extract_duration
import wave
import contextlib
import pytz
import math
import time

class WhiteNoise(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.random_laugh = False
        self.sounds = {"male": [], "female": []}
        self.endtime = None;
        if "gender" not in self.settings:
            self.settings["gender"] = "male"
        if "sounds_dir" not in self.settings:
            self.settings["sounds_dir"] = join(dirname(__file__), "sounds")
        self.process = None
        self.settings.set_changed_callback(self._fix_gender)
        

    def _fix_gender(self):
        if "f" in self.settings["gender"].lower():
            self.settings["gender"] = "female"
        elif "m" in self.settings["gender"].lower():
            self.settings["gender"] = "male"
        else:
            self.settings["gender"] = "robot"

    def initialize(self):
        sounds_dir = join(self.settings["sounds_dir"], "male")
        self.sounds["male"] = [join(sounds_dir, sound) for sound in
                               listdir(sounds_dir) if
                               ".wav" in sound or ".mp3" in
                               sound]
        sounds_dir = join(self.settings["sounds_dir"], "female")
        self.sounds["female"] = [join(sounds_dir, sound) for sound in
                                 listdir(sounds_dir) if
                                 ".wav" in sound or ".mp3" in sound]
        sounds_dir = join(self.settings["sounds_dir"], "robot")
        self.sounds["robot"] = [join(sounds_dir, sound) for sound in
                                listdir(sounds_dir) if
                                ".wav" in sound or ".mp3" in sound]
        # stop laughs for speech execution
        self.add_event("speak", self.stop_laugh)
        #Build play list
        self.play_list = {
            'ocean': join(abspath(dirname(__file__)), 'sounds', 'ocean.wav'),    
            'wind': join(abspath(dirname(__file__)), 'sounds', 'wind.wav'),
            'train': join(abspath(dirname(__file__)), 'sounds', 'rain.wav'),
        
        }
        
    #Play random noise or a specific noise from list
    @intent_file_handler('noise.white.intent')
    def handle_stories_bedtime(self, message):
        print("inside handler")
        wait_while_speaking()
        print (message.data.get('sound'))
        if message.data.get('sound') is not None:
            print("inside not None")
            title = message.data.get('sound')
            score = match_one(title, self.play_list)
            print(score)
            if score[1] > 0.5:
                self.process = play_wav(score[0])
            else:
                self.speak('Sorry I could not find that sound in my library')
                return None            
        else:
            print("inside None")
            story_file = list(self.play_list.values())
            story_file = random.choice(story_file)
            print(story_file)
            #if os.path.isfile(story_file):
            wait_while_speaking()
            self.process = play_wav(story_file)
    #Handles Loop Call
    @intent_file_handler('whitenoiseloop.intent')
    def handle_loop_whitenoise(self, message):
        print("inside loop handler")
        wait_while_speaking()
        print (message.data.get('sound'))
        if message.data.get('sound') is not None:
            print("inside not None")
            title = message.data.get('sound')
            score = match_one(title, self.play_list)
            print(score)
            if score[1] > 0.5:
                self.process = play_wav(score[0])
            else:
                return None
                self.speak('Sorry I could not find that sound in my library')
        else:
            print("inside None")
            story_file = list(self.play_list.values())
            story_file = random.choice(story_file)
            print(story_file)
            #if os.path.isfile(story_file):
            wait_while_speaking()
            self.process = play_wav(story_file)
            fname = story_file
            with contextlib.closing(wave.open(fname,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                print(duration)
##                    self.cancel_scheduled_event('loop_whitenoise')
##                    self.schedule_event(self.handle_loop_whitenoise,
##                    datetime.now() + timedelta(
##                    seconds=math.ceil(duration)),
##                    name='loop_whitenoise')

        #Extract Time and Duration of Audio Play
        utt = normalize(message.data.get('utterance', "").lower())
        extract = extract_duration(utt)
        print (extract)
        if extract:
            total_duration = extract[0]
            self.endtime = extract[0]
            utt = extract[1]
        utc=pytz.UTC
        print("Current Duration:" )
        secs = self.endtime.total_seconds()
        now = datetime.now()
        time_expires = now + timedelta(seconds=secs)
        self.timer = {
                 "duration": secs,
                 "expires": time_expires
                 }
        self.update_time(None)
                
                    
    def update_time(self, message):
        print("inside update_time")
        # Check if there is an expired timer
        now = datetime.now()
        # Calc remaining time and show using faceplate
        if (self.timer["expires"] > now):
            # Timer still running
            remaining = (self.timer["expires"] - now).seconds
            print (remaining)
            self.cancel_scheduled_event('ShowTimer')
            self.schedule_repeating_event(self.update_time,
                                          None, 1,
                                          name='ShowTimer')
        else:
            # Timer has expired but not been cleared, flash eyes
            overtime = (now - self.timer["expires"]).seconds
            print (overtime)
            self.cancel_scheduled_event('ShowTimer')
            self.stop()
    def stop_laugh(self):
        if self.process is not None:
            self.process.terminate()
            return True
        return False
    @intent_handler(IntentBuilder("")
      .require("Stop")
    )
    def stop(self):
        # abort current laugh
        stopped = self.stop_laugh()
        # stop random laughs
        if self.random_laugh:
            self.halt_laughing(None)
            stopped = True
        return stopped


def create_skill():
    return WhiteNoise()
