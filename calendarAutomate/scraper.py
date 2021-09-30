from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from beautiful_date import D, days
from time import sleep as nap
import requests


class TimeTable():
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.url = "http://gu.icloudems.com/"
        options = Options()
        options.add_argument("--log-level=0")
        options.headless = True

        print("setup drivers", end='')
        try:
            self.driver = webdriver.Chrome(
                executable_path='./chromedriver.exe',
                options=options)
        except Exception as e:
            raise Exception("Error in chromedriver.exe path",e)
        print(" ..successful")
        self.logedin = False

        # login here
        self.login()

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        if self.logedin:
            print("loging out ...", end='')
            self.driver.get("https://gu.icloudems.com/corecampus/logout.php")
            print(" Done")
            self.driver.quit()
        else:
            print("Not even initized the and ended🤣")

    def login(self):
        print(f"opening {self.url }")
        self.driver.get(self.url)

        username_input_xpath = '//*[@id="useriid"]'
        password_input_xpath = '//*[@id="actlpass"]'
        self.execute_when_element_on_screen(self.driver, username_input_xpath)

        user = self.driver.find_element_by_xpath(username_input_xpath)
        password = self.driver.find_element_by_xpath(password_input_xpath)

        user.send_keys(self.user)
        password.send_keys(self.password)

        button_xpath = '//*[@id="psslogin"]'
        login = self.driver.find_element_by_xpath(button_xpath)
        self.execute_when_element_on_screen(self.driver, button_xpath)
        nap(0.5)  # if having error in bg to load
        login.click()
        self.logedin = True

    def getTimeTable(self):
        turl = "https://gu.icloudems.com/corecampus/student/schedulerand/tt_report_view.php"
        print("opening -", turl)
        self.driver.get(turl)
        cookies = self.driver.get_cookies()
        return self.getTimeTableJSON(cookies)

    def getTimeTableJSON(self, cookies={}):
        return self.getTimeTableByRequest(cookies)  # success -  2/7

    def getTimeTableByRequest(self, cookies={}):
        tturl = 'https://gu.icloudems.com/corecampus/student/schedulerand/ctrl_tt_report.php'
        startDate = D.today()
        endDate = startDate + 6*days
        year = startDate.year

        # ttheader specific header for this request
        ttheader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '''" Not A;Brand";v="99", "Chromium";v="92"''',
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json; charset= UTF-8",
            'Referer': "https://gu.icloudems.com/corecampus/student/schedulerand/tt_report_view.php",
            'Origin': "https://gu.icloudems.com",
            'Accept-Language': "en-US,en;q=0.9",
            'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="92"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }

        jsonData = {
            "method": "getData",
            "action": "wdefault",
            "startDate": f"{startDate}",
            "endDate": f"{endDate}",
            "empid": "",
            "room": "",
            "acadyr": f"{year}-{year+1}"
        }

        cookiesListToUse = {i['name']: i['value'] for i in cookies}

        r = requests.post(
            url=tturl,
            headers=ttheader,
            cookies=cookiesListToUse,
            json=jsonData,
        )

        try:
            if r.status_code:
                return r.json()
            else:
                return {}
        except:
            raise Exception("Unable to process Data. not JSON 😞")

    def execute_when_element_on_screen(self, driver, xpath, time=10):
        # print(xpath)
        WebDriverWait(driver, float(time)).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

    @classmethod
    def runner(cls, *args, **kargs):
        with cls(*args, **kargs) as a:
            return a.getTimeTable()

    @staticmethod
    def NormalizeData(jsonData):
        # convert to more useabl able form start date and time its discription with end time
        if jsonData == []:
            return []
        returnArry = []
        for _day, timeList in jsonData['NEWTT'].items():
            # print('On -',_day)
            a = [list(end.values())[0][0] for end in timeList.values()]
            for cls in a:
                returnArry.append({
                    "division": cls["division"],
                    "date": cls["fromDate"],
                    "startTime": cls["fromtime"],
                    "endTime": cls["totime"],
                    "subjectCode": cls["sub_shortname"],
                    "subject": jsonData['newsubarr'][cls["sub_shortname"]],
                    "teacherName": cls["empFName"].strip(),
                    "batchCode": cls["batch_name"],
                    "location": cls["roomno"],
                    "meetLink": [
                        cls["meeting"],
                        cls["meetingbb"],
                        cls["defaultmeeting"]
                    ]
                })
        # example ele
        #  {'batchCode': 'MATH2300-Section-8',
        #     'date': '2021-09-02',
        #     'division': 'Section-8',
        #     'endTime': '12:30',
        #     'meetLink': [None, None, '0'],
        #     'startTime': '11:30',
        #     'subject': 'Numerical Methods',
        #     'subjectCode': 'MATH2300',
        #     'teacherName': 'KUMAR PRADEEP'},
        return returnArry

    @staticmethod
    def getData(*args, **kargs):
        jsondata = TimeTable.runner(*args, **kargs)
        return TimeTable.NormalizeData(jsonData=jsondata)


# for testing
# with open('res.json') as f :
#     r = TimeTable.NormalizeData(jsonData=json.loads((f.read())))
#     pprint(r)
if __name__ == "__main__":
    print(TimeTable.runner(
        '<your usernaem here>',
        '<your password here>'
    )
    )
    # TimeTable.getData(
    #      '<your usernaem here>',
    #     '<your password here>'
    # )
