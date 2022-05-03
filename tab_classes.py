import speech_recognition
import threading

import tkinter as tk
from tkinter import *
from tkinter import ttk

import autocorrect
from main_classes import *


def create_new_label(main_frame, label_text='', side=None, larger=False, last_label_position=None):
    print(dir(main_frame.winfo_children()[0]))
    wrap_length = 185
    width = 30
    frame_y_padding = 10

    if larger:
        wrap_length = 330
        width = 50

    side = LEFT if side is None else side
    anchor = "w" if side == LEFT else "e"

    if last_label_position == side:
        frame_y_padding = 0

    word_frame_main = ttk.Frame(main_frame)
    listening = Label(word_frame_main, text=label_text, relief=SOLID, wraplength=wrap_length,
                      bd=1, anchor=anchor,
                      padx=5,
                      justify=side,
                      width=width)
    listening.pack(side=side)
    word_frame_main.pack(fill=X, padx=20, pady=frame_y_padding)


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
        self.last_label_position = LEFT

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
        # create label to indicate listening
        create_new_label(self.scrollable_frame, label_text='Listening')
        self.last_label_position = LEFT

        try:
            with sr.Microphone(sample_rate=48000, chunk_size=2048) as source:
                # get speach data
                speech.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = speech.listen(source, timeout=1, phrase_time_limit=10)
                voice_command = speech.recognize_google(audio_data)

                create_new_label(self.scrollable_frame, label_text=voice_command, side=RIGHT,
                                 last_label_position=self.last_label_position)
                self.last_label_position = RIGHT

                # respond to user
                t = threading.Thread(target=self.respond_to_query, args=(voice_command,))
                t.start()
        except speech_recognition.UnknownValueError:
            create_new_label(self.scrollable_frame,
                             label_text='Unable to understand statement. Click the button to try again', larger=True,
                             last_label_position=self.last_label_position)
            self.last_label_position = LEFT

        except speech_recognition.RequestError:
            create_new_label(self.scrollable_frame,
                             label_text='Couldn\'t process request. Click the button to try again', larger=True,
                             last_label_position=self.last_label_position)
            self.last_label_position = LEFT

    def respond_to_query(self, voice_command):
        # get search result
        search_result = Main(voice_command).__()

        # adjust label width to accommodate large data
        if search_result is not None:
            larger = True if len(search_result) >= 30 else False

            create_new_label(self.scrollable_frame, label_text=search_result, larger=larger,
                             last_label_position=self.last_label_position)
            self.last_label_position = LEFT

            create_new_label(self.scrollable_frame, label_text='Click the button to continue',
                             last_label_position=self.last_label_position)
            return

        create_new_label(self.scrollable_frame,
                         label_text='Couldn\'t process request. Click the button to try again', larger=True)

        self.last_label_position = LEFT
