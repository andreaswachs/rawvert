# originated from https://github.com/achimoraites/Python-Image-Converter/blob/master/app/convert.py

from PIL import Image
import os
from threading import *
from concurrent.futures.thread import ThreadPoolExecutor
import rawpy
import imageio
from datetime import datetime
import optparse
import sys
import re

base_img_folder = "/mnt/c/billeder/"

class Rawvert:
    screen_lock = Semaphore()
    directory = 'converted'
    valid_file_types = [
        'RW2', 'ARW'
    ]
    target_dir = None        

    class action:
        START = 'Converting'
        END = 'Converted'

    def __init__(self, output_dir=None):
        self.output_dir = output_dir

    def process_msg(self, file_name, action):
        with self.screen_lock:
            print(f"{datetime.now().time().strftime('%H:%M:%S')} {action}: {file_name}")
    
    def convert_raw(self, file_name):
        try:
            # Declare save file name and path to the current image to convert
            save_file = f"{self.output_dir}/{('.'.join(file_name.split('.')[0:-1]))}.jpg"
            raw_path = f"{self.target_dir}/{file_name}"

            # message to stdout, beginning conversion
            self.process_msg(file_name=file_name,
                action=self.action.START)

            # convert the image 
            with rawpy.imread(raw_path) as raw:
                rgb = raw.postprocess(gamma=(5,8),use_camera_wb=True, no_auto_bright=True)
            
            # save the converted image
            imageio.imsave(save_file, rgb)

            self.process_msg(file_name=save_file,
                action=self.action.END)
        except Exception as e:
            print("There was an exception thrown while trying to convert images.")
            print(sys.exc_info()[0])
            print(e)

    def is_valid_image(self, file):
        # Check to see if the file name suffix is in valid file types array
        if file.split('.')[-1] in self.valid_file_types:
            return True  
        else:
            return False
        
    def is_valid_image_static(file):
        valid_file_types = [
            'RW2', 'ARW'
        ]
        # Check to see if the file name suffix is in valid file types array
        if file.split('.')[-1] in valid_file_types:
            return True  
        else:
            return False

    def convert_dir(self, target_dir):
        self.target_dir = target_dir
        print(f"Started conversion at: {datetime.now().time().strftime('%H:%M:%S')}")
        print(f"Converting \n -> {self.target_dir} directory.", end='\n\n')

        try:
            files = []
            # Go through all of the files in the directory
            for file in os.listdir(self.target_dir):
                # check to see if the current file is of a valid format
                if self.is_valid_image(file):
                    files.append(file)
            
            # Create a thread pool, where each thread is working on converting one image
            with ThreadPoolExecutor(max_workers=10) as executor:
                for file in files:
                    executor.submit(self.convert_raw, file)

            print(" \n Converted Images are stored at - > \n " + os.path.abspath(self.directory))
        except Exception as e:
            print(e)

if __name__ == '__main__':
    parser = optparse.OptionParser("usage%prog "+ \
    "-s <source directory> \n ex: usage%prog -s C:\\Users\\USerName\\Desktop\\Photos_Dir \n After -s Specify the directory you will convert")
    parser.add_option('-s', dest='nname', type='string', help='specify your source directory!')
    parser.add_option('-w', dest='walk', type='string', help='walk the parent directory for RW2 files')
    parser.add_option('--test', dest='test', action='store_false', default=False, help='Output files in test directory')
    (options, args) = parser.parse_args()
    
    if (options.nname == None and options.walk == None):
        print(parser.usage)
        exit(1)        

    # if the user just wants to convert one folder
    if options.nname:
        # Do some work with paths, setting up the output directory from the given target directory
        target_dir = os.path.relpath(options.nname)
        path_split = target_dir.split(' ')
        folder_month = str.capitalize(path_split[-2])
        folder_year = path_split[-1]
        output_folder = f"{base_img_folder}{folder_year}/{folder_month}"
        if options.test:
            output_folder = f"{base_img_folder}test/{folder_year}/{folder_month}"

        # Make sure that the output folder path exists
        try:
            os.makedirs(output_folder)
        except FileExistsError:
            pass

        # Create the image conversion object with the given output folder
        img = Rawvert(output_dir=output_folder)
        img.convert_dir(target_dir)

    # convert all the folders
    elif options.walk:
        # setting up the regex engine
        folder_pattern = re.compile('\d{1,2}\.\s\w+\s\d{4}')

        for folder_name, subfolders, filenames in os.walk(options.walk):
            if folder_pattern.search(folder_name):
                
                valid_files = False

                # Check to see if there is valid files in the directory
                for file in filenames:
                    if Rawvert.is_valid_image_static(file):
                        valid_files = True
                        break
                
                if valid_files:
                    target_dir = os.path.relpath(folder_name)
                    path_split = target_dir.split(' ')
                    folder_month = str.capitalize(path_split[-2])
                    folder_year = path_split[-1]
                    output_folder = f"{base_img_folder}{folder_year}/{folder_month}"
                    if options.test:
                        output_folder = f"{base_img_folder}test/{folder_year}/{folder_month}"

                    try:
                        os.makedirs(output_folder)
                    except FileExistsError:
                        pass

                    # Create the image conversion object with the given output folder
                    img = Rawvert(output_dir=output_folder)
                    img.convert_dir(target_dir)



    