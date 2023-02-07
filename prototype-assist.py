#region imports 
"""
The below section is specific to importing all libraries that are required
for the normal working of the script. These libraries should require a low
amount of dependancies. (e.g. mostly native libraries with some libraries
the user will have to download and maintain)

so far the breakdown of native / special libraries are as follows:

Current:
- native
- pillow 				(pip install pillow)
- google-api libraries	(pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib)

Future:
- TableTopSimulator API
"""

# native imports
import os, glob, io
import argparse, random
from datetime import datetime, timezone

# pillow import
from PIL import Image

# google-api imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

#endregion
#region examples

"""
The below section is specific to all descriptions and examples
that will be used within argparse. The description should be
updated regularly, and there should be examples for main use of
the script that is commonly used by the developer.
"""

# argument parser
arg_desc = '''\
Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image
- pdf: takes a group of images and combines them into a single pdf document (for an instruction manual)
- instruction_manual: 
'''

# provide examples
arg_example = '''\
=========
Examples:

Make deck face images for TableTop Simulator (TTS) from a directory filled with images, 
	using a cardback image reference to match size.

python prototype-assist.py mosaic --glob /path/to/directory/ --reference /path/to/reference/image
=========
'''

#endregion
#region common_args

# initialize common arguments
common_args = argparse.ArgumentParser(add_help=False)

# initialize the global values
common_args.add_argument('--deck_image_max_attribute_size', default=10000, dest='TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE', help="the max size TableTop Simulator (TTS) can handle for deck image attributes")
common_args.add_argument('--deck_image_max_reference_size', default=1000, dest='TTS_DECK_IMAGE_MAX_REFERANCE_SIZE', help="the max size TableTop Simulator (TTS) can handle for reference attributes")

# initialize the default values needed for most subparsers
common_args.add_argument('--directory', dest='directory', help="path to directory that images will be output")
common_args.add_argument('--gcreds', dest='gcreds', help="path to the credential.json file for google-api access")
common_args.add_argument('--keep_creds', dest='keep_creds', default=False, action='store_true', help="tell the script to delete any tokens it generates during processing")

# initialize the default arguments for source input (one of these is required for the script to function)
common_args.add_argument('--glob', dest='glob', help="regex used to pull multiple files from a path")
common_args.add_argument('--file', dest='file', help="path to a single file that will be used by the script")
common_args.add_argument('--glink', dest='glink', help="link pointing to a file in a google drive")

#endregion
#region parser_initializing

# initial argparse argument
parser = argparse.ArgumentParser(epilog=arg_example, formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc)

# initialize the subparsers variable
subparsers = parser.add_subparsers(
	title='actions', 
	help='used to organize the different sub functions of the script', 
	dest="sub",
	required=True
	)

# initialize the subparser for mosaic
mosaic = subparsers.add_parser(
	"mosaic",
	parents=[common_args]
	)

# initialize the subparser for tts_mapbuilder
tts_mapbuilder = subparsers.add_parser(
	"mapbuilder",
	parents=[common_args]
	)

# initialize the subparser for PDF
pdf_actions = subparsers.add_parser(
	"pdf",
	parents=[common_args]
	)

# initialize the subparser for creating an instruction manual
instruction_manual = subparsers.add_parser(
	"instruction_manual",
	parents=[common_args]
	)

#endregion
#region subparser_arguments

# initialize the subparser arguments for mosaic
mosaic.add_argument('--reference', dest='reference', help="path to the card back that will be used with tabletop simulator (TTS)")

# initialize the subparser arguments for tts_mapbuilder
tts_mapbuilder.add_argument('--assets', dest='assets', help="path to the directory containing multiple images that are assets for the map")

# initialize the subparser arguments for pdf
pdf_actions.add_argument('--author', default='prototye-assist.py', dest='author', help="the author to put in the output pdf")
pdf_actions.add_argument('--title', default='Created using prototye-assist.py', dest='title', help="the title to put in the output pdf")
pdf_actions.add_argument('--subject', default='https://github.com/bcvilnrotter/block-pillow', dest='subject', help="the subject to put in the output pdf")

# initialize the subparser arguments for instruction_manual
#TODO the segment for creating the instruction manual during the next coding session

#endregion
#region parser_process_and_conditions

# parse out the arguments for the mosaic function
args = parser.parse_args()

# check to ensure one of the required arguments are provided by the user
if not args.glink and not args.file and not args.glob:

	# provide a argparse error
	parser.error("please provide one of the following flags: --file, --glob, --glink")

#endregion
#region admin_functions

"""
This section of code will be dedicated to error/log messaging. This section
will include the function for logging, as well as functions that could be 
used as a wrapper try/catch arguments for other clusters of functions. This
may not be implemented, but wanted to log it here now.
"""

# function to log data that is happening
def log(message, type='INFO'):

	# get the current time
	now = datetime.now(timezone.utc)

	# combine the string for the log entry
	entry = str(now) + " [" + str(type) + "] " + str(message)

	# print the log entry
	print(entry)

# function to log that a feature is under construction, and point the user to the github repo
def under_construction():

	# log the "under construction" ascii art (really make it stick out)
	log("_______________________________________________________________________________________________")
	log("|      ____  |  ###                                                              |      ____  |")
	log("| \  i | o|  | #      ##   #  #  ###  ###  ###  #   #   ###  ###  #   ###   #  # | \  i | o|  |")
	log("| |>#######  | #     #  #  ## #  ###   #   #    #   #  #      #   #  #   #  ## # | |>#######  |")
	log("| /(_______) |  ###   ##   # ##  ###   #   #     ###    ###   #   #   ###   # ## | /(_______) |")
	log("|____________|___________________________________________________________________|____________|")
	
	# give the user in the log information on where to get more information
	log("This feature is not yet implemented. please go to https://github.com/bcvilnrotter/prototype-assist for more information")
	
	# exit the script
	exit()

# function to make output path
def outpath(path):

	# split the path to filename and extension
	filename, extension = os.path.splitext(path)
		
	# get current time
	now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
	
	# return the output path
	return filename + "-" + now + extension

#endregion
#region secondary_functions

"""
This section of code is solely focused on misculaneous/utility functions.
These include all the other functions that will be used to complete tasks
from the main functions described in the tools description.
"""

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

# function to connect to a google drive account, and pull down a file
def retrieve_google_drive_file(file_id, args):

	# check if path to credentials.json was provided by the user
	if not args.gcreds:

		# log that credential.json is needed for this function
		log("No google api credentials were found. Use the --gcreds flag. exiting.")

		# exit
		exit()
	
	# define the scope. May make this dynamic later
	SCOPES=['https://www.googleapis.com/auth/documents.readonly']

	# initialize the None variable for the creds
	creds = None

	# check if a token exists
	if os.path.exists('token.json'):

		# grab the creds with the found token
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	
	# check if creds is empty, and if creds are not valid
	if not creds or not creds.valid:

		# see if the creds just need a quick refresh
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())

		else:
			flow = InstalledAppFlow.from_client_secrets_file(args.gcreds, SCOPES)
			creds = flow.run_local_server(port=0)
		
		# save the token that was just created in the output location for later use
		with open('token.json', 'w') as token:
			token.write(creds.to_json())
	
	# pull the file object
	try:

		# try building the gdrive service object
		service = build('drive', 'v3', credentials=creds)

		# request data from drive api
		request = service.files().get_media(fileId=file_id)

		# initialize the data variable
		file = io.BytesIO()
		
		# initialize downloader object
		downloader = MediaIoBaseDownload(file, request)

		# download the data, and keep status up-to-date
		done = False
		while done is False:
			status, done = downloader.next_chunk()
			log("Download %d%%." % int(status.progress() * 100))
		
	except HttpError as error:
		log(F'An error occurred downloading the file: {error}', 'ERROR')
		return None

	# return the file object, don't forget to rewind
	return file.seek(0)

#endregion
#region pdf_tiller_processor_functions

"""
This section is dedicated to the functions that are used soleley within the
PDF subparser features. The goal of this is to make it so the instruction
manual can be easily converted into a PDF document for download on the
respective site that the eventual game will be hosted on.
"""

# tiller function to determine how to run the convert_to_pdf function
def tiller_convert_to_pdf(args):

	# check if file argument wasa called
	if args.file:

		#TODO: add code for telling the script how to print a pdf with only a single image file
		# for now, just run the under_construction function that logs this activity, and exit
		under_construction()
	
	# check if a file needs to be pulled using google-api
	if args.glink:
	
		#TODO: add code for telling the script how to print a pdf with only a single image file
		# file that needs to be pulled from google drive using the google-api
		# for now, just run the under_construction function that logs this activity, and exit
		under_construction()

	# check if the glob argument was called
	if args.glob:
	
		# run the convert_to_pdf using the glob argument
		convert_to_pdf(args.glob, outpath(os.path.join(args.directory, "output.pdf")), args.title, args.author, args.subject)

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

#endregion
#region instruction_manual_tiller_processing_functions

"""
This section of the code is solely focused on creating an "instruction manual" by
taking text from a document, and pasting the information on a series of template
images. This codes complete product will hopefully be smart enough to keep formatting
elements (e.g. paragraphs, font size, font style, and embeded images) while
consistently keeping the text in the images within indicies that are defined
by the user.
"""

# tiller function to help determine how to collect and process data to make instruction manuals
def tiller_instruction_manual(args):

	# check if a google api link is provided
	if args.link:

		# pull a file object from a google drive
		file = retrieve_google_drive_file((args.link).split('/')[-2], args)

		# run the instruction_manual function while passing the file object collected
		#TODO the instruction_manual function. It will probably look like the following:
		# instruction_manual(file, args)

#endregion
#region tiller_mosaic_tiller_processor_functions

"""
This section of the code is solely focused on taking pictures from the user, and 
combining them into a bigger picture that can be used for making decks in
TableTop Simulator (TTS). Although most of the functionality for this script will
be for use in TableTop Simulator, future additions may stride away from that
focus.
"""

# function for tilling out exactly how the tt_builddeck function should work
def tiller_builddeck(args):

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
	if args.file:

		# log the action
		log('image path provided: ' + str(args.file))
		
		# check if an output path is provided
		if args.directory:

			# if so, then run tts_builddeck with the provided output path
			tts_builddeck(args.file, args.directory)
		
		# if an output path is not provided
		else:

			# make the card deck image
			tts_builddeck(args.file, outpath(args.file))

	# check if user provided glob argument
	if args.glob:

		# log the action
		log('glob regex provided: ' + str(args.glob))

		# iterate recursively through the glob regex provided
		for file in glob.glob(args.glob):
			
			# place the outputted image in the same directory as the provided image
			tts_builddeck(file, outpath(os.path.join(args.directory, os.path.basename(file))))
	
	# check if a google link is provided
	if args.glink:

		#TODO: add code here to deal with a google_link
		# for now, just point to under_construction function
		under_construction()

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

#endregion
#region mapbuilder_tiller_processing_functions

"""
This section of the code is solely dedicated to making a map for use in a
board game through the TableTop Simulator (TTS). This currently involves
created a map from a background image, and randomly distributing other
asset icons around the map.
"""

# tiller function for the tts_buildmap subparser function
def tiller_buildmap(args):

	# check if a file is provided
	if args.file:

		# run the mapbuilder function
		tts_buildmap(args.file, args.assets)
	
	# check if a glob is provided
	if args.glob:

		#TODO: add code to provide the necessary information to tt_buildmap function
		# for now, just add the under_construction function, and exit
		under_construction()
	
	# check if a google_link is provided
	if args.glink:

		# TODO: add code to provide the necessary information to tt_buildmap function
		# for now, just add the under_construction function, and exit
		under_construction()

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

#endregion
#region main_function

"""
This section of the code is solely focused on the main function, as
well as its execution. In my current thinking the main function should
predominately be used for parsing out user triggers, and telling
which functions should be processed. The big functions should be
doing the heavy lifting once it is given all the data.

It looks like it will be important to have 'tiller' functions for each
subparsor main function to help process some of the user triggers. The
triggeres found in the main function, however, should be focused on
making sure the output of the script is as the user expects it to look
(e.g. setting up the jobs folder)
"""

def main():

	# check if mapbuilder or deckbuilder is called
	if args.sub == "mosaic":

		# run the tiller function for the deck builder
		tiller_builddeck(args)

	# check if mapbuilder is called
	if args.sub == "mapbuilder":

		# send the args attribute to the tiller_buildmap function
		tiller_buildmap(args)
	
	# check if pdf is called
	if args.sub == "pdf":

		# send the args attributes to the tiller pdf function
		tiller_convert_to_pdf(args)
	
	# check if instruction_manual is called
	if args.sub == "instruction_manual":

		# run the tiller function for the instruction_manual subparser
		#TODO: This will eventually lead to the instruction_manual functions,
		# but for now it will just lead to the under_construction function
		under_construction()

#endregion

if __name__ == "__main__":
	main()
