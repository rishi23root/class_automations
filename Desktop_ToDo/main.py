# main.py
# pip install py-wallpaper pillow
import json
from PIL import Image, ImageDraw, ImageFont
import os,datetime
from wallpaper import set_wallpaper
# for more info - https://pythonprogramming.altervista.org/make-an-image-with-text-with-python/ , https://www.geeksforgeeks.org/build-an-application-for-changing-pcs-wallpaper-using-python/

class toDo:
	# aim - to make to-do desktop background
	def __init__(self,max_events = 10):
		self.file_name = "ToDo.json"
		# open(file_name,'w').close() # to create the file if not exist
		today = datetime.datetime.now().strftime("%d/%b/%Y")
		self.heading = f"TO-DO ({today}) :-"
		self.max_todo = max_events
		self.work_list = ""
		self.image_name,self.w,self.h = "desktop_bg.jpg",1920,1080
		
	def read_json_file(self):
		# 1. read json files to read task
		with open(self.file_name) as f:
			# 1.1 extact data
			data  = json.load(f)
			todoList = data["ToDos"]
			# 1.2 the list are empty close the program and show that
			if todoList == [] :
				print("\nNothing to show here\n")
				return False
			else :
				for index,to in enumerate(todoList,1):
					if index == self.max_todo + 1 : 
						print(f"\nIt only show first {self.max_todo} for better visibility.\n")
						break 
					index = str(index).zfill(2)
					# wraping words
					if len(to) > 40 :
						a = to[35:].split(' ',1)
						a= '\n      '.join(a)
						to = to[0:35] + a 

					self.work_list += f"{index}. {to}\n"
				return True

	def create_save_image(self):
		# 2. create the image and save the images
		# create image
		image = Image.new(mode = "RGB", size = (self.w,self.h) ,color = "white")
		draw = ImageDraw.Draw(image)

		# draw text heading and events
		fnt = ImageFont.truetype('arial.ttf', 60)
		center_width = self.w/2 - len(self.heading)*16  # time of the normal length
		draw.text((center_width,200), self.heading, font=fnt, fill=(0,0,0))

		fnt = ImageFont.truetype('arial.ttf', 45)
		draw.text((center_width,270), self.work_list, font=fnt, fill=(0,0,0))

		image.save(self.image_name) # save file
		# os.system(self.image_name) # show file

	def set_bg(self):
		# 3. set the image to the background
		set_wallpaper(self.image_name)

	@classmethod
	def runner(cls,max_events = 10):
		c = cls(max_events)
		if c.read_json_file():
			c.create_save_image()
			c.set_bg()

if __name__ == '__main__':
	toDo.runner()