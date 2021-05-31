import os 
import textract

class reader:
    """return the file raw text"""
    def get_text(filename):
        if os.path.exists(filename):
            try:
                return textract.process(filename)
            except :
                if __name__ == "__main__":
                    print('make sure file is is .pptx, .docx or etc.')
        if __name__ == "__main__":
            print(filename, "file not found.")
            
        return ''

if __name__ == "__main__":
    print(reader.get_text('a.pptx'))