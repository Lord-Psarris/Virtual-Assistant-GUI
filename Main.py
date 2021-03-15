import tkinter as tk
from tkinter import *
from tkinter import ttk
from autocorrect import Speller
from API import Main
from API import *
from Browser import main as browser_main


def open_browser_():
    browser_main()


class Assistant:
    root = tk.Tk()
    root.title("Athena search")
    root.resizable(False, False)
    root.geometry("600x500")

    def __init__(self):
        self.parent = Assistant.root

        main_tab = ttk.Notebook(self.parent)

        self.text = ttk.Frame(main_tab)
        self.voice = ttk.Frame(main_tab)
        self.browse = ttk.Frame(main_tab)

        main_tab.add(self.text, text='Text Search')
        main_tab.add(self.voice, text='Voice Search')
        main_tab.add(self.browse, text='Browse')

        """text search tab"""
        self.search_bar = ttk.Entry(self.text, width=50)

        self.search_button = ttk.Button(self.text, text='Search', command=self.query)

        self.google_label = ttk.Label(self.text, text='Search in')

        self.google_redirect = ttk.Button(self.text, text='Google', command='')

        self.text_frame = ttk.Frame(self.text)
        self.search_result = Text(self.text_frame, font=('Arial', 10, 'normal'))
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=VERTICAL, command=self.search_result.yview)

        self.search_result.config(yscrollcommand=self.scrollbar.set)

        """Voice search tab"""
        self.container = ttk.Frame(self.voice)
        self.canvas = Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.c_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame)

        self.canvas.bind("<Configure>", self.configure_)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.begin = ttk.Button(self.scrollable_frame, text='Listen', width=10, command=self.start)

        """Browser tab"""
        self.open_borwser = ttk.Button(self.browse, text='Open Browser', command=open_browser_)
        # browser_main()

        # spreading
        self.main_tab = main_tab

        # functions
        self.packed()
        self.parent.mainloop()

    def configure_(self, event):
        height = 0
        for child in self.container.grid_slaves():
            height += child.winfo_reqheight()

        self.canvas.itemconfigure(self.c_frame, width=event.width, height=height)

    def query(self):
        spell = Speller()
        search_ = self.search_bar.get()
        if search_:
            print(search_)
            self.search_result.delete('0.0', END)
            m = Main(search_).__()
            print(m)
            if m == 'No Result':
                search_ = spell(search_)
                print(search_)
                m = Main(search_).__()
                if m == 'No Result':
                    pass
            self.search_result.insert(0.0 + 1, m)
        else:
            self.search_result.insert(0.0 + 1, 'searchbar is empty')

    def start(self):
        t = threading.Thread(target=self.voice_search)
        t.start()

    def voice_search(self):
        word_frame_main = ttk.Frame(self.scrollable_frame)
        listening = Label(word_frame_main, text='Listening...', relief=SOLID, wraplength=185,
                          bd=1, anchor='w',
                          padx=5,
                          justify=LEFT,
                          width=30)
        listening.pack(side=LEFT)
        word_frame_main.pack(fill=X, padx=20, pady=10)
        print('listen')
        loop = True
        while loop:
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
                    t = threading.Thread(target=self.response, args=(command,))
                    t.start()
                    loop = False
                loop = False
            except Exception as e:
                print(e)

    def response(self, word):
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

    def redirect(self):
        m = self.search_bar.get()
        webbrowser.open(f"www.google.com/search?q={m}", new=2, autoraise=True)
        # TODO: redirect to the browser u made

    def packed(self):
        self.main_tab.pack(expand=1, fill="both")

        """text search tab"""
        self.search_bar.place(x=170, y=60, height=30)
        self.search_button.place(x=170, y=100)
        self.google_label.place(x=20, y=165)
        self.google_redirect.place(x=72, y=163, width=50)
        self.text_frame.place(x=15, width=570, height=260, y=190)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.search_result.pack(fill=BOTH, expand=True)

        """Voice search tab"""
        self.container.pack(fill="both", expand=True)
        self.canvas.pack(side="left", fill="both", expand=1)
        self.scrollbar.pack(side="right", fill="y", expand=0)
        self.begin.pack(anchor='w', padx=20, pady=30)

        """Browser tab"""
        self.open_borwser.place(relx=0.5, rely=0.5, anchor=CENTER)


if __name__ == "__main__":
    Assistant()
