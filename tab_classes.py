import speech_recognition
import threading

import tkinter as tk
from tkinter import *
from tkinter import ttk

import autocorrect
from main_classes import *


class TextSearchTab(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.search_bar = ttk.Entry(self, width=50)

        self.search_button = ttk.Button(self, text='Search', command=self.make_search_request)

        self.google_label = ttk.Label(self, text='Search in')

        self.google_redirect = ttk.Button(self, text='Google', command=self.redirect_to_google)

        self.text_frame = ttk.Frame(self)
        self.search_result = Text(self.text_frame, font=('Arial', 10, 'normal'))
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=VERTICAL, command=self.search_result.yview)

        self.search_result.config(yscrollcommand=self.scrollbar.set)

        self.search_bar.place(x=170, y=60, height=30)
        self.search_button.place(x=170, y=100)
        self.google_label.place(x=20, y=165)
        self.google_redirect.place(x=72, y=163, width=50)
        self.text_frame.place(x=15, width=570, height=260, y=190)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.search_result.pack(fill=BOTH, expand=True)

    def make_search_request(self):
        """
        First query the search classes in main_classes.py, if it doesn't produce a valid result, run the spell checker
        to correct the typo and try again. Any how it goes output the result tot the result tab
        :return:
        """

        # initialize spell checker
        spell_checker = autocorrect.Speller()

        # get search bar text
        search_bar_text = self.search_bar.get()

        # if searchbar is empty don't run
        if not search_bar_text:
            self.search_result.insert(0.0 + 1, 'searchbar is empty')
            return

        print(search_bar_text)
        # empty the result tab
        self.search_result.delete('0.0', END)

        # run the search
        query_result = Main(search_bar_text).__()
        print(query_result)
        if query_result is None:
            # pass text through spell checker and try again
            spell_checked_search = spell_checker(search_bar_text)

            print(spell_checked_search)
            query_result = Main(spell_checked_search).__()

        if query_result is None:
            query_result = 'Couldn\'t find anything. Please try again'

        self.search_result.insert(0.0 + 1, query_result)

    def redirect_to_google(self):
        self.root.select(2)


class VoiceSearchTab(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.container = ttk.Frame(self)
        self.canvas = Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame)

        self.canvas.bind("<Configure>", self.configure_canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.begin = ttk.Button(self.scrollable_frame, text='Listen', width=10, command=self.start_listening)

        self.container.pack(fill="both", expand=True)
        self.canvas.pack(side="left", fill="both", expand=1)
        self.scrollbar.pack(side="right", fill="y", expand=0)
        self.begin.pack(anchor='w', padx=20, pady=30)

    def configure_canvas(self, event):
        height = 0
        for child in self.container.grid_slaves():
            height += child.winfo_reqheight()

        self.canvas.itemconfigure(self.canvas_frame, width=event.width, height=height)

    def start_listening(self):
        voice_search_thread = threading.Thread(target=self.search_using_speech_data)
        voice_search_thread.start()

    def search_using_speech_data(self):
        word_frame_main = ttk.Frame(self.scrollable_frame)
        listening = Label(word_frame_main, text='Listening...', relief=SOLID, wraplength=185,
                          bd=1, anchor='w',
                          padx=5,
                          justify=LEFT,
                          width=30)
        listening.pack(side=LEFT)
        word_frame_main.pack(fill=X, padx=20, pady=10)

        try:
            with sr.Microphone() as source:
                speech.adjust_for_ambient_noise(source, duration=0.5)
                audio = speech.listen(source, timeout=2)
                command = speech.recognize_google(audio)
                word_frame = ttk.Frame(self.scrollable_frame)
                question = Label(word_frame, text=command, relief=SOLID, wraplength=185, bd=1, anchor='e', padx=5,
                                 justify=RIGHT, width=30)
                question.pack(side=RIGHT)
                word_frame.pack(fill=X, padx=20, pady=10)
                print('done')
                t = threading.Thread(target=self.respond_to_query, args=(command,))
                t.start()
        except speech_recognition.UnknownValueError:
            return None

    def respond_to_query(self, word):
        word_frame_main = ttk.Frame(self.scrollable_frame)
        m = Main(word).__()
        print(m)
        if m == 'No Result':
            word_frame_main = ttk.Frame(self.scrollable_frame)
            listening = Label(word_frame_main, text='Sorry, didn\'t get that.', relief=SOLID, wraplength=185,
                              bd=1, anchor='w',
                              padx=5,
                              justify=LEFT,
                              width=30)
            listening.pack(side=LEFT)
            word_frame_main.pack(fill=X, padx=20, pady=10)

            word_frame_main = ttk.Frame(self.scrollable_frame)
            listening = Label(word_frame_main, text='Click the button to try again', relief=SOLID, wraplength=185,
                              bd=1, anchor='w',
                              padx=5,
                              justify=LEFT,
                              width=30)
            listening.pack(side=LEFT)
            word_frame_main.pack(fill=X, padx=20, pady=10)
        else:
            word_frame_main = ttk.Frame(self.scrollable_frame)
            listening = Label(word_frame_main, text=m, relief=SOLID, wraplength=185,
                              bd=1, anchor='w',
                              padx=5,
                              justify=LEFT,
                              width=30)
            listening.pack(side=LEFT)
            word_frame_main.pack(fill=X, padx=20, pady=10)
            Play(m).__()

            word_frame_main = ttk.Frame(self.scrollable_frame)
            listening = Label(word_frame_main, text='Click the button to try again', relief=SOLID, wraplength=185,
                              bd=1, anchor='w',
                              padx=5,
                              justify=LEFT,
                              width=30)
            listening.pack(side=LEFT)
            word_frame_main.pack(fill=X, padx=20, pady=10)
