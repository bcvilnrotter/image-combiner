# imports
import argparse
import os, sys
import random
import datetime as dt
from PIL import Image

# argparse
arg_desc = '''\
      Python Pillow Module
      --------------------
      '''
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description = arg_desc)
parser.add_argument("-i", "--image", metavar = "IMAGE", help = "Path to your base image")
parser.add_argument("-s", "--secondary", metavar = "SECOND", help = "Path to the secondary images")
parser.add_argument("-o", "--output", metavar = "OUTPUT", help = "Path to output file")
args = vars(parser.parse_args())

# initial code
directory = args["secondary"]
resources = []

image = Image.open(args["image"])

for filename in os.listdir(directory):
  filepath = os.path.join(directory, filename)
  resources.append((Image.open(filepath)).resize((100, 100)))
  
for i in range (o, random.randint(5,10)):
  position = (random.randint(o, image_copy.width), random.randint(0,image_copy.height))
  resource = resources[random.randint(0, len(resources) - 1)]
  image_copy.paste(resource, position, resource)
  
image_copy.save(args["output"] + dt.datetime.now().strftime("%m-%d-%YT%H-%M-%S") + ".JPG")
