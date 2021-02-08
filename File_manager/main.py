# python main.py
import time,os,sqlite3,datetime,json
# pip install watchdog 
from listener import EventHandler,Listener
from Teleporter import Teleporter
from pathlib import Path

class supervisor:
    '''this class is responsible for the using all the modules and 
    senitization of the events and returing of the final moving path'''
    def __init__(self ,database_name =  'File_manager.db'):
        # open database and read database and santize the data
        self.database_name = database_name
    
    def __enter__(self):
        # initalize the database
        self.database = sqlite3.connect(self.database_name,check_same_thread=False)
        self.cursor = self.database.cursor()
        print('connected to database')
        return self
    
    def __exit__(self,a,b,c):
        # close the database
        self.database.close()
        print('closing database.')
        # add after testing function to remove the local database file
        self.remove_database()

    def remove_database(self):
        # use to delete the file after tranfering of the filea and reading all data 
        print("Deleting the local database file.....  ",end=' ')
        try:
            os.remove(os.path.join(os.getcwd(),self.database_name))
            print("done file removed")
        except Exception as e:
            print(f"\n Error in removing the file \n have error ==> {e}")
                
    def read_database(self,_return = [],filters = ''):
        # return tuple
        if _return == [] : values = '*'
        else :values = ','.join(_return) 
        
        # filter
        if filters : filter_str = 'WHERE ' + filters
        else : filter_str = ''

        search_query = f"SELECT {values} FROM events {filter_str}"
        # print(search_query)
        
        try : return iter(self.cursor.execute(search_query))
        except : return []
    
    def delete_entry(self,_id):
        # to remove a row to moved files or folder
        sql_delete_query = f"DELETE from events where id = {_id}"
        self.cursor.execute(sql_delete_query)
        self.database.commit()

    def action(self):
        # [print(a) for a in list(self.read_database())]

        # 0 remove the file which are moved after creation 
        # for moved_entry in list(self.read_database(_return=[],filters = f" type = 'moved' ")) : 
        #     _return,filters = [],f"type = 'created' "
        #     for created_entry in self.read_database(_return,filters) : 
        #         if created_entry[3] == moved_entry[3]  :
        #             # print(created_entry[0])
        #             self.delete_entry(created_entry[0])

        # # 1. delete the delete events "we cannot compair from the other events here because it is possible to have deleted events fist and other events later and yes we use time to compair but it possible that may be this poscess is happen multiple time in the mean time"
        # _return,filters = [],f"type = 'deleted' "
        # for entry in self.read_database(_return,filters) : 
        #     self.delete_entry(entry[0])

        # # 2.remove the duplicate files made by video files 
        # to_del_id = []
        # for event_l1 in list(self.read_database()):
        #     for event_l2 in list(self.read_database()):
        #         if event_l1[0] != event_l2[0] and event_l1[3] == event_l2[3]:
        #             to_del_id.append(event_l2[0])
        # else : 
        #     for i in to_del_id : self.delete_entry(i)

        # 3. create a directory system for all the listening directories with all sub directory of listend events 
        # if past is a valid path       
        Listing_dict = {}
        for event in self.read_database() :
            event = list(event)
            for listin in listing_folders:
                if event[1] == 'moved' and event[4].startswith(listin):
                    if not os.path.exists(event[4]) : continue
                    event[4] = event[4].replace(listin,'')
                    if listin in list(Listing_dict.keys()):
                        Listing_dict[listin].append(event)
                    else : 
                        Listing_dict[listin] = [event]
                elif event[1] == 'created' and event[3].startswith(listin):
                    if not os.path.exists(event[3]) : continue
                    event[3] = event[3].replace(listin,'')
                    if listin in list(Listing_dict.keys()) : 
                        Listing_dict[listin].append(event)
                    else : 
                        Listing_dict[listin] = [event]
        else:
            # sort for the event according to the transfer rate
            def sort_fun(event):
                if event[1] == "moved" : return len(event[4])
                else : return len(event[3])

            for key in Listing_dict:
                # len of the path
                Listing_dict[key] = sorted(Listing_dict[key], key= lambda l : sort_fun(l)) 
                # is directory
                Listing_dict[key] = sorted(Listing_dict[key], key= lambda l : not l[2] )

        # for i in Listing_dict:  # for debuging
        #     print(i)
        #     for j in Listing_dict[i] :
        #         print("\t",j)

        # 4. return all the paths to move  
        to_move = []
        def get_action_src(parent,events):
            # give the path of the event to use
            srcs = []
            if type(events) != list : list_of_event = [event]
            else : list_of_event = events
            for event in list_of_event:
                if event[1] == 'moved' : 
                    if event[4].startswith('\\') : event[4] = event[4].replace('\\','',1)
                    srcs.append(os.path.join(parent,event[4]))
                else : 
                    if event[3].startswith('\\') : event[3] = event[3].replace('\\','',1)
                    srcs.append(os.path.join(parent,event[3]))
            else : return srcs
        for key,value_list in zip(Listing_dict.keys(),Listing_dict.values()):
            # print(f"working on dir - {key}")
            to_move += get_action_src(key,value_list)

        return to_move

    @classmethod
    def sanitizer(cls,database_name):
        # it takes database name with extention
        with cls(database_name=database_name) as r :
            return r.action()
    
    @classmethod
    def runner(cls,database_name:str,listing_folders:list,destination):
        # it takes database name without extention
        database_name = database_name.replace('.','') + '.db'
        # for listening and saving events 
        Listener(listing_folders,database_name)

        To_move = cls.sanitizer(database_name)
        # To_move = []  # for testing 

        # to move the events 
        if To_move:
            os.chdir(destination)
            # today
            destination = os.path.join(destination,today)
            if not os.path.exists(destination):
                os.mkdir(destination)
            
            try : 
                class_name = input("\n\nEnter the name of the class to save data :") + '-' + each_class_time 
            except KeyboardInterrupt: 
                class_name = 'undefine-' + each_class_time[:2] + '-' + each_class_time 

            destination = os.path.join(destination,class_name)
            print("working on -")
            [print("\t",a) for a in To_move]
            for path_src in To_move:
                # print(path_src)
                if ":\\" not in path_src : 
                    path_src = path_src.replace(':',':\\')
                if os.path.isdir(path_src):
                    source,file_name = path_src.rsplit('\\',1)
                    # print("\tdir ",path_src) print(source,destination,file_name)
                    Teleporter.Directory(source,destination,file_name,rename = False)
                elif os.path.isfile(path_src):
                    source,file_name = path_src.rsplit('\\',1)
                    # print("\tfile ",path_src) (source,destination,file_name)
                    Teleporter.File(source,destination,file_name)   
        else :
            print("Nothing to work on..")

        print("\n\t\tProgram ended...")

now = datetime.datetime.now()
today = now.strftime("%d-%m-%Y-%a")
each_class_time = now.strftime("%H_%M")

if __name__ == "__main__":
    # for json fiel extract saving_directory,listing_folders
    with open('info.json') as f : data = json.load(f)

    saving_directory = data["SAVING_DIRECTORY"]
    listing_folders = data["Listing_folder"]

    home = str(Path.home())
    
    if saving_directory[:2] not in ['C:','E:','D:','E:','F:','G:']:
        saving_directory = os.path.join(home,saving_directory)

    saving_folder = os.path.join(saving_directory,"CLASSES")
    if not os.path.exists(saving_folder) : os.mkdir(saving_folder)

    listing_directory = []
    for path in listing_folders:
        if path[:2] not in ['C:','E:','D:','E:','F:','G:']:
            path = os.path.join(home,path)
        listing_directory.append(path)
    
    listing_folders = EventHandler.pathSenitization(listing_directory)
    destination = saving_folder
    supervisor.runner('File_manager',listing_folders,destination)
