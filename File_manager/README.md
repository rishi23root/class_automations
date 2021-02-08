# FILE MANAGER
This program is useful when you wanna MANAGER your class FILES 

because when the class start we don't make folders for notes files and take many screenshots ,record videos and download files  which all are save in differnt folders and finding the specific files after the class and re-arrange them its to much work and time consuming so with the help of this program we can automate the this process.

## working 
This program will listen to the every event('created','moved','deleted') which happen in the the listing folders and save in a local database in your pc and when u done with the listening press `ctrl + c` to stop listening and provide the name of the class to save all the data.
 
YOU can changer the listening folder in `info.json` all the path should be absolute or windows default folders names
```info.json
"SAVING_DIRECTORY":"desktop",
"Listing_folder":[
    "Downloads",
    "pictures",
    "documents",
    "desktop",
    "videos",
    "E:\\"
    ]
```
## complete requirements
  - copy the command and run `pip install watchdog shutil`

# steps to using this program after cloning repo
  - cd File_manager
  - run the python program like this `python main.py` 
Then give the asked values and thats it.

## alert
videos files may take some time to download,

if not download completely program raise error of permission denied.

so make sure all the files are sucessfull downloaded and saved.
