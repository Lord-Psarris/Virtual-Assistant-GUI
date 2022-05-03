# imports
import http.client as http
import pyautogui
import pyttsx3
import requests
import speech_recognition as sr
import time
import wikipedia
import wolframalpha

import CONFIG as CF

# necessities
appId = CF.WOLFRAM_ALPHA_API_KEY  # get the wolfram alpha app id
client = wolframalpha.Client(appId)
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')  # getting details of current voice
speaker.setProperty('voice', voices[1].id)
rate = speaker.getProperty('rate')  # getting details of current speaking rate: 200
speaker.setProperty('rate', 170)  # setting up new voice rate
speech = sr.Recognizer()


def search(param):
    pyautogui.hotkey('win', 's')
    print(param)
    time.sleep(3)
    pyautogui.typewrite(param)
    time.sleep(1)
    pyautogui.typewrite(['enter'])


# main class
class Main:
    def __init__(self, query):
        self.loop = True
        self.query = query

    def __(self):

        self.connection = http.HTTPConnection("www.google.com", timeout=5)
        try:
            self.connection.request("HEAD", "/")
            self.connection.close()
            command = self.query
            haystack = command
            count = haystack.find('open')
            if command == 'end':
                self.loop = False
            elif count == 0:
                param = command.replace('open ', '')
                search(param)
                # Play(f'opening {param}').__()
                time.sleep(3)
                return f'opening {param}'
            else:
                answer = Personalised(command)
                answer = answer.__()
                print('1')
                if answer is None:
                    answer = Wolfram(command).__()
                    print('2')
                    print(answer)
                    if answer is None:
                        wiki = Wiki(command).__()
                        if wiki is None:
                            return None
                        else:
                            self.answer = wiki
                            print('3')
                            return self.answer
                    else:
                        image = Image(command).__()
                        if image is None:
                            pass
                        else:
                            answer = answer.join(f'\n{image}')
                        return answer
                else:
                    self.answer = answer
                    return self.answer

        except Exception as e:
            print(e)
            return 'No internet connection'
        self.connection.close()


# other classes
class Wiki:

    def __init__(self, variable):
        self.variable = variable

    def __(self):

        results = wikipedia.search(self.variable)
        # If there is no result, print no result
        if not results:
            return None
        try:
            page = wikipedia.page(results[0])
        except (wikipedia.DisambiguationError, error):
            page = wikipedia.page(error.options[0])

        wiki = str(page.summary)
        return wiki


class Wolfram:

    def __init__(self, variable):
        self.variable = variable

    def __(self):
        res = client.query(self.variable)
        if res['@success'] == 'false':
            return None
        else:
            # pod[0] is the question
            # pod0 = res['pod'][0]
            # pod[1] may contain the answer
            pod1 = res['pod'][1]
            if (('definition' in pod1['@title'].lower()) or ('result' in pod1['@title'].lower()) or (
                    pod1.get('@primary', 'false') == 'true')):
                # extracting result from pod1
                result = FixQuestion(pod1['subpod'])
                r = result.fix()
                if 'Wolfram|Alpha' in r:
                    result = r.replace('Wolfram|Alpha', 'Athena')
                    return result
                else:
                    return r
            else:
                return None


class Image:

    def __init__(self, variable):
        self.variable = variable

    def __(self):
        url = 'http://en.wikipedia.org/w/api.php'
        data = {'action': 'query', 'prop': 'pageimages', 'format': 'json', 'piprop': 'original',
                'titles': self.variable}
        try:
            keys = ''
            res = requests.get(url, params=data)
            key = res.json()['query']['pages'].keys()
            for i in key:
                keys = i
            if keys == "-1":
                pass
            else:
                image_url = res.json()['query']['pages'][keys]['original']['source']
                return image_url
        except Exception as e:
            print('there was an exception processing the image ' + str(e))


class Personalised:

    def __init__(self, variable):
        self.variable = variable

    def __(self):
        if self.variable == "what do you call yourself":
            return 'My name is Athena.'
        elif self.variable == "what would you like to call yourself":
            return 'I would like to be called "The greatest dopest finest virtual beauty there is" but' \
                   ' Lord psarris says its too much'
        elif self.variable == "when were you created" or self.variable == "when were you made":
            return 'I have no idea. You can ask Lord psarris about that.'
        elif self.variable == "who is lord psarris":
            return 'Lord is my creator, he\'s a really awesome guy'
        elif self.variable == "who is jesus":
            return 'Jesus is the Son of God, who died to redeem us from the curse of the law.'
        else:
            return None


# helper classes
class FixQuestion:

    def __init__(self, question):
        self.question = question

    def fix(self):
        if isinstance(self.question, list):
            return self.question[0]['plaintext']
        else:
            return self.question['plaintext']

    def fix_(self):
        tried = self.question.split('(')[0]
        return tried


class Play:
    def __init__(self, variable):
        self.variable = variable

    def __(self):
        speaker.say(self.variable)
        speaker.runAndWait()
        speaker.stop()


if __name__ == "__main__":
    m = Main('what is your name')
    m = m.__()
