import pyautogui
import os 
from time import time, perf_counter,sleep as nap
from win10toast import ToastNotifier
import argparse

class writter:
    def __init__(self, text: str=None, file_name: str = 'data.txt', show_notification:bool = True ):
        """
        text      : str      write only text in the string
        file_name : str      write the text in the file
        show_notification : bool      to see notification at the program end
        """
        if text :
            self.to_write = text
        else :
            if os.path.isfile(file_name):
                with open(file_name) as fi:
                    self.to_write = fi.read()
            else :
                raise Exception(f"File not found : {file_name}")
        
        self.nap_time = 4 # time given to place the cursor 
        self.charSpaceTime = 0.015 # time between each char typed
        self.show_notification = True 

    def __enter__(self):
        print('\tInitializing the WRITTER')
        print('FAIL-SAFE is on the left of the screen (take your mouse there to stop the program)')
        self.start_time = perf_counter()
        return self
    
    def __exit__(self, a, b, c):
        time_taken = round(perf_counter() - self.start_time,2)
        if self.show_notification :
            print('time_taken : ',time_taken,'seconds')
            self.push_notification(
                title="Writter notify",
                message=f"Task Completed successfully in {time_taken} seconds."
            )
    
    def push_notification(self, 
                        title, 
                        message, 
                        duration = 3, 
                        icon_path = "type.ico" ):
        # createing notification box
        toaster = ToastNotifier()
        toaster.show_toast(title,message,icon_path=icon_path,duration=duration)

    def writeText(self):
        """write the char to the screen"""
        print(f"\n\nSleeping for {self.nap_time} seconds put you cursor to the possition\n")

        nap(self.nap_time)
        
        try :
            pyautogui.write(
                self.to_write,
                interval=self.charSpaceTime
            )
        except :
            print("\t\tExiting the program")
            print("FAIL-SAFE trigered")
            self.show_notification = False
            exit()

    @classmethod
    def runner(cls,
                text: str = None,
                file_name: str = 'data.txt',
                show_notification:bool = True):

        with cls(text=text, file_name=file_name, show_notification=show_notification) as typer :
            # start witting 
            typer.writeText()

# examples:
# python3 main.py -f .\README.md
# python3 main.py -t "this the way"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--text', default=None, help = "String to write.")
    parser.add_argument('-f','--file', default='data.txt', help = "file to read from. (default=data.txt).")
    args = parser.parse_args()
    # print(args)
    if args.text:
        writter.runner(text=args.text)
    else :
        writter.runner(text=args.text,file_name=args.file)
