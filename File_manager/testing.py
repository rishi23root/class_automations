import os
from time import sleep as nap
import shutil

# just for the testing 

os.chdir('C:\\Users\\risha\\desktop')
print(f"enter into {os.getcwd()}")

os.mkdir("b")
nap(0.1)
os.mkdir("b\\c")
nap(0.1)
os.mkdir("b\\d")
open("a.txt",'w')
nap(0.1)

os.mkdir("a")
shutil.rmtree("b", ignore_errors=True)
nap(0.1)
os.mkdir("a\\b")
nap(0.1)
open("a\\a.txt",'w')
os.rename("a","renamed")

os.mkdir("c")
nap(0.1)
open("c\\a.txt",'w')
os.mkdir("c\\a")
