# imports
import argparse
import os, random, glob
from datetime import datetime, timezone
from PIL import Image

# argument parser
arg_desc = '''\
Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image
'''

# provide examples
arg_example = '''\
=========
Examples:

Make deck face images for TableTop Simulator (TTS) from a directory filled with images, 
	using a cardback image reference to match size.

python prototype-assist.py mosaic -g /path/to/directory/ -r /path/to/reference/image
=========
'''

# initial argparse argument
parser = argparse.ArgumentParser(epilog=arg_example, formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc)

# initialize the global values
parser.add_argument('--deck_image_max_attribute_size', default=10000, dest='TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE', help="the max size TableTop Simulator (TTS) can handle for deck image attributes")
parser.add_argument('--deck_image_max_reference_size', default=1000, dest='TTS_DECK_IMAGE_MAX_REFERANCE_SIZE', help="the max size TableTop Simulator (TTS) can handle for reference attributes")

# initialize the default values needed for most subparsers
parser.add_argument("-g", '--glob', dest='glob', help="regex used to pull multiple files from a path")
parser.add_argument("-d", '--directory', dest='directory', help="path to directory that images will be output")
parser.add_argument("-i", '--image', dest='image', help="Path to our base image")

# initialize the subparsers variable
subparsers = parser.add_subparsers(help='used to organize the different sub functions of the script', dest="sub")

# initialize the subparser for mosaic
mosaic = subparsers.add_parser("mosaic")

# initialize the subparser for tts_mapbuilder
tts_mapbuilder = subparsers.add_parser("mapbuilder")

# initialize the subparser for PDF
pdf_actions = subparsers.add_parser("pdf")

# initialize the subparser arguments for mosaic
mosaic.add_argument("-r", '--refernce', dest='reference', help="path to the card back that will be used with tabletop simulator (TTS)")

# initialize the subparser arguments for tts_mapbuilder
tts_mapbuilder.add_argument("-a", '--assets', dest='assets', help="path to the directory containing multiple images that are assets for the map")

# initialize the subparser arguments for pdf
pdf_actions.add_argument('-a', '--author', default='prototye-assist.py', dest='author', help="the author to put in the output pdf")
pdf_actions.add_argument('-t', '--title', default='Created using prototye-assist.py', dest='title', help="the title to put in the output pdf")
pdf_actions.add_argument('-s', '--subject', default='https://github.com/bcvilnrotter/block-pillow', dest='subject', help="the subject to put in the output pdf")

# parse out the arguments for the mosaic function
args = parser.parse_args()

"""
This section of code will be dedicated to error/log messaging. This section
will include the function for logging, as well as functions that could be 
used as a wrapper try/catch arguments for other clusters of functions. This
may not be implemented, but wanted to log it here now.

Author: Brian Vilnrotter
"""

# function to log data that is happening
def log(message, type='INFO'):

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
def inspect_image(image, check_value=args.TTS_DECK_IMAGE_MAX_REFERANCE_SIZE):

	# create a flag that states whether the image provided was altered
	altered = False

	# check if any attributes in the image are over the check_value
	if any(x > check_value for x in image.size):

		# log activity
		log('  - image provided was larger than maximum value ' + str(check_value))

		# use the thumbnail function to reduce the size of the image while maintaining aspect ratio
		image.thumbnail((check_value, check_value))

		# log activity
		log('  - image was altered to (' + str(image.size) + ')', 'METR')

		# create a flag that the image was altered
		altered = True

	# return the deliverables based on the function arguments
	return altered, image

"""
This section is dedicated to the functions that are used soleley within the
PDF subparser features. The goal of this is to make it so the instruction
manual can be easily converted into a PDF document for download on the
respective site that the eventual game will be hosted on.

author: Brian Vilnrotter
"""

# function to handle pdf files
def convert_to_pdf(glob_path, outpath, pdf_title, pdf_author, pdf_subject):

	# initialize the pages list
	pages = []

	# glob through the filepath provided to start iterate through files found
	for file in glob.glob(glob_path):

		# log activity - found file to add to pdf
		log(file + " was found, and will be added to the created pdf.")
		
		# append the file to the pages list by using Image
		pages.append(Image.open(file))
	
	# save the collected pdf files as a pdf
	pages[0].save(outpath, save_all=True, append_images=pages[1:], title=pdf_title, author=pdf_author, subject=pdf_subject)

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
	log('- opened file: ' + file)

	# check if a card back image is provided
	if args.reference:

		# upload the reference image
		reference = Image.open(args.reference)

		# resize the image to the size of the reference
		image = image.resize(reference.size)

		# log activity
		log(' - image resized based on reference: ' + args.reference)
	
	# get specs of uploaded image
	width, height = image.size

	# log metrics
	log('- adjusted file has width: ' + str(width) + ' height: ' + str(height), 'METR')

	# create the coeficient dimensions of the new image to be created
	nwidth, nheight = deck_coef

	# log metrics
	log('- initial coefficient sizes for output image: [' + str(nwidth) + ',' + str(nheight) + ']', 'METR')

	# start a while loop that continues as long as the resulting image has attributes above 10k pixels
	while any(x > args.TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE for x in [nwidth*width, nheight*height]):
	
		# check if width of new image will be above 10k pixels
		if nwidth*width > args.TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nwidth value by 1
			nwidth = nwidth - 1
		
		# if the width is not above 10k pixels, check the height
		elif nheight*height > args.TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nheight value by 1
			nheight = nheight - 1
	
	# create new image variable
	new = Image.new(image.mode, (nwidth*width, nheight*height))
	
	# log action
	log('- adjusted deck image was made [' + str(nwidth) + ',' + str(nheight) + '] that has width: ' + str(nwidth*width) + ' and height: ' + str(nheight*height), 'METR')

	# iterate through the new images height
	for h_index in range(nheight):

		# iterate through the new images width
		for w_index in range(nwidth):
			 
			# paste the image based on the index number
			new.paste(image, (width*w_index, height*h_index))
		 
	# log action
	log('- pasted images together')
	
	# save created image to the designated output path
	new.save(output)
	
	# log action
	log('- saved the created image to location: ' + str(output))

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
	log('- load background image ' + background)

	# iterate through the directory provided for the assets
	for filename in os.listdir(folder):

		# build out the file path from the filename
		filepath = os.path.join(folder, filename)

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

	# check if mapbuilder or deckbuilder is called
	if (args.sub == "mosaic"):
		
		# check for reference optional argument
		if args.reference:

			# inspect the reference image
			altered, reference = inspect_image(Image.open(args.reference))

			# check if the image was altered
			if altered:

				# assign the new outpath to the args.reference variable
				args.reference = outpath(args.reference)

				# save the image to the destination assigned to the args.reference variable
				reference.save(args.reference)

				# log activity
				log('- reference image provided was altered and saved to the same directory')

		# check if "-i" arguement is called
		if args.image:

			# log the action
			log('image path provided: ' + str(args.image))
			
			# check if an output path is provided
			if args.directory:

				# if so, then run tts_builddeck with the provided output path
				tts_builddeck(args.image, args.directory)
			
			# if an output path is not provided
			else:

				# make the card deck image
				tts_builddeck(args.image, outpath(args.image))

		# else, check if "-d" argument is called
		elif args.glob:

			# log the action
			log('glob regex provided: ' + str(args.glob))

			# iterate recursively through the glob regex provided
			for file in glob.glob(args.glob):
				
				# place the outputted image in the same directory as the provided image
				tts_builddeck(file, outpath(os.path.join(args.directory, os.path.basename(file))))

	# check if mapbuilder is called
	if args.sub == "mapbuilder":

		# run the mapbuilder function
		tts_buildmap(args.image, args.assets)
	
	# check if pdf is called
	if args.sub == "pdf":

		# run the pdf converter function
		convert_to_pdf(args.glob, outpath(os.path.join(args.directory, "output.pdf")), args.title, args.author, args.subject)

if __name__ == "__main__":
	main()
