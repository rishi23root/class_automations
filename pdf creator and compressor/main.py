from PIL import Image
import os,math,argparse,random
from time import sleep as nap
# pip3 install PyMuPDF Pillow

class pdf:
    '''This class is can create pdf from the given images ,compress a exiting pdf,create a compressed pdf
    One of the best thing is that you can provide the *size* for the compression
    limitation -> This class is limied to work with images.
    program will update the file if already exist.'''
    def __init__(self,files_lacation):
        if os.getcwd() != files_lacation:
            self.change_dir(files_lacation)
        self.image_type = ['PNG','JPG','JPEG','JIFF','TIFF']
        name_len = 5
        self.pdf_name = ''.join(['imageToPdf']+['.pdf'])

    def add_image_type(self,new_type):
        self.image_type.append(new_type)
        print(f"file type list ={self.image_type}")

    def change_dir(self,directory):
        # this will change directory
        print(f"change dir to - {directory} ..",end=" ")
        os.chdir(directory)
        print("done .")
    
    def open_convert(self,image_path):
        to_print = image_path.rsplit('\\',1)[1]
        print(f"working on '{to_print}' {random.choice(['😀','😁','😎','🤗','😃'])}")
        image = Image.open(image_path)
        return image.convert('RGB')

    def search_for_image_in_dir(self,name_list):
        self.imagelist = []
        for i in name_list:
            image_path = os.path.join(os.getcwd(),i)
            # check if file is not a directory and if exist and is type of image
            if not os.path.isdir(image_path) and os.path.exists(image_path) and image_path.rsplit('.',1)[1].upper() in self.image_type:
                self.imagelist.append(self.open_convert(image_path))
            else:
                print(i + " <-- This file is not acceptable or not exist.")
    
    def get_file_size(self,name):
        # file size in kb in ceil  
        return math.ceil(os.stat(os.path.join(os.getcwd(),name)).st_size /1024)

    def save_pdf(self):
        if self.imagelist:
            if len(self.imagelist) > 1:
                self.imagelist[0].save(self.pdf_name,save_all=True, append_images=self.imagelist[1:])
            else:
                self.imagelist[0].save(self.pdf_name,save_all=True)
            
            print(self.pdf_name +' PDF real size - '+str(self.get_file_size(self.pdf_name))+' kb')
        else:
            print("No Images found to create pdf ^_____^   ¯\_(ツ)_/¯")

    def save_compressed_pdf(self,size_needed):
        # set the quality variable at your desired level, The more the value of quality variable and lesser the compression 
        quality = 80 # for about same size
        self.pdf_compressed_name = ''.join(['imageToPdf','-compressed']+['.pdf'])
        def savepdf(quality):
            if len(self.imagelist) > 1:
                self.imagelist[0].save(self.pdf_compressed_name,
                                        save_all=True,
                                        append_images=self.imagelist[1:],
                                        optimize = True,
                                        quality = quality)
            else:
                self.imagelist[0].save(self.pdf_compressed_name,
                                        save_all=True,
                                        optimize = True,
                                        quality = quality)

        if self.imagelist:
            start,end = 5,quality
            savepdf(70)
            starting_size = self.get_file_size(self.pdf_compressed_name)
            while starting_size > size_needed :
                # on every itreation quatiy use half of the range value
                quality = int((start + end) / 2)                
                savepdf(quality)
                current_size = self.get_file_size(self.pdf_compressed_name)
                if 10 < (size_needed - current_size) < 60 : 
                    break 
                elif start == end :
                    print(f"\ncurrent size => {current_size} File can not compress more this is best possible compression from our side.")
                    break
                elif (current_size - size_needed) < 0 :
                    # low then require
                    start = quality
                elif (current_size - size_needed) > 0 :
                    # higher then require
                    end = quality
            
            try:
                print(self.pdf_compressed_name + ' PDF compressed size - '+str(current_size)+' kb')
            except :
                print(self.pdf_compressed_name + ' PDF is already smaller then needed compressed size is  - '+str(starting_size)+' kb')

        else:
            print("No Images found to create pdf ^_____^   ¯\_(ツ)_/¯")

    @classmethod
    def create_compressed_pdf(cls,directory,size_needed = 1024 ,save_original=True):
        # compression level 1=normal ,2 = average ,3 = max 
        pdf = cls(directory)
        # pdf.add_image_type("png")
        pdf.search_for_image_in_dir(os.listdir())
        if save_original : pdf.save_pdf()
        pdf.save_compressed_pdf(size_needed)

    @classmethod
    def compress_pdf(cls,path_to_pdf,size_needed):
        # may update here to not using any outside module to compress pdf 
        # extract all images and then use this class to make new pdf from it 
        import fitz, io

        path_to_pdf = path_to_pdf.replace('/','\\')
        directory ,file_name= path_to_pdf.rsplit('\\',1)
        print(directory)

        pdf_file = fitz.open(file_name)
        pdf = cls(directory)

        pdf.imagelist = []
        for page_index in range(len(pdf_file)):
            # get the page itself
            page = pdf_file[page_index]
            image_list = page.getImageList()
            # printing number of images found in this page
            # if image_list : print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
            for image_index, img in enumerate(page.getImageList(), start=1):
                xref = img[0]
                base_image = pdf_file.extractImage(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                # load it to PIL
                image = Image.open(io.BytesIO(image_bytes))
                # save it to memory
                pdf.imagelist.append(image.convert('RGB'))

        # print(pdf.imagelist )
        pdf.save_compressed_pdf(size_needed)

    @classmethod
    def create_pdf(cls,directory):
        pdf = cls(directory)
        pdf.search_for_image_in_dir(os.listdir())
        pdf.save_pdf()
    
    @classmethod
    def create_pdf_from_list(cls,directory,names :list):
        pdf = cls(directory)
        pdf.search_for_image_in_dir(names)
        pdf.save_pdf()


#### examples for testing :)
# name = 'imageToPdf.pdf'
# pdf.create_compressed_pdf(os.getcwd(),save_original=False)
# pdf.create_pdf(os.getcwd())
# pdf.create_pdf_from_list(os.getcwd(),["Screenshot (168).png","Screenshot (169).png","Screenshot (170).png","Screenshot (173).png"])
# pdf.compress_pdf(os.path.join(os.getcwd(),name),1024)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--size', default = 1024,type = int, help = "max size of your compressed file (defaut = 1024 = 1 Mb).")
    parser.add_argument('-a','--action', default = 0 ,type = int, help = '''what do you wanna do here :\n
        0 -> 'create a pdf and its compressed version',\n
        1 -> 'compressed a pdf',\n
        2 -> 'create simple pdf',\n
        3 -> 'pdf from list of file names '.''')
    # parser.add_argument('-d','--directory', default = os.getcwd(), help = "need to give the directory to program so it can collect all files.(default = current working directory)")

    args = parser.parse_args()
    if args.action == 0 or args.action == 2:
        # ask for directory name 
        dirPath = input("Enter the Full path of the directory with files : ")
        if args.action == 0 : 
            pdf.create_compressed_pdf(dirPath,args.size)
        else :
            pdf.create_pdf(dirPath)
    elif args.action == 1:
        # ask a file name which u wanna compress
        file_name = input("Enter the full path for the file to compress : ")
        pdf.compress_pdf(file_name,args.size)
    elif args.action == 3 :
        # ask for file directory and list of file to create a pdf of 
        dirPath = input("Enter the Full path of the directory with files : ")
        name_list = []
        for i in range(int(input("Enter the number of images YOU wanna Enter : "))):
            name_list.append(input(f"Enter image {i} Name --> : "))
        # print(name_list)
        pdf.create_pdf_from_list(dirPath,name_list)