import webbrowser as web
import pyautogui
import json
import schedule
import time
import re,os
from time import sleep as nap

def get_json_data(filename='info.json'):
    jsondata = json.load(open(filename))
    return sorted(jsondata['classes'],key=lambda x:x['join_time'])

def schedul_classes():
    for _class in get_json_data():
        class_code = _class['code']
        start_time = _class['join_time']
        end_time = _class['end_time']
        day = _class['day']
        getattr(schedule.every(),day.lower()).at(start_time).do(join_class,class_code,start_time,end_time)
        print("\tScheduled class '%s' on %s at %s"%(class_code,day,start_time))

def time_in_sec(time_str):
    return sum([a*b for a,b in zip(
        [3600,60],
        map(int,time_str.split(':'))
        )
    ])
     
def join_class(class_code,starttime,endtime):
    url = f"https://meet.google.com/{class_code}"
    print("starting meeting -",url)
    web.open(url)
    # wait buttons appear

    r = re.compile(f"Meet - {class_code} .+")
    window_name = ([ele.string for ele in [re.match(r,win) for win in  pyautogui.getAllTitles()] if ele ] or [''])[0]
    # maximise the window
    pyautogui.getWindowsWithTitle(window_name)[0].maximize()
    # change the focus to the chrome and bring it in focus 
    pyautogui.getWindowsWithTitle(window_name)[0].activate()
    
    # find buttons to close the camera and mike 
    nap(2.5)
    dismissPoint = pyautogui.locateCenterOnScreen(os.path.join('finder','dismiss2.PNG'),confidence=0.7) 
    pyautogui.click(dismissPoint.x or None,dismissPoint.y or None)
    nap(0.2)

    try :
        # try to dismiss the browser notification for open camera and mike permissions
        blockPoint = pyautogui.locateCenterOnScreen(os.path.join('finder','block.PNG'),confidence=0.7) 
        pyautogui.click(blockPoint.x or None,blockPoint.y or None)
    except : pass

    # joining
    try :
        joininPoint = pyautogui.locateCenterOnScreen(os.path.join('finder','joinin.PNG'),confidence=0.7)
        pyautogui.click(joininPoint.x or None,joininPoint.y or None)
    except AttributeError :
        nap(1)
        joininPoint = pyautogui.locateCenterOnScreen(os.path.join('finder','joinin.PNG'),confidence=0.5)
        pyautogui.click(joininPoint.x or None,joininPoint.y or None)
    except :
        print("Button not found ")
        return

    # sleep for class run time
    time_to_sleep = time_in_sec(endtime)-time_in_sec(starttime)
    a = divmod(time_to_sleep,60)
    print("Going to sleeo for next :",":".join(map(str,[a[1],*divmod(a[0],60)[::-1]][::-1])),"hours")
    nap(time_to_sleep)

    # leaving
    try :
        joininPoint = pyautogui.locateCenterOnScreen(os.path.join('finder','leave.PNG'),confidence=0.7)
        pyautogui.click(joininPoint.x or None,joininPoint.y or None)
    except : pass
    finally :
        # close the tab
        pyautogui.keyDown('ctrl')  # hold down the ctrl key
        pyautogui.press('w') 
        pyautogui.keyUp('ctrl')  # hold down the shift key
        print()
        print()
        
# join_class('rvz-xypz-buu','00:57','00:58')

# starting process
print("\nscheduling classes \nPlease don't use this device while running this program\n\n")
schedul_classes()
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("closing program, bye-bye!")