# imports
import argparse
import os, sys
# import random
import datetime as dt
from PIL import Image

# argument parser
arg_desc = '''\
      Python Pillow Module
      --------------------
      Features:
      - tts-deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
      '''

# initial argparse argument
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description = arg_desc)

# tts-deckbuilder
parser.add_argument("-d", --directory, metavar = "DIRECTORY_IMAGE", help = "path to directory containing multiple base images")
parser.add_argument("-i", --input, metavar = "FILE_IMAGE", help = "Path to our base image")
parser.add_argument("-o", --output, metavar = "OUTPUT_IMAGE", help = "Path to directory where output will be placed")
parser.add_argument("-n", --number, metavar = "NUMBER", help = "Number of cards to be made in the deck")

# parse out the arguments
args = vars(parser.parse_args())

"""
This section of the code is solely focused on taking pictures from the user, and 
combing them into a bigger picture that can be used for making decks in
TableTop Simulator (TTS). Although most of the functionality for this script will
be for use in TableTop Simulator, future additions may stride away from that
focus.

author: Brian Vilnrotter
"""
# directory = args["secondary"]
# resources = []

# image = Image.open(args["image"])

# for filename in os.listdir(directory):
#   filepath = os.path.join(directory, filename)
#   resources.append((Image.open(filepath)).resize((100, 100)))
  
# for i in range (o, random.randint(5,10)):
#   position = (random.randint(o, image_copy.width), random.randint(0,image_copy.height))
#   resource = resources[random.randint(0, len(resources) - 1)]
#   image_copy.paste(resource, position, resource)
  
# image_copy.save(args["output"] + dt.datetime.now().strftime("%m-%d-%YT%H-%M-%S") + ".JPG")
