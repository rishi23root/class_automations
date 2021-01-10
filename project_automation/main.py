# python main.py
from docx import Document # pip install python-docx   
from docx.shared import Inches,Pt,RGBColor
from PIL import Image
import json
import os


class project_creator:
    def __init__(self,info_file):
        # file name saved 
        self.info_file = info_file

    def __enter__(self):
        self.extract_info()
        # start a new word file 
        self.document = Document()
        # use sections to edit page layout and margin
        sections = self.document.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        return self
    
    def __exit__(self ,type, value, traceback):
        # save the file at last
        self.document.save(self.file_name +'.docx')
        print(self.file_name," Saved 😁😀")
        return False

    def extract_info(self):
        # data file and read data and update class
        with open(self.info_file,'r',encoding="utf8") as info_file:
            info = json.load(info_file)
            self.file_name = info["file_name"]
            self.directory = os.path.normpath(info["directory"])
            self.userinfo = info["userinfo"]
            self.questions = info["data"]["questions"]
            self.files = info["data"]["files"]
            self.isHeading = info["format"]["heading"]
            self.block = info["format"]["data"]
            self.isEnd_name = info["format"]["end_name"]
           
    def file_reader(self,file_name):
        print(f'reading file => {file_name} 🕵️‍')
        # try except block for error 
        try:
            with open(file_name ,mode = 'r',encoding="utf8") as code:
                return code.read()
        except :
            raise Exception("file reading error -check file name and location (we are using encoding='utf8' for decoding)")

    def question(self,data):
        # add heading for questions
        que = self.document.add_heading(data, level=1)
        font = que.style.font
        font.size = Pt(20)
        font.color.rgb = RGBColor(0,0,0)
    
    def code(self,data):
        # sol
        ans = self.document.add_paragraph("")
        ans.add_run('Sol.').bold = True

        # add code to the doc
        code = self.document.add_paragraph(data)
        # indent for code
        paragraph_format = code.paragraph_format
        paragraph_format.left_indent = Inches(0.5)
        font = code.style.font
        font.size = Pt(14)
        font.color.rgb = RGBColor(0,0,50)
    
    def image(self,image):
        # add iamge to the doc
        # output
        output = self.document.add_paragraph("")
        output.add_run('output.').bold = True
        
        # image width and height of image
        w,h = Image.open(image).size
        self.page_lines += round(h/30)

        # big - 1920 1080  # idle - 700 _
        if w < 700:
            self.document.add_picture(image)
        else:
            self.document.add_picture(image,width=Inches(7.5))

    def data_block(self,question,code_data,ss):
        # write questions as heading in bold
        if self.block["question"] :
            self.question(question) # print(question)
            self.page_lines += 2

        if self.block["solution"] :
            self.code(code_data)  # print(code_data)
            self.page_lines += len(code_data.split('\n'))+1

        if self.block["picture"] : 
            self.image(ss)   # print(ss)
            # self.page_lines

    def create_file(self):
        # write file name at top in center
        if self.isHeading:
            heading = self.document.add_heading(self.file_name, 0)  # print(self.file_name)
            heading.alignment = 1
        self.page_lines = 3 
        for question,files in zip(self.questions,self.files):
            # question  # code = self.file_reader(files[0]) # ss = files[1]
            self.data_block(question,self.file_reader(files[0]),files[1])

            # add page break for every new question
            print(self.page_lines)
            if self.page_lines >= 28  and question != self.questions[-1]:
                self.document.add_page_break()
            
            self.page_lines = 0

        if self.isEnd_name:
            # add name of the student in the end the file 
            hr = self.document.add_paragraph("_____________________________________________________________________")
            hr.alignment = 1
            para = f'''Student : {self.userinfo["username"]}\nRoll No : {self.userinfo["ROLL NO"]}'''
            end_userinfo = self.document.add_paragraph(para)
            font = end_userinfo.style.font
            font.color.rgb = RGBColor(0,0,0)


    @staticmethod
    def open_file(file_name):
        # to open the fiel for results 
        print("opening file for checking ...")
        os.startfile(file_name+'.docx')

    @classmethod
    def runner(cls,info_file):
        with cls(info_file) as clas :
            # chnge dir to the directory
            os.chdir(clas.directory)
            print(f"Dir changed to {clas.directory}")

            # this will create file and save all the changes
            clas.create_file()
            file_name = clas.file_name
        
        # to open the after it saved
        cls.open_file(file_name)


if __name__ == "__main__":
    project_creator.runner("info.json")
