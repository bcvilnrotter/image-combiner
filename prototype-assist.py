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
import yaml

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

# initialize common arguments
common_args = argparse.ArgumentParser(add_help=False)

# initialize the global values
common_args.add_argument(
	'--deck_image_max_attribute_size', 
	default=10000, 
	dest='TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE', 
	help="the max size TableTop Simulator (TTS) can handle for deck image attributes"
)
common_args.add_argument(
	'--deck_image_max_reference_size', 
	default=1000, 
	dest='TTS_DECK_IMAGE_MAX_REFERANCE_SIZE', 
	help="the max size TableTop Simulator (TTS) can handle for reference attributes"
)

# initialize the default values needed for most subparsers
common_args.add_argument('--job', dest='job', help="path to output folder")
common_args.add_argument('--gcreds', dest='gcreds', help="path to the credential.json file for google-api access")
common_args.add_argument(
	'--keep_creds', 
	dest='keep_creds', 
	default=False, 
	action='store_true', 
	help="tell the script to delete any tokens it generates during processing"
)

# initialize the default arguments for source input (one of these is required for the script to function)
common_args.add_argument('--glob', dest='glob', help="regex used to pull multiple files from a path")
common_args.add_argument('--file', dest='file', help="path to a single file that will be used by the script")
common_args.add_argument('--glink', dest='glink', help="link pointing to a file in a google drive")

# initialize other common args
common_args.add_argument(
	'--debug', 
	action='store_true', 
	dest='debug', 
	help="a flag to add extra insight for debugging purposes"
)

#endregion
#region parser_initializing

# initial argparse argument
parser = argparse.ArgumentParser(
	epilog=arg_example, 
	formatter_class=argparse.RawDescriptionHelpFormatter, 
	description=arg_desc
)

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

instruction_manual.add_argument(
	'--config',
	dest='config',
	help='the config file used for formatting and stylizing information.'
)
instruction_manual.add_argument(
	'--margin', 
	default=0.1, 
	dest='margin', 
	help='the % of the image the margin should take up'
)
instruction_manual.add_argument(
	'--margin_offset', 
	default='0,0', 
	dest='margin_offset', 
	help='custom x, y offset values for custom margin placement'
)
instruction_manual.add_argument(
	'--title_page',
	dest='title_page',
	help='the title page to use when created the pdf'
)
instruction_manual.add_argument(
	'--dont_build_pdf',
	default=False,
	action='store_true',
	dest='dont_build_pdf',
	help='a flag to tell the script not to build the individual \
		pages into a pdf'
)
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

# initiazlie the global vehicular transport that treats all values within globally
vehicle = {}

# add the args variable to the vehicle
vehicle.update({'args': args})

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
def setup_jobsfolder():

	# check if the args contains a user defined folder location
	if vehicle['args'].job:

		# assign args.job to a new variable to make scaling easier
		path = vehicle['args'].job
		
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
def inspect_image(image, check_value=vehicle['args'].TTS_DECK_IMAGE_MAX_REFERANCE_SIZE):

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
def retrieve_google_drive_file(file_id):

	# check if path to credentials.json was provided by the user
	if not vehicle['args'].gcreds:

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
			flow = InstalledAppFlow.from_client_secrets_file(vehicle['args'].gcreds, SCOPES)
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

def get_manual_page():

	# once the text is collected, make an image object for the page
	if not vehicle['args'].template:

		# default image for making a manual
		#TODO identify a better way default setup for manual pages than the below
		vehicle.update({'image': Image.new(mode="RGBA", size=(640,480), color='orange')})
	
	else:

		# create the image object out of the user inputted template path
		vehicle.update({'image': Image.open(vehicle['args'].template)})

		log('added template object to vehicle dictionary.')

# function to return a shapely box
def setup_marginbox(width, height):

	# make the shapely polygon for the marginbox
	return shapely.Polygon(
		[
			(width, height), 
			(vehicle['image'].width - width, height),
			(vehicle['image'].width - width, vehicle['image'].height - height),
			(width, vehicle['image'].height - height),
			(width, height)
		]
	)

def collect_font_details(paragraph):

	font_dict = {}

	# cycle through the config parameters to see if the style fit
	for style in vehicle['config']['styles']:

		log("Paragraph Style: " + paragraph.style.name + " Style: " + style['name'])
		
		if style['name'] == paragraph.style.name:

			font_dict['style_name']		= style['name']
			font_dict['font_size']		= style['size']
			font_dict['font_color']		= style['color']
			font_dict['line_spacing']	= style['spacing']
			font_dict['bold']			= style['bold']
			font_dict['italic']			= style['italic']
			font_dict['bolditalic']		= style['bolditalic']
			font_dict['regular']		= style['regular']

	log(str(font_dict))	
	font_dict['font_obj'] = ImageFont.truetype(
		font_dict['regular'], 
		size=int(font_dict['font_size'])
	)

	# log activity
	log('style_name: ' + str(font_dict['style_name']))
	log('line_spacing: ' + str(font_dict['line_spacing']))

	return font_dict
	
# function which deals with different styles for paragraph objects
def stylize_line(indent, line_height, cursor, font_dict):

	# check for the paragraph style
	if font_dict['style_name'] == 'List Paragraph':

		# draw the word onto the page template
		vehicle['draw'].text((cursor.x, cursor.y), " - ", font_dict['font_color'], font=font_dict['font_obj'])				
		
		# get the shapely box of the word, and update the cursor
		cursor = shapely.Point(
			cursor.x + (font_dict['font_obj'].getbbox(" - "))[2] + font_dict['font_obj'].getbbox(" ")[2], 
			line_height
		)		
		
		# adjust the indent value so it gets updated after the first line is drawn
		indent = font_dict['font_obj'].getbbox(" - ")[2]
	
	# return the necesary items
	return indent, cursor

# function to collect the details of a run to dictate how to draw them
def collect_run_details(run, font_dict):

	# initialize run_dict object to return at end of function
	run_dict = {}
	
	# give font size
	run_dict['run_size'] = font_dict['font_size']

	# cycle through the values collected to determine which font file to use
	if [run.font.bold,run.font.italic] == [True, True]:
		run_dict['run_name'] = font_dict['bolditalic']
	elif [run.font.bold,run.font.italic] == (True,False):
		run_dict['run_name'] = font_dict['bold']
	elif [run.font.bold,run.font.italic] == (False,True):
		run_dict['run_name'] = font_dict['italic']
	else:
		run_dict['run_name'] = font_dict['regular']
	log('run_name: ' + run_dict['run_name'])
	
	run_dict['run_color'] = font_dict['font_color']
	log('run_color: ' + str(run_dict['run_color']))
	
	# assign a font object for the specific word
	run_dict['font_obj'] = ImageFont.truetype(
		run_dict['run_name'], 
		size=int(run_dict['run_size'])
	)

	# assign the font spacing
	run_dict['line_spacing'] = font_dict['line_spacing']

	return run_dict

# function to draw specific word, and then update what is necessary to continue
def step_word(word, line_height, cursor, run_dict):

	vehicle['draw'].text((cursor.x, cursor.y), word, run_dict['run_color'], font=run_dict['font_obj'])
	
	log('word drawn: ' + word)

	return shapely.Point(
		cursor.x + \
			run_dict['font_obj'].getbbox(word)[2] + \
			run_dict['font_obj'].getbbox(" ")[2], 
		line_height
	)

# function to update a new line when the word surpasses the marginbox
def new_line(line_height, cursor, marginbox, run_dict):

	# update the line height using the font size and line spacing used in the function call
	line_height += int(run_dict['run_size'] + run_dict['line_spacing'])
	
	# update the cursor position using the minimum x value of the marginbox and the indent
	# as well as the hight of the line value determined above.
	cursor = shapely.Point(marginbox.bounds[0] + run_dict['indent'], line_height)

	# return the updated line_height and cursor variables
	return line_height, cursor

# function to return a shapely polygon of a word using font.getbbox()
def get_shapely_word(cursor, word, run_dict):

	bbox = run_dict['font_obj'].getbbox(word)

	return shapely.geometry.Polygon(
		[(cursor.x + x, cursor.y + y) for x, y in shapely.geometry.box(*bbox).exterior.coords]
	)

# function to draw the words within runs
def write_word(word, line_height, cursor, marginbox, run_dict):

	# get a shapely polygon box that is similar to marginbox for comparisons
	shapely_word = get_shapely_word(cursor, word, run_dict)

	if shapely_word.within(marginbox):
		vehicle['draw'].polygon(shapely_word.exterior.coords, outline='green')
		cursor = step_word(word, line_height, cursor, run_dict)
	
	vehicle['draw'].polygon(marginbox.exterior.coords, outline='blue')

	# check if the word position being drawn is inside the marginbox
	if shapely_word.bounds[2] > marginbox.bounds[2]:

		if vehicle['args'].debug:
			vehicle['draw'].polygon(shapely_word.exterior.coords, outline='green')
			log(str(shapely_word.bounds[2]) + ' > ' + str(marginbox.bounds[2]))
		
		# add new line with current word
		line_height, cursor = new_line(line_height, cursor, marginbox, run_dict)

		# rerun the write_word function
		line_height, cursor = write_word(word, line_height, cursor, marginbox, run_dict)		

	# check if the word position being drawn is below the marginbox
	elif line_height > marginbox.bounds[3]:

		if vehicle['args'].debug:
			vehicle['draw'].polygon(shapely_word.exterior.coords, outline='green')
			log(str(line_height) + ' > ' + str(marginbox.bounds[3]))

		# save the current image
		vehicle['image'].save(outpath('output.png'))

		log('saved page...')
		
		# make a new  image object to the vehicle
		vehicle.update({'image': Image.open(vehicle['args'].template)})

		vehicle.update({'draw': ImageDraw.Draw(vehicle['image'])})

		log('created new page...')
		
		#image.save(outpath(str(pagenum) + "-output.png"))
		#image = image_default.copy()
		#pagenum += 1

		# reset cursor
		cursor = shapely.Point(marginbox.bounds[0], marginbox.bounds[1])

		line_height = cursor.y

		log('new cursor: x' + str(cursor.x) + ' y' + str(cursor.y))
		log('new line_height: ' + str(line_height))

		# add new line with current word
		#TODO expand on new_line so that it resets the cursor value, and makes a new page
		line_height, cursor = new_line(line_height, cursor, marginbox, run_dict)

		# rerun the write_word function
		line_height, cursor = write_word(word, line_height, cursor, marginbox, run_dict)		

		log('new cursor: x' + str(cursor.x) + ' y' + str(cursor.y))
		log('new line_height: ' + str(line_height))

	return line_height, cursor	

# function for writing lines on an instruction manual page
def write_line(paragraph, cursor, marginbox, font_dict):

	# initialize a variable to track the y value of the lines
	line_height = cursor.y

	# assign a variable to adjust the marginbox for style indentation
	indent = 0

	log('marginbox: ' + str(marginbox.bounds))

	log('cursor: ' + str(cursor))

	# stylzing the paragh as necessary based on the style value
	indent, cursor = stylize_line(indent, line_height, cursor, font_dict)
	
	# iterate through the run objects in the paragraph
	for run in paragraph.runs:
	
		# create the run dictionary to determine how to write it
		run_dict = collect_run_details(run, font_dict)

		# add the indent value to the dictionary
		#TODO find a better way to transfer the indent value to other functions
		run_dict['indent'] = indent

		# iterate through the words in each run
		for word in (run.text).split(" "):
			line_height, cursor = write_word(word, line_height, cursor, marginbox, run_dict)

	# this is the number that indicates line spacing.
	#line_height += (int(font_dict['font_size']) + font_dict['line_spacing'])
	line_height, cursor = new_line(line_height, cursor, marginbox, run_dict)	

	# return an up-to-date cursor shapely object so that the cursor object can be updated for then ext paragraph
	return shapely.Point(marginbox.bounds[0], line_height)

# function which makes pages while iterating through paragraph objects
def write_pages(doc, marginbox):

	# setup the initial cursor point to send to the write_line function
	cursor = shapely.Point(marginbox.bounds[0], marginbox.bounds[1])
	
	# iterate through the lines of the text collected
	for paragraph in doc.paragraphs:
			
		# for each line, write the line to the template image
		cursor = write_line(
			paragraph, 
			cursor,
			marginbox, 
			collect_font_details(paragraph)
		)
	
	# afterwards save the image
	#TODO this image.save function may need to be put in a different part of the script
	vehicle['image'].save(outpath("output.png"))

# function to compile pages into pdf once complete
def build_pdf_manual():

	log('compiling the page files into a pdf...')
	
	# create list of file paths to make into a pdf
	pages = []

	# check if a title page is given
	if vehicle['args'].title_page and os.path.isfile(vehicle['args'].title_page):
		
		# add the title page to the pages list
		pages.append(Image.open(vehicle['args'].title_page))

	# glob through the jobs folder, and add the pages to the pages list
	for page in glob.glob(vehicle['jobsfolder'] + '\*.png'):
		pages.append(Image.open(page))

	# save the collected pages to pdf
	save_to_pdf(pages, outpath('output.pdf'))

#endregion
#region pdf_tiller_processor_functions

"""
This section is dedicated to the functions that are used soleley within the
PDF subparser features. The goal of this is to make it so the instruction
manual can be easily converted into a PDF document for download on the
respective site that the eventual game will be hosted on.
"""

# tiller function to determine how to run the convert_to_pdf function
def tiller_convert_to_pdf():

	# check if file argument wasa called
	if vehicle['args'].file:

		#TODO: add code for telling the script how to print a pdf with only a single image file
		# for now, just run the under_construction function that logs this activity, and exit
		under_construction()
	
	# check if a file needs to be pulled using google-api
	if vehicle['args'].glink:
	
		#TODO: add code for telling the script how to print a pdf with only a single image file
		# file that needs to be pulled from google drive using the google-api
		# for now, just run the under_construction function that logs this activity, and exit
		under_construction()

	# check if the glob argument was called
	if vehicle['args'].glob:
	
		# run the convert_to_pdf using the glob argument
		convert_to_pdf(outpath("output.pdf"))

# function to save a list of pages to pdf
def save_to_pdf(pages, outpath):
	
	title = vehicle['args'].title if 'title' in vehicle['args'] else "default"

	author = vehicle['args'].author if 'author' in vehicle['args'] else "default"
	
	subject = vehicle['args'].subject if 'subject' in vehicle['args'] else "default"

	pages[0].save(
		outpath, 
		save_all=True, 
		append_images=pages[1:], 
		title=title, 
		author=author, 
		subject=subject
	)

# function to handle pdf files
def convert_to_pdf(outpath):

	# initialize the pages list
	pages = []

	# glob through the filepath provided to start iterate through files found
	for file in glob.glob(vehicle['glob']):

		# log activity - found file to add to pdf
		log(file + " was found, and will be added to the created pdf.")
		
		# append the file to the pages list by using Image
		pages.append(Image.open(file))
	
	# save the collected pdf files as a pdf
	save_to_pdf(pages, outpath)

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
def tiller_make_manual():

	# check if a google api link is provided
	if vehicle['args'].glink:

		# pull a file object from a google drive
		file = retrieve_google_drive_file((vehicle['args'].glink).split('/')[-2])

		# assign the collected file to the right variable
		#TODO add more robust way to determine which type of file format was collected
		doc = docx.Document(file)

	get_manual_page()

	# adjust the marginbox with offset values if the user provided any
	offsetx, offsety = vehicle['args'].margin_offset.split(',')

	vehicle.update({'draw': ImageDraw.Draw(vehicle['image'])})

	# collect the style information provided in the config file
	with open(vehicle['args'].config, 'r') as f:
		vehicle.update({'config' : yaml.safe_load(f)})

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
		setup_marginbox(
			int(vehicle['image'].width * vehicle['args'].margin + int(offsetx)), 
			int(vehicle['image'].height * vehicle['args'].margin + int(offsety))			
		)
	)

# function to add text to images
def make_manual(doc, marginbox):
			
	# create the different images needed for the pages of the manual
	write_pages(doc, marginbox)

	# once the pages are made, check to see if pdf should be made
	if vehicle['args'].dont_build_pdf == False:

		build_pdf_manual()

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
def tiller_builddeck():

	# check for reference optional argument
	if vehicle['args'].reference:

		# inspect the reference image
		altered, reference = inspect_image(Image.open(vehicle['args'].reference))

		# check if the image was altered
		if altered:

			# assign the new outpath to the args.reference variable
			vehicle['args'].reference = outpath(vehicle['args'].reference)

			# save the image to the destination assigned to the vehicle['args'].reference variable
			reference.save(vehicle['args'].reference)

			# log activity
			log('- reference image provided was altered and saved to the same directory')

	# check if "-i" arguement is called
	if vehicle['args'].file:

		# log the action
		log('image path provided: ' + str(vehicle['args'].file))

		# if so, then run tts_builddeck with the provided output path
		tts_builddeck(vehicle['args'].file)

	# check if user provided glob argument
	if vehicle['args'].glob:

		# log the action
		log('glob regex provided: ' + str(vehicle['args'].glob))

		# iterate recursively through the glob regex provided
		for file in glob.glob(vehicle['args'].glob):
			
			# place the outputted image in the same directory as the provided image
			tts_builddeck(file, outpath(os.path.basename(file)))
	
	# check if a google link is provided
	if vehicle['args'].glink:

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
	if vehicle['args'].reference:

		# upload the reference image
		reference = Image.open(vehicle['args'].reference)

		# resize the image to the size of the reference
		image = image.resize(reference.size)

		# log activity
		log(' - image resized based on reference: ' + vehicle['args'].reference)
	
	# get specs of uploaded image
	width, height = image.size

	# log metrics
	log('- adjusted file has width: ' + str(width) + ' height: ' + str(height), 'METR')

	# create the coeficient dimensions of the new image to be created
	nwidth, nheight = deck_coef

	# log metrics
	log('- initial coefficient sizes for output image: [' + str(nwidth) + ',' + str(nheight) + ']', 'METR')

	# start a while loop that continues as long as the resulting image has attributes above 10k pixels
	while any(x > vehicle['args'].TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE for x in [nwidth*width, nheight*height]):
	
		# check if width of new image will be above 10k pixels
		if nwidth*width > vehicle['args'].TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nwidth value by 1
			nwidth = nwidth - 1
		
		# if the width is not above 10k pixels, check the height
		elif nheight*height > vehicle['args'].TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE:

			# reduce the nheight value by 1
			nheight = nheight - 1
	
	# create new image variable
	new = Image.new(image.mode, (nwidth*width, nheight*height))
	
	# log action
	log('- adjusted deck image was made [' + str(nwidth) + ',' + str(nheight) + '] \
    	that has width: ' + str(nwidth*width) + ' and height: ' + str(nheight*height), 'METR')

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
def tiller_buildmap():

	# check if a file is provided
	if vehicle['args'].file:

		# run the mapbuilder function
		tts_buildmap(vehicle['args'].file, vehicle['args'].assets)
	
	# check if a glob is provided
	if vehicle['args'].glob:

		#TODO: add code to provide the necessary information to tt_buildmap function
		# for now, just add the under_construction function, and exit
		under_construction()
	
	# check if a google_link is provided
	if vehicle['args'].glink:

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
	vehicle.update({"jobsfolder":setup_jobsfolder()})

	# check if mapbuilder or deckbuilder is called
	if vehicle['args'].sub == "mosaic":

		# run the tiller function for the deck builder
		tiller_builddeck()

	# check if mapbuilder is called
	if vehicle['args'].sub == "mapbuilder":

		# send the args attribute to the tiller_buildmap function
		tiller_buildmap()
	
	# check if pdf is called
	if vehicle['args'].sub == "pdf":

		# send the args attributes to the tiller pdf function
		tiller_convert_to_pdf()
	
	# check if instruction_manual is called
	if vehicle['args'].sub == "instruction_manual":

		# run the tiller function for the instruction_manual subparser
		tiller_make_manual()

#endregion

if __name__ == "__main__":
	main()
