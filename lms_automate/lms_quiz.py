import requests
from bs4 import BeautifulSoup
import webbrowser as web
import urllib.parse as urlparse
import keyboard
from collections import OrderedDict
import re
import subprocess

def copy2clip(txt):
    return subprocess.check_call(
        'echo "'+txt.strip()+'" |clip',
        shell=True)

class Question:
    def __init__(self,question,options) -> None:
        self.question = question
        self.options = options

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class lms_quiz():
    def __init__(self,sessionid,url):
        self.sessionid = sessionid
        self.url = url
        self.hot_hey = "ctrl+shift+'"

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Cookie': f"MoodleSession={self.sessionid}"
            }
        self.questions = OrderedDict() 
        
        self.url_parts = list(urlparse.urlparse(self.url))
        self.query = dict(urlparse.parse_qsl(self.url_parts[4]))
        
        # GET TOTAL QUESTION AND PAGES
        html_soup = self.get_page(self.url)
        questions = self.get_total_questins(html_soup)
        self.question_count = len(questions)

        # pages are 0 - nth-1   
        # if more page exits
        try:
            self.pages = urlparse.parse_qs(urlparse.urlparse(questions[-1]).query).get('page')[0]
        except :
            self.pages = 0
        
        # get question from first page
        for que in self.get_question(html_soup) :
            self.questions[que] = None

    def get_updated_url(self,params):
        self.query.update(params)
        self.url_parts[4] = urlparse.urlencode(self.query)
        return urlparse.urlunparse(self.url_parts)

    def get_all_question(self):
        count = 1
        print(f"\n{bcolors.OKGREEN}Exploring new Pages.")
        while self.question_count != len(self.questions):
            params = {'page':f'{count}'}
            page_url = self.get_updated_url(params)
            print(f"{bcolors.OKCYAN}  {count} : {page_url}{bcolors.ENDC}")
            # get the page
            page_html_soul = self.get_page(page_url)
            # get the questions and update list of questions
            for i in self.get_question(page_html_soul):   ### need to use it 
                self.questions[i] = None 
            count += 1
            if count >= self.question_count:
                break
        print()

    def get_page(self,url):
        """get the page from url and cookies then return parse resutls"""
        response = requests.get(
            url,
            headers = self.headers
        )
        if response.status_code == 404:
            print(bcolors.FAIL, "Error in opening page - ", url, bcolors.ENDC)
            exit()

        return BeautifulSoup(response.content, 'html.parser')
        
    def get_total_questins(self,soup):
        """take page and return and count total questions""" 
        return [ href for href in [link_['href'] for link_ in \
            soup.select("div.qn_buttons.clearfix.multipages a") \
                if link_] if href]

    def get_question(self,soup):
        """get questions from the soup/ from html page"""
        content = soup.select(".content .formulation.clearfix")
        # fix it for the text-area adn file upload 
        questions = []
        for question in content:
            question_ = BeautifulSoup(f"<html>{question}</html>", 'html.parser').text
            question_ = re.sub(r"[A-Z]{3}[0-9]{2}[A-Z][0-9]{4}[_A-Z0-9:]*","",question_)
            question_ = question_.replace('\r\n',' ')
            question_ = question_.replace('Clear my choice','')
            question_ = question_.replace('Select one:','\n')
            question_ = question_.replace('Loading...','')
            question_ = question_.replace('You can drag and drop files here to add them.Drop files here to upload','\n')
            question_ = question_.replace('Maximum file size: 1MB, ','')
            question_ = question_.replace('- drag and drop not supported','')
            question_ = question_.replace('You can drag and drop files here to add them.','')
            question_ = question_.replace('Drop files here to upload','')
            question_ = re.sub(r"maximum number of files: \d","",question_)
            question_ = re.sub(r"Accepted file typesDocument file.*","",question_)
            question_ = re.sub(r"\nPDF.*","",question_)
            question_ = question_.replace('\n\n','')

            # seperate quesiton and its options
            only_question = re.search(r"^Question text(.*)",question_).group(1)
            options = [ x.group().strip() \
                for x in re.finditer(r"(\n([a-z]\. )?.*)",question_) ] or []
                # for x in re.finditer(r"(([a-z]\. |\n).*)",question_) ] or []
            
            # print(question_)
            # print(only_question)
            # print(options)
            # print()
            questions.append(
                Question(only_question,options)
                )

        return questions
    
    def get_content_urls(self,question):
        """return the list of url to search reasults"""
        question = urlparse.quote(question)

        # update the comments to get more results 
        return [
            f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={question}&btnG=",# google scholar
            f"https://www.google.com/search?q={question}",# google
            # f"https://en.wikipedia.org/w/index.php?search={question}&title=Special%3ASearch&profile=advanced",# wiki-pedia
            # f"https://www.quora.com/search?q={question}",# quora
            f"https://www.answers.com/search?q={question}",# answer
            f"https://www.toppr.com/ask/search/?query={question}"# toppr
            ]
        
    def open_searches(self,question):
        "this will open pages to get the results"
        # can be update according to use
        for url in self.get_content_urls(question) :
            web.open(url)

    def show_answers(self):
        """show resutls to the user"""
        for index ,ques in enumerate(self.questions.keys()):
            print(f"{bcolors.WARNING}[Question:{index+1}] > \n{bcolors.OKBLUE}{ques.question}{bcolors.ENDC}")
            for op in ques.options:
                print(f"{bcolors.OKBLUE}{op}{bcolors.ENDC}")
            copy2clip(ques.question)
            print(f"{bcolors.OKCYAN}\tQuestion is copied to the clip-board.{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}Press hot keys to see the next question results <{self.hot_hey}>.{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}\t\tor ctrl+c for next question.{bcolors.ENDC}")

            try :
                # on key press event
                keyboard.wait(f"{self.hot_hey}")
            except KeyboardInterrupt:
                print("next questinon")
                continue
            print(f"{bcolors.OKGREEN}showing pages{bcolors.ENDC}")
            self.open_searches(ques.question)
       
    @classmethod
    def runner(cls,sessionid,url):
        cl = cls(sessionid,url)
        cl.get_all_question()
        cl.show_answers()

if __name__ == "__main__":
    # update the sessionid from brower and url 
    sessionid = "" # example - '5gk1ti0t2e65qmgb0772snsdfl7'
    url = "" # example "https://lms.galgotiasuniversity.edu.in/mod/quiz/attempt.php?attempt=6314102&cmid=484157"

    # testing
    sessionid = "lev15q85j50mn8viqlks0ert85" # example - '5gk1ti0t2e65qmgb0772snsdfl7'
    url = "https://lms.galgotiasuniversity.edu.in/mod/quiz/attempt.php?attempt=6404785&cmid=500516" # example "https://lms.galgotiasuniversity.edu.in/mod/quiz/attempt.php?attempt=6314102&cmid=484157"
    # url = "http://127.0.0.1:5500/testing10que.html?attempt=6349252&cmid=498254"


    if not sessionid or not url :
        raise Exception(f"{bcolors.FAIL}Update the value to use the program {bcolors.ENDC}")
    lms_quiz.runner(
            sessionid,url
            )
