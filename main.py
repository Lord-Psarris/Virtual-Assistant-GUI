import os

import ctypes

import sys
from tkinter import ttk

import re
from autocorrect import Speller

from cefpython3 import cefpython as cef
from main_classes import *
import tkinter as tk
from tkinter import *
import platform
import logging as _logging

WindowUtils = cef.WindowUtils()
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# Globals
logger = _logging.getLogger("tkinter_.py")
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"


def close_window():
    exit()


def is_valid_url(url):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)

    if url == None:
        return False

    if re.search(p, url):
        return True
    else:
        return False


class Assistant:
    root = tk.Tk()
    root.title("Athena search")
    root.minsize(600, 500)
    root.maxsize(600, 500)

    def __init__(self):
        self.parent = Assistant.root
        self.counter = 1

        main_tab = ttk.Notebook(self.parent)
        main_tab.bind("<<NotebookTabChanged>>", self.handle_change)

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

        self.google_redirect = ttk.Button(self.text, text='Google', command=self.redirect)

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
        browser_tab = ttk.Notebook(self.browse)
        browser_tab.bind("<<NotebookTabChanged>>", self.add_tab)
        browser_tab.bind("<Button-3>", self.close_tab)

        browser_ = tk.Frame(browser_tab)
        add_tab = tk.Frame(browser_tab)

        browser_tab.add(browser_, text=f'Tab {str(self.counter)}')
        browser_tab.add(add_tab, text='+')

        main(browser_)

        # spreading
        self.main_tab = main_tab
        self.browser_tab = browser_tab

        # functions
        self.packed()
        self.parent.protocol("WM_DELETE_WINDOW", close_window)
        self.parent.mainloop()

    def add_tab(self, event):
        selection = event.widget.select()
        tab = event.widget.tab(selection, "text")
        if tab == '+':
            browser_ = tk.Frame(self.browser_tab)
            main(browser_)
            self.counter += 1
            self.browser_tab.add(browser_, text=f'Tab {str(self.counter)}')
            self.browser_tab.forget(selection)
            self.browser_tab.event_generate("<<NotebookTabClosed>>")

            add_tab = tk.Frame(self.browser_tab)
            self.browser_tab.add(add_tab, text='+')

            self.browser_tab.select(self.counter - 1)

    def close_tab(self, event):
        clicked = self.browser_tab.tk.call(self.browser_tab._w, "identify", "tab", event.x, event.y)
        tab = event.widget.tab(clicked, "text")
        if tab == '+':
            return
        self.browser_tab.forget(clicked)

    def handle_change(self, event):
        w, h = pyautogui.size()
        selection = event.widget.select()
        tab = event.widget.tab(selection, "text")
        if tab == 'Browse':
            self.parent.maxsize(w, h)
            self.parent.minsize(600, 500)
        else:
            if self.parent.state() == 'zoomed':
                self.parent.state('normal')
            self.parent.maxsize(600, 500)
            self.parent.minsize(600, 500)

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
        self.main_tab.select(2)

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
        self.browser_tab.pack(expand=1, fill="both")


# browser
def main(root):
    logger.setLevel(_logging.DEBUG)
    stream_handler = _logging.StreamHandler()
    formatter = _logging.Formatter("[%(filename)s] %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.info("CEF Python {ver}".format(ver=cef.__version__))
    logger.info("Python {ver} {arch}".format(
        ver=platform.python_version(), arch=platform.architecture()[0]))
    logger.info("Tk {ver}".format(ver=tk.Tcl().eval('info patchlevel')))
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    MainFrame(root)
    settings = {}
    if MAC:
        settings["external_message_pump"] = True
    cef.Initialize(settings=settings)
    logger.debug("Main loop exited")
    # cef.Shutdown()


class MainFrame(tk.Frame):

    def __init__(self, root):
        self.browser_frame = None
        self.navigation_bar = None
        self.root = root

        # Root
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)

        # MainFrame
        tk.Frame.__init__(self, root)
        # self.master.title("Athena Browser")
        # self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        self.setup_icon()
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # NavigationBar
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.grid(row=0, column=0,
                                 sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, self.navigation_bar)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("MainFrame.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            if self.navigation_bar:
                height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        logger.debug("MainFrame.on_focus_in")

    def on_focus_out(self, _):
        logger.debug("MainFrame.on_focus_out")

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
            self.browser_frame = None
        else:
            self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def setup_icon(self):
        resources = os.path.join(os.path.dirname(__file__), "resources")
        icon_path = os.path.join(resources, "tkinter" + IMAGE_EXT)
        if os.path.exists(icon_path):
            self.icon = tk.PhotoImage(file=icon_path)
            # noinspection PyProtectedMember
            self.master.call("wm", "iconphoto", self.master._w, self.icon)


class BrowserFrame(tk.Frame):

    def __init__(self, mainframe, navigation_bar=None):
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, mainframe)
        self.mainframe = mainframe
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        """For focus problems see Issue #255 and Issue #535. """
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url="https://www.google.com/")
        assert self.browser
        self.browser.SetClientHandler(LifespanHandler(self))
        self.browser.SetClientHandler(LoadHandler(self))
        self.browser.SetClientHandler(FocusHandler(self))
        self.message_loop_work()

    def get_window_handle(self):
        if MAC:
            # Do not use self.winfo_id() on Mac, because of these issues:
            # 1. Window id sometimes has an invalid negative value (Issue #308).
            # 2. Even with valid window id it crashes during the call to NSView.setAutoresizingMask:
            #    https://github.com/cztomczak/cefpython/issues/309#issuecomment-661094466
            #
            # To fix it using PyObjC package to obtain window handle. If you change structure of windows then you
            # need to do modifications here as well.
            #
            # There is still one issue with this solution. Sometimes there is more than one window, for example when application
            # didn't close cleanly last time Python displays an NSAlert window asking whether to Reopen that window. In such
            # case app will crash and you will see in console:
            # > Fatal Python error: PyEval_RestoreThread: NULL tstate
            # > zsh: abort      python tkinter_.py
            # Error messages related to this: https://github.com/cztomczak/cefpython/issues/441
            #
            # There is yet another issue that might be related as well:
            # https://github.com/cztomczak/cefpython/issues/583

            # noinspection PyUnresolvedReferences
            from AppKit import NSApp
            # noinspection PyUnresolvedReferences
            import objc
            logger.info("winfo_id={}".format(self.winfo_id()))
            # noinspection PyUnresolvedReferences
            content_view = objc.pyobjc_id(NSApp.windows()[-1].contentView())
            logger.info("content_view={}".format(content_view))
            return content_view
        elif self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        logger.debug("BrowserFrame.on_focus_out")
        """For focus problems see Issue #255 and Issue #535. """
        if LINUX and self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        logger.info("BrowserFrame.on_root_close")
        if self.browser:
            logger.debug("CloseBrowser")
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        else:
            logger.debug("tk.Frame.destroy")
            self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None


class LifespanHandler(object):

    def __init__(self, tkFrame):
        self.tkFrame = tkFrame

    def OnBeforeClose(self, browser, **_):
        logger.debug("LifespanHandler.OnBeforeClose")
        self.tkFrame.quit()


class LoadHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnLoadStart(self, browser, **_):
        if self.browser_frame.master.navigation_bar:
            self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())


class FocusHandler(object):
    """For focus problems see Issue #255 and Issue #535. """

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        logger.debug("FocusHandler.OnTakeFocus, next={next}"
                     .format(next=next_component))

    def OnSetFocus(self, source, **_):
        logger.debug("FocusHandler.OnSetFocus, source={source}"
                     .format(source=source))
        if LINUX:
            return False
        else:
            return True

    def OnGotFocus(self, **_):
        logger.debug("FocusHandler.OnGotFocus")
        if LINUX:
            self.browser_frame.focus_set()


class NavigationBar(tk.Frame):

    def __init__(self, master):
        self.back_state = tk.NONE
        self.forward_state = tk.NONE

        tk.Frame.__init__(self, master)
        resources = os.path.join(os.path.dirname(__file__), "resources")

        # Back button
        self.back_button = tk.Button(self, text='prev',
                                     command=self.go_back)
        self.back_button.grid(row=0, column=0)

        # Forward button
        self.forward_button = tk.Button(self, text='next',
                                        command=self.go_forward)
        self.forward_button.grid(row=0, column=1)

        # Reload button
        self.reload_button = tk.Button(self, text='reload',
                                       command=self.reload)
        self.reload_button.grid(row=0, column=2)

        # Url entry
        self.url_entry = tk.Entry(self)
        self.url_entry.bind("<FocusIn>", self.on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self.on_url_focus_out)
        self.url_entry.bind("<Return>", self.on_load_url)
        self.url_entry.bind("<Button-1>", self.on_button1)
        self.url_entry.grid(row=0, column=3,
                            sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=100)
        tk.Grid.columnconfigure(self, 3, weight=100)

        # Update state of buttons
        self.update_state()

    def go_back(self):
        if self.master.get_browser():
            self.master.get_browser().GoBack()

    def go_forward(self):
        if self.master.get_browser():
            self.master.get_browser().GoForward()

    def reload(self):
        if self.master.get_browser():
            self.master.get_browser().Reload()

    def set_url(self, url_):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url_)

    def on_url_focus_in(self, _):
        pass

    def on_url_focus_out(self, _):
        pass

    def on_load_url(self, _):
        website = self.url_entry.get()
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            if is_valid_url(website):
                self.master.get_browser().LoadUrl(website)
            else:
                print('not correct')
                if ".com" in website or '.org' in website or '.net' in website:
                    if "https://" not in website and "www." in website:
                        website = f"https://{website}"
                    if "https://" not in website and "www." not in website:
                        website = f"https://www.{website}"
                    self.set_url(website)
                else:
                    website = f"https://www.google.com/search?q={website}"
                    self.set_url(website)
                self.master.get_browser().LoadUrl(website)

    def on_button1(self, _):
        """For focus problems see Issue #255 and Issue #535. """
        logger.debug("NavigationBar.on_button1")
        self.master.master.focus_force()

    def update_state(self):
        browser = self.master.get_browser()
        if not browser:
            if self.back_state != tk.DISABLED:
                self.back_button.config(state=tk.DISABLED)
                self.back_state = tk.DISABLED
            if self.forward_state != tk.DISABLED:
                self.forward_button.config(state=tk.DISABLED)
                self.forward_state = tk.DISABLED
            self.after(100, self.update_state)
            return
        if browser.CanGoBack():
            if self.back_state != tk.NORMAL:
                self.back_button.config(state=tk.NORMAL)
                self.back_state = tk.NORMAL
        else:
            if self.back_state != tk.DISABLED:
                self.back_button.config(state=tk.DISABLED)
                self.back_state = tk.DISABLED
        if browser.CanGoForward():
            if self.forward_state != tk.NORMAL:
                self.forward_button.config(state=tk.NORMAL)
                self.forward_state = tk.NORMAL
        else:
            if self.forward_state != tk.DISABLED:
                self.forward_button.config(state=tk.DISABLED)
                self.forward_state = tk.DISABLED
        self.after(100, self.update_state)


class Tabs(tk.Frame):

    def __init__(self):
        tk.Frame.__init__(self)
        # TODO: implement tabs


if __name__ == "__main__":
    Assistant()
