from multiprocessing import context
from lms_quiz import lms_quiz, bcolors, copy2clip
from data_extractor import google
from transformers import pipeline
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import keyboard
from file_reader import reader
from pathlib import Path
import fnmatch
import re
import os
import time
import tempfile

class lms_quiz_ai(lms_quiz):
    def __init__(self, sessionid, url, path_to_content: Path):
        """models are from - https://huggingface.co/transformers/usage.html"""
        super().__init__(sessionid, url)
        self.path_to_content = Path(path_to_content)
        self.AiConfirm_rate = 0.01
        # souce - online and teacher ppts etc

    def __enter__(self):
        self.question_filename = "questions" + time.strftime("%d-%b-%H%M%S") + ".txt"
        self.questions_file = open(self.question_filename, mode='a')
        self.temp_file = tempfile.TemporaryFile(dir='.', mode='a+',encoding='utf-8')
        self.temp_file_data = ''

        # load models
        self.load_models()
        # get data for ai from local file system
        self.get_files_data()
        
        return self

    def __exit__(self, a, b, c):
        self.temp_file.close()
        self.questions_file.close()
        if open(self.question_filename).read() == "":
            os.remove(self.question_filename)

        print(f'\n\n\t\t{bcolors.BOLD} Goodbye',end=f"{bcolors.ENDC}\n")

    def load_models(self):
        # loading all the pretrained models
        print(f"{bcolors.OKGREEN}Loading Models", end=f"{bcolors.ENDC}\n")

        # fill-mask
        print(f"{bcolors.OKCYAN}Loading fill-mask Model",
              end=f"......{bcolors.ENDC}")
        self.nlp = pipeline("fill-mask")
        print(' Successfully Loaded')

        # questions and answers
        print(f"{bcolors.OKCYAN}Loading question-answering Model",
              end=f".....{bcolors.ENDC}")
        self.qna = pipeline("question-answering")
        print(' Successfully Loaded')

        # can add tokenizer model


    def save_questions(self):
        """save the questions in the file"""
        for que in self.questions:
            self.questions_file.writelines(f"{que.question}\n")
            for option in que.options:
                self.questions_file.writelines(f"{option}\n")
            else :
                self.questions_file.writelines("\n")
            self.questions_file.flush()
            

    # ai models call functions
    def nlp_results(self, question):
        """fillups type question"""
        question = re.sub(r"[_|\.]{2,}", self.nlp.tokenizer.mask_token, question)
        res_list = self.nlp(question)
        # res_list = [res for res in res_list if res['score'] >= 0] # all more then equal to 50 % prediction
        res_list = [res for res in res_list if res['score'] >= self.AiConfirm_rate] # all more then equal to 50 % prediction
        if res_list:
            print(f" {bcolors.OKCYAN}From nlp AI -",end=f"{bcolors.ENDC}\n")
            for res in res_list:
                print(f" {bcolors.OKGREEN}{round(res['score']*100)}% --> {res['sequence']}",end=f"{bcolors.ENDC}\n")

    def qna_results(self, question, context=None, info=None):
        """qna for the question"""
        # use note and site data
        # print(context)
        if not context : # is None
            context = self.temp_data
        res = self.qna(question=question, context=str(context))
        # if res and res['score'] > 0 :
        if res and res['score'] > self.AiConfirm_rate :
            if info :
                print(f" {bcolors.OKCYAN}From {info} -",end=f"{bcolors.ENDC}\n")
            print(f" {bcolors.OKGREEN}{round(res['score']*100)}% --> {res['answer']}",end=f"{bcolors.ENDC}\n")


    # data extractor for ai files from pc
    def get_content_files(self):
        """return the files to read"""
        if os.path.isdir(self.path_to_content) :
            files_path = []     
            for root, dirs, files in os.walk(self.path_to_content):
                for name in files:
                    if fnmatch.fnmatch(name, '*.docx') or \
                            fnmatch.fnmatch(name, '*.pptx') or \
                        fnmatch.fnmatch(name, '*.pdf') or\
                            fnmatch.fnmatch(name, '*.txt'):
                        files_path.append(
                            Path(os.path.join(root, name))
                        )
            return files_path
        else :
            print(bcolors.FAIL,"Please Enter a valid path\n\t",\
                self.path_to_content,"NOT FOUND",bcolors.ENDC)
            return []
            

    def get_files_data(self):
        """extact the data from the content fields"""
        content_file_path = self.get_content_files()

        if content_file_path:
            print(f"\n{bcolors.OKGREEN} Reading files for the content.",
                  end=f"{bcolors.ENDC}\n")

        for index, file_path in enumerate(content_file_path):
            # read the file data and save it in teh temp file
            print(f"\t{bcolors.OKCYAN}{index + 1}. {os.path.basename(file_path)}",
                  end=f"{bcolors.ENDC}\n")
            self.temp_file.write(str(reader.get_text(file_path)).replace('\n', ' '))
            self.temp_file.seek(0)
            self.temp_file.flush()

    @property
    def temp_data(self):
        """get the tempfile data and sanitize it """
        if self.temp_file_data:
            return self.temp_file_data
        temp_res = self.temp_file.read()
        temp_res = re.sub(r"stdout \d{1,}", '', temp_res)
        temp_res = re.sub(r"stderr \d{1,}", '', temp_res)
        temp_res = re.sub(r"tdout \d{1,}", '', temp_res)
        temp_res = temp_res.replace('\\n', '')
        self.temp_file_data = temp_res.replace(' '*2, '')
        return self.temp_file_data

    # extract data from web and predict the results 
    def get_anwers_from_all_source(self,question):
        """give answer from the local system and 
        get the page from google and make prediction from that"""
        
        # from local file_system
        self.qna_results(question, info="local content")
            
        # get links from google 
        run = google(q= question)
        run.run_crawl()
        results = [ res['a'] for res in run.results \
            if not res['a'].startswith('https://www.youtube.com/')][:3]

        with ThreadPoolExecutor() as executor:
            executor.map(lambda x: \
                self.qna_results(
                    question,
                    context=self.get_page_text(x),
                    info=x),
                results)

    def get_page_text(self,url):
        html_soup = self.get_page(url)
        # delete out tags
        for script in html_soup(["script", "style"]):
            script.decompose()

        return "".join(list(html_soup.stripped_strings))
    
    # representaion working
    def show_answers(self):
        """show resutls to the user"""
        # show question
        for index, ques in enumerate(self.questions.keys()):
            print(f"{bcolors.WARNING}[Question:{index+1}] > \n{bcolors.OKBLUE}{ques.question}{bcolors.ENDC}")
            for op in ques.options:
                print(f"{bcolors.OKBLUE}{op}{bcolors.ENDC}")
            copy2clip(ques.question)
            print(f"{bcolors.OKCYAN}\tQuestion is copied to the clip-board.{bcolors.ENDC}")

            # show ai answer right away
            print(f"{bcolors.WARNING}", ">> >> >> ", f"{bcolors.OKGREEN}AI{bcolors.WARNING}",">> >> >> ", end=f"{bcolors.ENDC}\n")
            if re.match(r'[_|\.]{2,}', ques.question) :
                self.nlp_results(ques.question)
                print(f"{bcolors.WARNING}", ">> >> >> ", end=f"{bcolors.ENDC}\n")
            self.get_anwers_from_all_source(ques.question)
            print(f"{bcolors.WARNING}", ">> >> >> "*3, end=f"{bcolors.ENDC}\n")
            print()

            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}Press hot keys to see the next question results <{self.hot_hey}>.{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}\t\tor ctrl+c for next question.{bcolors.ENDC}")
            try:
                # on key press event
                keyboard.wait(f"{self.hot_hey}")
            except KeyboardInterrupt:
                # print("showing next question ")
                continue
            print(f"{bcolors.OKGREEN}showing pages{bcolors.ENDC}")
            self.open_searches(ques)

    @classmethod
    def runner(cls, sessionid, url, path_to_content):
        with cls(sessionid, url, path_to_content) as cl:
            cl.get_all_question()
            cl.save_questions()
            cl.show_answers()


if __name__ == "__main__":
    # update the sessionid from brower and url 
    sessionid = "" # example - '5gk1ti0t2e65qmgb0772snsdfl7'
    url = "" # example "https://lms.galgotiasuniversity.edu.in/mod/quiz/attempt.php?attempt=6314102&cmid=484157"

    sessionid = "ospj55eaturml9ql8golsfqv34" # example - '5gk1ti0t2e65qmgb0772snsdfl7'
    url = "http://127.0.0.1:5500/testing10qu.html?attempt=6349252&cmid=498254"
    
    # UPDATE path_to_content to the study material
    # path_to_content = 'C://Users//Rishabh Jain//Documents'
    path_to_content = 'G://class_stuff//'

    if not sessionid or not url or not path_to_content:
        raise Exception(f"{bcolors.FAIL}Update the value to use the program {bcolors.ENDC}")
        
    lms_quiz_ai.runner(
        sessionid,
        url,
        path_to_content
    )