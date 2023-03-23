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
- shapely				(pip install shapely)
- docx					(pip install python-docx)
- google-api libraries	(pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib)

Future:
- TableTopSimulator API
"""

# native imports
import os, glob, io
import argparse, random
from datetime import datetime, timezone

# pillow import
from PIL import Image, ImageDraw, ImageFont, ImageColor

# extra 3rd party import modules
import shapely
import numpy as np

# docx import
import docx

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

python prototype-assist.py mosaic --glob '/path/to/directory/*' --reference /path/to/reference/image
=========
'''

#endregion
#region common_args

# initiazlie the global vehicular transport that treats all values within globally
vehicle = {}

# initialize common arguments
common_args = argparse.ArgumentParser(add_help=False)

# initialize the global values
common_args.add_argument('--deck_image_max_attribute_size', default=10000, dest='TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE', help="the max size TableTop Simulator (TTS) can handle for deck image attributes")
common_args.add_argument('--deck_image_max_reference_size', default=1000, dest='TTS_DECK_IMAGE_MAX_REFERANCE_SIZE', help="the max size TableTop Simulator (TTS) can handle for reference attributes")

# initialize the default values needed for most subparsers
common_args.add_argument('--job', dest='job', help="path to output folder")
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
instruction_manual.add_argument('--template', default=None, dest='template', help='path to page image')
instruction_manual.add_argument('--font_name', default={
	'bold'		:	'arialbd.tff',
	'italic'	:	'ariali.tff',
	'bolditalic':	'arialbi.ttf',
	'regular'	:	'arial.ttf'
}, dest='font_name', help='the font that the script will use to add text to pages')
instruction_manual.add_argument('--font_size', default=12, dest='font_size', help='the number of lines per page')
instruction_manual.add_argument('--spacing', default=3, dest='spacing', help='the number of pixel spacing between lines')
instruction_manual.add_argument('--font_color', default='black', dest='font_color', help='the color of the text to be added to the page')
instruction_manual.add_argument('--margin', default=0.1, dest='margin', help='the % of the image the margin should take up')
instruction_manual.add_argument('--margin_offset', default='0,0', dest='margin_offset', help='custom x, y offset values for custom margin placement')
#TODO the segment for creating the instruction manual during the next coding session

#endregion
#region parser_process_and_conditions

# parse out the arguments for the mosaic function
args = parser.parse_args()

# check to ensure one of the required arguments are provided by the user
if not args.glink and not args.file and not args.glob:

	# provide an argparse error
	parser.error("please provide one of the following flags: --file, --glob, --glink")

# if glink is provided, must check if the creds are not provided
if args.glink and not args.gcreds:

	# provide an argparse error
	parser.error("Please provide the google creds using --gcreds when providing a google link")

#endregion
#region admin_functions

"""
This section of code will be dedicated to error/log messaging. This section
will include the function for logging, as well as functions that could be 
used as a wrapper try/catch arguments for other clusters of functions. This
may not be implemented, but wanted to log it here now.
"""

# function to get current date-time for consistent results
def get_now():

	# return the time with a consistent datetime function
	return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

# function that sets up the output environment
def setup_jobsfolder(args):

	# check if the args contains a user defined folder location
	if args.job:

		# assign args.job to a new variable to make scaling easier
		path = args.job
		
		# check if the directory does not exist
		if not os.path.exists(path):

			# make the folder
			os.mkdir(path)

		# return the user inputted directory
		return path

	# else, make a directory at the root of the script location
	else:

		# define the varible to hold the folder path
		jobsfolder = os.path.join(os.getcwd(), get_now())
		
		# create the folder path
		os.mkdir(jobsfolder)

		# return the folder path created
		return jobsfolder

# function to log data that is happening
def log(message, type='INFO'):

	# combine the string for the log entry
	entry = str(get_now()) + " [" + str(type) + "] " + str(message)

	# build a file path to check
	logpath = os.path.join(vehicle["jobsfolder"], "log.txt")

	# open or create a log file
	with open(logpath, "a") as f:

		# write the entry to the file
		f.write(entry + "\n")

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
def outpath(path, dated=True):

	# split the path to filename and extension
	root, extension = os.path.splitext(path)

	# pull the filename from the root
	filename = os.path.basename(root)
	
	# check if the script call wants a unique date identifier in the filename
	if dated == True:
	
		# return the output path
		return str(vehicle["jobsfolder"]) + "\\" + filename + "-" + get_now() + extension

	# else, return a non-unique dated filename path string
	else:

		return str(vehicle["jobsfolder"] + "\\" + filename + extension)

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
	SCOPES=['https://www.googleapis.com/auth/drive']

	# initialize the None variable for the creds
	creds = None

	# initialize what the path for the token should be
	token = outpath('token.json', dated=False)

	# log activity
	log(" - checking if a previously made token exists in jobs path")

	# check if a token exists
	if os.path.exists(token):

		# log activity
		log(" - token found, pulling credentials from token")

		# grab the creds with the found token
		creds = Credentials.from_authorized_user_file(token, SCOPES)
	
	# log activity
	log(" - checking if google-api creds are useable")
	
	# check if creds is empty, and if creds are not valid
	if not creds or not creds.valid:

		# log activity
		log(" - creds found do not work, troubleshooting...")

		# see if the creds just need a quick refresh
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())

		else:
			flow = InstalledAppFlow.from_client_secrets_file(args.gcreds, SCOPES)
			creds = flow.run_local_server(port=0)
		
		# log activity
		log(" - writing token contents")

		# save the token that was just created in the output location for later use
		with open(token, 'w') as token:
			token.write(creds.to_json())
	
	# pull the file object
	try:

		# try building the gdrive service object
		service = build('drive', 'v3', credentials=creds)

		# log the activity
		log(" - attempting to download the file with file_id:" + str(file_id))
		
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
			log(" - Download %d%%." % int(status.progress() * 100))
		
	except HttpError as error:
		log(F'An error occurred downloading the file: {error}', 'ERROR')
		return None

	# return the file object, don't forget to rewind
	return file

# function to return a shapely box
def setup_marginbox(image, width, height):

	return shapely.Polygon(
		[
			(width, height), 
			(image.width - width, height),
			(image.width - width, image.height - height),
			(width, image.height - height),
			(width, height)
		]
	)

# function for writing lines on an instruction manual page
def write_line(paragraph, image_default, image, cursor, marginbox, draw, font_dict):

	# initialize a variable to track the y value of the lines
	line_height = cursor.y

	# assign a variable to adjust the marginbox for style indentation
	indent = 0

	# assign the page number
	pagenum = 1

	log('marginbox: ' + str(marginbox.bounds))

	log('cursor: ' + str(cursor))

	if font_dict['style_name'] == 'List Paragraph':

		# draw the word onto the page template
		draw.text((cursor.x, cursor.y), " - ", font_dict['font_color'], font=font_dict['font_obj'])				
		
		# get the shapely box of the word, and update the cursor
		cursor = shapely.Point(
			cursor.x + (font_dict['font_obj'].getbbox(" - "))[2] + font_dict['font_obj'].getbbox(" ")[2], 
			line_height
		)		
		
		# adjust the indent value so it gets updated after the first line is drawn
		indent = font_dict['font_obj'].getbbox(" - ")[2]
	
	# iterate through the run objects in the paragraph
	for run in paragraph.runs:
	
		# determine whether basic word values have None value, if so use presented values
		if run.font.size is None:
			run_size = font_dict['font_size']
		else:
			run_size = run.font.size.pt
		log('run_size: ' + str(run_size))

		# cycle through the values collected to determine which font file to use
		if [run.font.bold,run.font.italic] == [True, True]:
			run_name = font_dict['font_name']['bolditalic']
		elif [run.font.bold,run.font.italic] == (True,False):
			run_name = font_dict['font_name']['bold']
		elif [run.font.bold,run.font.italic] == (False,True):
			run_name == font_dict['font_name']['italic']
		else:
			run_name = font_dict['font_name']['regular']
		log('run_name: ' + run_name)
		
		if run.font.color.rgb is None:
			run_color = font_dict['font_color']
		else:
			run_color = run.font.color.rgb
		log('run_color: ' + str(run_color))
		
		# assign a font object for the specific word
		font = ImageFont.truetype(run_name, size=int(run_size))

		for word in (run.text).split(" "):
		
			# check if the word position being drawn is outside the marginbox
			if (cursor.x + font.getbbox(word)[2]) > marginbox.bounds[2]:

				log(str(cursor.x + font.getbbox(word)[2]) + ' <= ' + str(marginbox.bounds[2]))		
				
				# update the line height using the font size and line spacing used in the function call
				line_height += (run_size + font_dict['line_spacing'])
				
				# update the cursor position using the minimum x value of the marginbox and the indent
				# as well as the hight of the line value determined above.
				cursor = shapely.Point(marginbox.bounds[0] + indent, line_height)

				# draw the word text
				draw.text((cursor.x, cursor.y), word, run_color, font=font)

				# update the cursor using the wordbox bounds
				cursor = shapely.Point(
					cursor.x + font.getbbox(word)[2] + font.getbbox(" ")[2], 
					line_height
				)
			
			# check if the word position being drawn is below the marginbox
			elif (cursor.y + font.getbbox(word)[3]) > marginbox.bounds[3]:

				log(str(cursor.y + font.getbbox(word)[3]) + ' <= ' + str(marginbox.bounds[3]))

				#TODO: save the page with unique filename that dictates pagenumber
				#TODO: create a new page and generate the marginbox
				#TODO: reset the cursor position on the new page
				#TODO: draw the word

				image.save(outpath(str(pagenum) + "-output.png"))
				
				image = image_default.copy()

				cursor = shapely.Point(marginbox.bounds[0], marginbox.bounds[1] + font.getbbox(word)[3])

				pagenum += 1

				draw.text((cursor.x, cursor.y), word, run_color, font=font)

				# update the cursor using the wordbox bounds
				cursor = shapely.Point(
					cursor.x + font.getbbox(word)[2] + font.getbbox(" ")[2], 
					line_height
				)				
			
			# if the word surpases the edge of the marginbox
			else:

				log(str((cursor.x + font.getbbox(word)[2])) + ' < ' + str(marginbox.bounds[2]))
				
				# draw the word onto the page template
				draw.text((cursor.x, cursor.y), word, run_color, font=font)				
				
				# get the shapely box of the word, and update the cursor
				cursor = shapely.Point(
					cursor.x + \
						font.getbbox(word)[2] + \
						font.getbbox(" ")[2], 
					line_height
				)		

	# this is the number that indicates line spacing.
	line_height += (int(font_dict['font_size']) + font_dict['line_spacing'])

	# return an up-to-date cursor shapely object so that the cursor object can be updated for then ext paragraph
	return shapely.Point(marginbox.bounds[0], line_height), image

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
		convert_to_pdf(args.glob, outpath("output.pdf"), args.title, args.author, args.subject)

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
def tiller_make_manual(args):

	# check if a google api link is provided
	if args.glink:

		# pull a file object from a google drive
		file = retrieve_google_drive_file((args.glink).split('/')[-2], args)

		# assign the collected file to the right variable
		#TODO add more robust way to determine which type of file format was collected
		doc = docx.Document(file)

	# once the text is collected, make an image object for the page
	if not args.template:

		# default image for making a manual
		#TODO identify a better way default setup for manual pages than the below
		image = Image.new(mode="RGBA", size=(640,480), color='orange')
	
	else:

		# create the image object out of the user inputted template path
		image = Image.open(args.template)

	# adjust the marginbox with offset values if the user provided any
	offsetx, offsety = args.margin_offset.split(',')

	# create the marginbox based on the created page image and user input
	# marginbox has a object called .bounds that contains 4 values.
	# (min x value, min y value, max x value, max y value) in that order
	
	# .bounds[0] = min x
	# .bounds[1] = min y
	# .bounds[2] = max x
	# .bounds[3] = max y

	# this marginbox is created with the function setup_marginbox within the
	# make_manual function for clean coding.

	make_manual(
		doc, 
		image, 
		setup_marginbox(
			image,
			int(image.width * args.margin + int(offsetx)), 
			int(image.height * args.margin + int(offsety)),
				
		), 
		ImageDraw.Draw(image),
		{
			'font_name'		:	args.font_name,
			'font_size'		:	args.font_size,
			'font_color'	:	args.font_color,
			'line_spacing'	:	args.spacing 
		}
	)

# function to add text to images
def make_manual(doc, image_default, marginbox, draw, user_input):

	# setup the initial cursor point to send to the write_line function
	cursor = shapely.Point(marginbox.bounds[0], marginbox.bounds[1])

	# iterate through the lines of the text collected
	for paragraph in doc.paragraphs:
		
		# assign a new default object
		image = image_default.copy()
		
		style = paragraph.style

		if style is not None:

			font_dict = {
				'style_name'	:	style.name
			}
			
			font_dict['font_name'] = user_input['font_name']

			if style.font.size is not None:
				font_dict['font_size'] = style.font.size.pt
			else:
				font_dict['font_size'] = user_input['font_size']
			
			if style.font.color is not None:
				font_dict['font_color'] = style.font.color.rgb
			else:
				font_dict['font_color'] = user_input['font_color']			

			font_dict['line_spacing'] = user_input['line_spacing']
			
		else:

			# create a font dictionary to send to the write_line function
			font_dict = {
				'style_name'	:	None,
				'font_name' 	: 	user_input['font_name'],
				'font_size'		:	user_input['font_size'],
				'font_color'	: 	user_input['font_color'],
				'line_spacing' 	: 	user_input['line_spacing']
			}
		
		# create the default font object and add it to the font dictionary
		font_dict['font_obj'] = ImageFont.truetype(
			font_dict['font_name']['regular'], 
			size=int(font_dict['font_size'])
		)

		# log activity
		log('style_name: ' + str(font_dict['style_name']))
		log('line_spacing: ' + str(font_dict['line_spacing']))
			
		# for each line, write the line to the template image
		cursor, image = write_line(paragraph, image_default, image, cursor, marginbox, draw, font_dict)

	# afterwards save the image
	image.save(outpath("output.png"))

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

		# if so, then run tts_builddeck with the provided output path
		tts_builddeck(args.file)

	# check if user provided glob argument
	if args.glob:

		# log the action
		log('glob regex provided: ' + str(args.glob))

		# iterate recursively through the glob regex provided
		for file in glob.glob(args.glob):
			
			# place the outputted image in the same directory as the provided image
			tts_builddeck(file, outpath(os.path.basename(file)))
	
	# check if a google link is provided
	if args.glink:

		#TODO: add code here to deal with a google_link
		# for now, just point to under_construction function
		under_construction()

# function to build deck image
def tts_builddeck(file, deck_coef=[10,7]):

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
	
	# get new outpath
	output = outpath(vehicle['jobsfolder'])
	
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

	# setup the jobs folder
	vehicle.update({"jobsfolder":setup_jobsfolder(args)})

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
		tiller_make_manual(args)

#endregion

if __name__ == "__main__":
	main()
