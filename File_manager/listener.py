from watchdog.observers import Observer # pip install watchdog
from watchdog.events import FileSystemEventHandler
import time , os
import sqlite3

class EventHandler(FileSystemEventHandler):
    '''to cleate logs of events in the database ,inherits from theFileSystemEventHandler class of the observer and
     takes prameter as the database nama to save '''
    ignore_src_extention = ['db-journal','tem','crdownload','tmp','ini'] # .tmp, .crdownload , .ini
    def __init__(self,database_name):
        self.database_name = database_name  
        # rename the old database
        name , ext = self.database_name.rsplit('.',1)
        old_name = "".join([name,'_old.',ext])    
        if os.path.exists(old_name):
            print(f"Deleteing the database")
            if input("can we delete the most oldest database :").upper() in ['YES',"y",'1']:
                os.remove(old_name)
            else:
                print("we can move forword either delete that database or rename it ....")
                exit()

        try:
            os.rename(self.database_name,old_name)
            print(f"old database is Renamed to {old_name}")
        except : pass
        finally: print("Creating new Local Database...")

        self.database = sqlite3.connect(self.database_name,check_same_thread=False)
        self.cursor = self.database.cursor()

        print('setup Database')
        # create table in database
        self.cursor.execute('''CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                isDir BLOB,
                src TEXT,
                target TEXT,
                time REAL,
                folder TEXT
                );''')
        print('creating tables in Database')
        self.database.commit()

    def close(self):
        # save any unsaved changes
        self.database.commit()
        # close all the open files
        self.database.close()
        print('Local Database closed and saved successfully.')

    def new_entry(self,values):
        # value example ('type',isDir,'src/','to location',1234567)
        New_entry_query = "INSERT INTO events (type,isDir,src,target,time) VALUES ( ?, ?, ?, ?,?)"
        self.cursor.execute(New_entry_query, values)
        self.database.commit()
    
    def sanitized_save(self,data):
        # simplify the event reading and return only useful data
        # dir(event) => 'event_type', 'is_directory', 'is_synthetic', 'key', 'src_path'
        # , is_directory = data.is_directory,src_path = data.src_path
        event_type = data.event_type
        src_path = data.src_path
        key = data.key

        # value example (type,isDir,src,target,time,folder)
        if event_type == 'moved' : 
            values = (key[0],key[-1],key[1],key[2],time.time())
            # excepting files with specific extention 
            try: 
                if "$RECYCLE.BIN" in key[1] or key[2].rsplit('.',1)[1] in self.ignore_src_extention : return
            except : pass
            print(f"{key[0]}- {key[2]}") 
        else : 
            isdir = 1 if os.path.isdir(key[1]) else 0
            values = (key[0],isdir,key[1],'',time.time())
            # excepting files with specific extention 
            try: 
                if "$RECYCLE.BIN" in key[1] or key[1].rsplit('.',1)[1] in self.ignore_src_extention : return
            except : pass
            print(f"{key[0]}- {key[1]}") 
        
        self.new_entry(values)        

    def on_modified(self, event):
        # update the file name in json if change
        # print("on_modified")
        # there is no need of update odifications 
        pass
    
    def on_created(self, event):
        self.sanitized_save(event)

    def on_deleted(self, event):
        self.sanitized_save(event)

    def on_moved(self,event):
        self.sanitized_save(event)        
    
    @staticmethod
    def pathSenitization(listing_folders):
        # make directory path readable for program and remove / from end if exist. 
        paths = []
        for path in listing_folders :
            # path = [ p for p in path.replace('/','\\').split('\\') if p != '']
            if len(path) > 1 : path = '\\'.join([ p for p in path.replace('/','\\').split('\\') if p != ''])
            if os.path.isdir(path) : paths.append(path)
            else : print("path reject check again : ",path)
        return paths

def Listener(path_list,database_name):
    '''use EventHandler loging and observer to listening the events of the systems'''
    paths  = EventHandler.pathSenitization(path_list)
    # initialized the database
    event_handler = EventHandler(database_name)
    observer = Observer()
    observer_list = []

    for path in paths:
        print("listening - ",path)
        # Schedules watching of a given path
        observer.schedule(event_handler, path,recursive=True)
        # Add observable to list of observer_list
        observer_list.append(observer)
    else :
        print("all given paths are active for listening...  PRESS (ctrl + c ) to stop")
        observer.start()
        # for ob in observer_list : ob.start()

    try : 
        while True : time.sleep(5)
        # raise error if wanna use to 
    except KeyboardInterrupt:
        # close the database and save changes
        event_handler.close()
        print('stoping the process PRESS-> (ctrl + c ) to stop')
        # for different methods of closing functions don't use keyboardInterrupt. 
        # stop observer if interrupted
        observer.unschedule_all()
        for o in observer_list : o.stop()
    
    # Wait until the thread terminates before exit
    for o in observer_list : o.join()

if "__main__" == __name__:
    # testing data 
    listing_folders = [
        'C:\\Users\\risha\\Downloads',
        'C:\\Users\\risha\\pictures\\',
        'C:/Users/risha/videos',
        'C:\\Users\\risha\\documents',
        'E:\\',
        'D:/class_automations/watch/',
        'C:\\Users\\risha\\desktop'
    ]
    Listener(listing_folders,'File_manager.db')
