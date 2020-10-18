from Qt import QtWidgets
from Qt import QtCompat
from Qt import QtGui
from Qt import QtCore

import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import time

from functools import partial


class VoiceToText(object):
    def __init__(self, ui=None):
        super(VoiceToText, self).__init__()
        self.ui = ui

        self.engine = None
        self.voices = None
        self.results = None
        self.connections()
        self.initialize()

    def initialize(self):
        #self.engine = pyttsx3.init('sapi5')
        self.engine = pyttsx3.init('dummy')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("listing....")
            self.speak("listing....")
            # r.pause_threshold=1
            audio = sr.Recognizer().listen(source)
            print(audio)
        try:
            print("Recognizing.....")
            self.speak("Recognizing.....")
            query = sr.Recognizer().recognize_google(audio, language='en-US')
            print(query)
            print("user said :", query)
            self.speak(f"u said {query}")
        except Exception as e:
            print(e)
            self.speak("say again please....")
            return "None"
        return query

    def give_command(self):
        results = None
        query = self.take_command().lower()

        if "wikipedia" in query:
            query = query.replace("wikipedia", "")
            self.results = wikipedia.summary(query, sentences=5)

        elif "open google" in query:
            webbrowser("google.com")

        elif "open whats app" in query:
            webbrowser("whatsapp.com")

        elif "open facebook" in query:
            webbrowser("facebook.com")

        elif "open music" in query:
            music_dir = ""
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))

        elif "what is the time" in query:
            strTime = datetime.datetime.now().hour
            self.results = strTime

        else:
            self.results = query

    def recording_start_stop(self):
        if self.ui.recording_pb.isChecked():
            self.give_command()

        if self.results:
            self.ui.voice_text_te.clear()
            self.ui.voice_text_te.textCursor().insertText(self.results)

    def hide_widget(self):
        if self.ui.voice_wd.isHidden():
            self.ui.voice_wd.show()
            self.ui.image_converter_wd.hide()
            self.ui.text_wd.hide()
            return
        self.ui.voice_wd.hide()

    def connections(self):
        self.ui.voice_hide_pb.clicked.connect(partial(self.hide_widget))
        self.ui.recording_pb.clicked.connect(partial(self.recording_start_stop))