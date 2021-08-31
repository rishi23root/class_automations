from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA
from beautiful_date import hours, D, days
from pathlib import Path


class calendar:
    def __init__(self,
                 userEmail: str,
                 credentials_path: Path = './credentials.json'):
        """initilize the login for access calender if not already
        :param userEmail:
            Email of the user used in the authentication
        :param credentials_path:
            Path of the credentials_path json file which we downloaded form the api of the GCC(google cloud console)        
        """
        self.calendar = GoogleCalendar(
            userEmail,
            credentials_path=credentials_path
        )

    # create new event

    def createNewEvent(self,
                       title: str,
                       start,
                       Nhours: int = 1,
                       description: str = None,
                       location: str = None,
                       attendees=None
                       ):

        # may update for https://google-calendar-simple-api.readthedocs.io/en/latest/attachments.html
        """create new event and save to the calendar
        :param title:
            title for the event 
        :param start:
            starting time of the event 
        :param Nhours:
            number of hours in int to put this event defautl is one-1
        :param description:
            Description of the event. Can contain HTML.
        :param location:
            Geographic location of the event as free-form text.
            but can take any string without any issue like `online` 
        :param attendees:
            Attendee or list of attendees.
            Each attendee given as email string.
        """
        end = start + Nhours*hours
        print("New event is created at", start)
        self.calendar.add_event(
            event=Event(
                title,
                start=start,
                end=end,
                description=description,
                location=location,
                attendees=attendees
            )
        )

    # fetch data

    def getFiltedEvents(self, start, end, starttimeORupdated=None):
        """return ids for the events filter form the params
        :param start end:
            time of the event to use in the filter
        :param starttimeORupdated:
            starttime OR updated filters values 
        """
        return [
            i for i in self.calendar.get_events(
                start,
                end,
                order_by=starttimeORupdated
            )
        ]

    def getEventBetween(self, start, nextNdays=0):
        """
        return list of events between the time
        :param start:
            time of the event to use in the filter
        :param nextNdays:
            Number of days to get events of
        """
        if nextNdays >= 0:
            assert "nextNdays should be greater then or equl to 0"
        end = start + nextNdays*days
        # print(start, end)
        return self.getFiltedEvents(
            start,
            end
        )

    # remove data

    def clearEvents(self, events: list = []):
        """take list of events list id to remove form the calender
        :param events:
            list of events to remove 
        """
        # clear all the events from the borwser
        [self.calendar.delete_event(event) for event in events]

    def clearCalendar(self, till="today"):
        """remove all the events from today to till
        collect all the elements till and remove then onebyone
        :param till:
            today or week(include today and next 6 days)"""
        today = D.today()
        if till == "today":
            to = today
        elif till == "week":
            to = today + 6*days
        # print(today,to)
        self.clearEvents(
            events=self.getFiltedEvents(
                today,
                to
            )
        )

    # represent data

    def showNextOrGivenEvents(self, events: list = []):
        """just display all future events in the colender or from param list\
        :param events:
            list of events to show  
        """
        [print(event) for event in (events or self.calendar)]


if __name__ == '__main__':
    # change it to your email if running this file 🥇
    a = calendar("rishabhjainfinal@gmail.com")
    a.clearCalendar('today')
    a.createNewEvent(
        "tesing for first time",
        D.today()[2:00], 1.5
    )
    # a.showNextOrGivenEvents()
    # print(a.getEventBetween(D.today()))
