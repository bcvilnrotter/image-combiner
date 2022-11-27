# imports
import argparse
import os, sys
import random
from datetime import datetime, timezone
from PIL import Image

# global constants
TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE = 10000 	# the max size TableTop Simulator (TTS) can handle for deck image attributes
TTS_DECK_IMAGE_MAX_CARDBACK_SIZE = 1000		# the max size TableTop Simulator (TTS) can handle for cardback attributes

# argument parser
arg_desc = '''\
Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image
'''

# initial argparse argument
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description = arg_desc)

# initialize the subparsers variable
subparsers = parser.add_subparsers(help='used to organize the different sub functions of the script', dest="sub")

# initialize the subparser for tts_deckbuilder
tts_deckbuilder = subparsers.add_parser("deckbuilder")

# initialize the subparser for tts_mapbuilder
tts_mapbuilder = subparsers.add_parser("mapbuilder")

# initialize the subparser arguments for tts_deckbuilder
tts_deckbuilder.add_argument("-d", '--directory', dest='directory', help="path to directory containing multiple base images")
tts_deckbuilder.add_argument("-i", '--image', dest='image', help="Path to our base image")
tts_deckbuilder.add_argument("-c", '--cardback', dest='cardback', help="path to the card back that will be used with tabletop simulator (TTS)")
tts_deckbuilder.add_argument("-o", '--output', dest='output', help="optional path to output directory")

# initialize the subparser arguments for tts_mapbuilder
tts_mapbuilder.add_argument("-a", '--assets', help="path to the directory containing multiple images that are assets for the map")
tts_mapbuilder.add_argument("-i", '--image', help="path to the background image used for the map")

# parser.add_argument("-o", '--output', metavar="OUTPUT_IMAGE", help="Path to directory where output will be placed")
# parser.add_argument("-n", --number, metavar="NUMBER", default=60, help = "Number of cards to be made in the deck")

# parse out the arguments for the tts_deckbuilder function
args = parser.parse_args()

"""
This section of code will be dedicated to error/log messaging. This section
will include the function for logging, as well as functions that could be 
used as a wrapper try/catch arguments for other clusters of functions. This
may not be implemented, but wanted to log it here now.

Author: Brian Vilnrotter
"""

# function to log data that is happening
def log(type, message):

	# get the current time
	now = datetime.now(timezone.utc)

	# combine the string for the log entry
	entry = str(now) + " [" + str(type) + "] " + str(message)

	# print the log entry
	print(entry)

"""
This section of code is solely focused on misculaneous/utility functions.
These include all the other functions that will be used to complete tasks
from the main functions described in the tools description.

Author: Brian Vilnrotter
"""

# function to make output path
def outpath(path):

	# split the path to filename and extension
	filename, extension = os.path.splitext(path)
		
	# get current time
	now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
	
	# return the output path
	return filename + "-" + now + extension

# function for adjusting the size of an image provided based on max pixel value provided
def inspect_image(image, check_value=TTS_DECK_IMAGE_MAX_CARDBACK_SIZE):

	# create a flag that states whether the image provided was altered
	altered = False

	# check if any attributes in the image are over the check_value
	if any(x > check_value for x in image.size):

		# log activity
		log('INFO', '  - image provided was larger than maximum value ' + str(check_value))

		# use the thumbnail function to reduce the size of the image while maintaining aspect ratio
		image.thumbnail((check_value, check_value))

		# log activity
		log('METR', '  - image was altered to (' + str(image.size) + ')')

		# create a flag that the image was altered
		altered = True

	# return the deliverables based on the function arguments
	return altered, image

"""
This section of the code is solely focused on taking pictures from the user, and 
combining them into a bigger picture that can be used for making decks in
TableTop Simulator (TTS). Although most of the functionality for this script will
be for use in TableTop Simulator, future additions may stride away from that
focus.

author: Brian Vilnrotter
"""

# function to build deck image
def tts_builddeck(file, output, deck_coef=[10,7]):

	# import the user provided image
	image = Image.open(file)

	# log the action
	log('INFO', '- opened file: ' + file)

	# check if a card back image is provided
	if args.cardback:

		# upload the cardback image
		cardback = Image.open(args.cardback)

		# resize the image to the size of the cardback
		image = image.resize(cardback.size)

		# log activity
		log('INFO', ' - image resized based on cardback: ' + args.cardback)
	
	# get specs of uploaded image
	width, height = image.size

	# log metrics
	log('METR', '- adjusted file has width: ' + str(width) + ' height: ' + str(height))

	# create the coeficient dimensions of the new image to be created
	nwidth, nheight = deck_coef

	# log metrics
	log('METR', '- initial coefficient sizes for output image: [' + str(nwidth) + ',' + str(nheight) + ']')

	# start a while loop that continues as long as the resulting image has attributes above 10k pixels
	while any(x > TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE for x in [nwidth*width, nheight*height]):
	
		# check if width of new image will be above 10k pixels
		if nwidth*width > TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nwidth value by 1
			nwidth = nwidth - 1
		
		# if the width is not above 10k pixels, check the height
		elif nheight*height > TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nheight value by 1
			nheight = nheight - 1
	
	# create new image variable
	new = Image.new(image.mode, (nwidth*width, nheight*height))
	
	# log action
	log('METR', '- adjusted deck image was made [' + str(nwidth) + ',' + str(nheight) + '] that has width: ' + str(nwidth*width) + ' and height: ' + str(nheight*height))

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

"""
This section of the code is solely dedicated to making a map for use in a
board game through the TableTop Simulator (TTS). This currently involves
created a map from a background image, and randomly distributing other
asset icons around the map.

Author: Brian Vilnrotter
"""

# function for creating a map
def tts_buildmap(background, folder, assets = [], resize = (100,100)):

	# load the background image
	image = Image.open(background)

	# log action
	log('INFO', '- load background iamge ' + background)

	# iterate through the directory provided for the assets
	for filename in os.listdir(folder):

		# build out the file path from the filename
		filepath = os.path.join(assets, filename)

		# resize the asset and appent it to the asset list
		assets.append((Image.open(filepath)).resize(resize))
	
	# iterate through a random number of items to place the assets on the background map
	for i in range(0, random.randint(5,10)):

		# create the position the asset will be placed on the background map
		position = (random.randint(0,image.width), random.randint(0, image.height))

		# pick a random image from the assets list
		asset = assets[random.randint(0, len(assets) -1)]

		# paste the chosen asset on the background in the chosen position
		image.paste(asset, position, asset)
	
	# save the created image out
	image.save(outpath(background))

"""
This section of the code is solely focused on the main function, as
well as its execution.

Author: Brian Vilnrotter
"""

def main():

	# check for cardback optional argument
	if args.cardback:

		# inspect the cardback image
		altered, cardback = inspect_image(Image.open(args.cardback))

		# check if the image was altered
		if altered:

			# assign the new outpath to the args.cardback variable
			args.cardback = outpath(args.cardback)

			# save the image to the destination assigned to the args.cardback variable
			cardback.save(args.cardback)

			# log activity
			log('INFO', '- cardback image provided was altered and saved to the same directory')

	# check if "-i" arguement is called
	if args.image:

		# log the action
		log('INFO', 'image path provided: ' + str(args.image))
		
		# check if an output path is provided
		if args.output:

			# if so, then run tts_builddeck with the provided output path
			tts_builddeck(args.image, args.output)
		
		# if an output path is not provided
		else:

			# make the card deck image
			tts_builddeck(args.image, outpath(args.image))

	# else, check if "-d" argument is called
	elif args.directory:

		# log the action
		log('INFO', 'directory path provided: ' + str(args.directory))

		# iterate recursively through the directory provided
		for subdir, dirs, files in os.walk(args.directory):

			# with the created values iterate through the files
			for file in files:

				# make a path of each file using created values
				path = os.path.join(subdir, file)
				
				# check if an output directory is provided
				if args.output:

					# then run tts_builddeck with the provided directory
					tts_builddeck(path, outpath(os.path.join(args.output, file)))

				# if not then - 
				else:
				
					# place the outputted image in the same directory as the provided image
					tts_builddeck(path, outpath(os.path.join(args.directory, file)))

if __name__ == "__main__":
	main()
