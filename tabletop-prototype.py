# imports
import argparse
import os, sys
import random
import datetime as dt
from PIL import Image

# argument parser
arg_desc = '''\
      Python Pillow Module
      --------------------
      '''
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description = arg_desc)
parser.add_argument("-i", "--image", metavar = "IMAGE", help = "Path to your base image")
parser.add_argument("-s", "--secondary", metavar = "SECOND", help = "Path to the secondary images")
parser.add_argument("-o", "--output", metavar = "OUTPUT", help = "Path to output file")
args = vars(parser.parse_args())

"""
This section of the code is solely focused on taking pictures from the user, and 
combing them into a bigger picture that can be used for making decks in
TableTop Simulator (TTS). Although most of the functionality for this script will
be for use in TableTop Simulator, future additions may stride away from that
focus.

author: Brian Vilnrotter
"""
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
