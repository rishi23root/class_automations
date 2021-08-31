from scraper import TimeTable
from cloudAPI import calendar
from beautiful_date import D

# get data from the time table
def getAndPaint(userName,password,Email):
    data = TimeTable.getData(
        userName,password
    )

    # plot that data on the calendar
    if data : 
        Cal = calendar(Email)
    for clas in data:
        # 'date': '2021-08-31'
        date = clas['date'].split('-')
        time = clas['startTime'].split(':')
        starttime = (D @ int(date[2])/int(date[1])/int(date[0]))[int(time[0]):int(time[1])]
        meets = [i for i in clas['meetLink'] if i and len(i)>5 ] or ''
        discription = f"<h3>{clas['teacherName']}</h3>{clas['subjectCode']}-{clas['subject']}\n{meets}"

        Cal.createNewEvent(
            title=f"{clas['subject']} ({clas['batchCode']})",
            start=starttime,
            location=clas['location'],
            description=discription
        )

def clearCalender(Email):
    cal = calendar(Email)
    cal.clearCalendar('week')

if __name__ == '__main__':
    userName = '<your usernaem here>',
    password ='<your password here>'
    Email = "<your password here>"
    # clearCalender(Email)
    getAndPaint(userName,password,Email)