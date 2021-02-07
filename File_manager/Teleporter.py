import datetime
import os,time,uuid,shutil 

class Teleporter:
    '''to move the files and folders around'''
    # responsible for all the moving of files 
    def __init__(self,source,destination,file_name = None ,directory = None,rename = False):
        if file_name or directory : self.file_name ,self.directory_name = file_name , directory 
        else : raise Exception("File or Directory name cannot be empty.")
        
        # source and destination paths
        self.source ,self.destination ,self.rename = source, destination, rename
        if self.source == self.destination : raise Exception('Source and Destination cannot be same.')
        if directory and self.absolute_path(self.source,self.directory_name) == self.destination : 
            raise Exception('You cannot move a folder into the same folder.')

        # check if source directory exists
        if not os.path.exists(self.source) : raise Exception(f"Directory {self.source} not found ")
        
        # check destination folder exist if does not then crate one
        if not os.path.exists(self.destination) : os.mkdir(self.destination)

    def name_with_suffix(self,rename = False):
        # use file creation time in the suffix
        try :
            # file
            name,extention = self.file_name.rsplit('.',1)
            extention = '.' + extention
            # name - time_of_last modification . exetention 
            if self.rename or rename:
                mtime = str(datetime.datetime.fromtimestamp(os.stat(self.absolute_path(self.source,self.file_name)).st_ctime)).split(' ')[1].split('.')[0].replace(':','_') 
                return name  + '-'  +  mtime[:5] + '-' + str(uuid.uuid4())[:8] + extention
            return name + extention
        except AttributeError :
            # dir
            name = self.directory_name
            if self.rename or rename :
                mtime = str(datetime.datetime.fromtimestamp(os.stat(self.absolute_path(self.source,self.directory_name)).st_ctime)).split(' ')[1].split('.')[0].replace(':','_') 
                return name  + '-'  +  mtime[:5] + '-' + str(uuid.uuid4())[:8] 
            return name
        except Exception as e : raise Exception(e)

    def absolute_path(self,directory,name,*args):
        # returns file absolute path
        return os.path.join(directory,name,*args)

    def move_file(self):
        # move file to the destination and show error if any "Name explanatory"
        _from = self.absolute_path(self.source,self.file_name)
        _to = self.absolute_path(self.destination,self.name_with_suffix())
        try: 
            # first check if already exist 
            if os.path.exists(_to):
                _to = self.absolute_path(self.destination,self.name_with_suffix(rename = True))
                shutil.move(_from,_to)
                new_file_name = _to.rsplit('\\',1)[1]
                print(f"{self.file_name} -> File Moved successfully as {new_file_name} .")
                self.renamed_name = new_file_name
            else:
                shutil.move(_from,_to)
                print(f"{self.file_name} -> File Moved successfully.") 
                self.renamed_name = self.file_name
        except PermissionError : raise Exception("Permission denied.") 
        except Exception as e : raise Exception(e)

    def move_dir(self):
        # moving the directory
        try :
            _from = self.absolute_path(self.source,self.directory_name)
            _to = self.absolute_path(self.destination,self.name_with_suffix())

            if os.path.exists(_to):
                _to = self.absolute_path(self.destination,self.name_with_suffix(True))
                shutil.move(_from,_to)
                new_file_name = _to.rsplit('\\',1)[1]
                print(f"{self.directory_name} Directory moved sucessfully as {new_file_name}.")          
                self.directory_name = new_file_name
            else :
                shutil.move(_from,_to)
                print(f"{self.directory_name} Directory moved sucessfully .")
        except PermissionError : raise Exception("Permission denied.") 
        except Exception as e : raise Exception(e)
        finally:
            self.renamed_name = self.directory_name

        # rename the child file is user actated rename true 
        if self.rename :
            for file_name in os.listdir(_to):
                name ,extention = file_name.rsplit('.',1)
                absolute_file_path = self.absolute_path(_to,file_name)
                mtime = str(datetime.datetime.fromtimestamp(os.stat(absolute_file_path).st_ctime)).split(' ')[1].split('.')[0].replace(':','_') 
                new_file_name = name  + '-'  +  mtime[:5]  + '.' + extention
                shutil.move(absolute_file_path,self.absolute_path(_to,new_file_name))
                print(file_name)

    @classmethod
    def File(cls,source,Destination,file_name,rename= False ):
        T = cls(source,Destination,file_name = file_name,rename = rename)
        print(f"\nTeleporting File {file_name} - from {source} to {Destination}")
        T.move_file()
        return T.renamed_name 
    
    @classmethod
    def Directory(cls,source,Destination,dir_name,rename = False):
        T = cls(source,Destination,directory = dir_name,rename = rename)
        print(f"\nTeleporting Folder {dir_name} - from {source} to {Destination}")
        T.move_dir()
        return T.renamed_name 

if __name__ == "__main__":
    # testiing data
    source      = 'D:\\class_automations\\watch'
    destination = os.path.join('D:\\class_automations\\watch',"a")
    _name = "b" # file or directory name

    # making directory for testing
    if not os.path.exists(destination) : 
        os.mkdir(destination)
    if not os.path.exists(os.path.join('D:\\class_automations\\watch',"b")):
        os.mkdir(os.path.join('D:\\class_automations\\watch',"b"))

    # Teleporter.File(source,destination,_name)
    Teleporter.Directory(source,destination,_name,rename = False)