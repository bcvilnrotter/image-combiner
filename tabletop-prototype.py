#!C:\Users\Glapthorn\.pyenv\pyenv-win\versions\3.10.8\

# imports
import argparse
import os, sys
# import random
from datetime import datetime, timezone
from PIL import Image

# argument parser
arg_desc = '''\
Python Pillow Module
--------------------
Features:
- tts_deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- tts_mapbuilder: takes a background image, and smaller resource images to randomly place across the background image
'''

# initial argparse argument
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description = arg_desc)

# initialize the subparsers variable
subparsers = parser.add_subparsers(help='used to organize the different sub functions of the script')

# initialize the subparser for tts_deckbuilder
tts_deckbuilder = subparsers.add_parser("tts_deckbuilder")

# initialize the subparser arguments for tts_deckbuilder
tts_deckbuilder.add_argument("-d", '--directory', metavar="DIRECTORY_IMAGE", help="path to directory containing multiple base images")
tts_deckbuilder.add_argument("-i", '--image', metavar="FILE_IMAGE", help="Path to our base image")
# parser.add_argument("-o", '--output', metavar="OUTPUT_IMAGE", help="Path to directory where output will be placed")
# parser.add_argument("-n", --number, metavar="NUMBER", default=60, help = "Number of cards to be made in the deck")

# parse out the arguments
args = parser.parse_args()

"""
This section of the code is solely focused on taking pictures from the user, and 
combining them into a bigger picture that can be used for making decks in
TableTop Simulator (TTS). Although most of the functionality for this script will
be for use in TableTop Simulator, future additions may stride away from that
focus.

author: Brian Vilnrotter
"""

# function to make output path
def outpath(path):

	# split the path to filename and extension
	filename, extension = os.path.splitext(path)
		
	# get current time
	now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
	
	# return the output path
	return filename + "-" + now + extension

# function to log data that is happening
def log(type, message):

	# get the current time
	now = datetime.now(timezone.utc)

	# combine the string for the log entry
	entry = str(now) + " [" + str(type) + "] " + str(message)

	# print the log entry
	print(entry)

# function to build deck image
def tts_builddeck(file, output):

	# import the user provided image
	image = Image.open(file)

	# log the action
	log('INFO', '- opened file: ' + file)
	
	# get specs of uploaded image
	width, height = image.size

	# log metrics
	log('METR', '- opened file has width: ' + str(width) + ' height: ' + str(height))

	# create the coeficient dimensions of the new image to be created
	nwidth, nheight = [7, 10]

	# log metrics
	log('METR', '- coefficient sizes for output picture will contain ' + str(nwidth) + ' pictures wide, and ' + str(nheight) + ' pictures tall')
	
	# create new image variable
	new = Image.new(image.mode, (nwidth*width, nheight*height))
	
	# log action
	log('INFO', '- created a new image that has width: ' + str(nwidth*width) + ' and height: ' + str(nheight*height))

	# iterate through the new images height
	for h_index in range(nheight):

		# iterate through the new images width
		for w_index in range(nwidth):
			 
			# paste the image based on the index number
			new.paste(image, (width*w_index, height*h_index))
		 
	# log action
	log('INFO', '- pasted images together')
	
	# save created image to the designated output path
	new.save(output)
	
	# log action
	log('INFO', '- saved the created image to location: ' + str(output))

# function __main__
def main():

	# check if "-i" arguement is called
	if args.image:

		# log the action
		log('INFO', 'Image path provided: ' + str(args.image))
		
		# make the card deck image
		tts_builddeck(args.image, outpath(args.image))

	# else, check if "-o" argument is called
	elif args.directory:

		# log the action
		log('INFO', 'Directory path provided: ' + str(args.directory))

		# iterate recursively through the directory provided
		for subdir, dirs, files in os.walk(args.directory):

			# with the created values iterate through the files
			for file in files:

				# make a path of each file using created values
				path = os.path.join(subdir, file)
				
				# make the card deck image
				tts_builddeck(path, outpath(os.path.join(args.directory, file)))

if __name__ == "__main__":
	main()

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
