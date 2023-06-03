# Scope

This scripting tool is intended to give functionality to many actions related to building prototypes
and art assets for physical game projects. This functionality includes, but is not limited to, 
working with prototyping tools such as Table Top Simulator (TTS), and building instruction manual
assets for already published games.

Changes to structure and dependancies to this project will be more continuous, but the scope described
above should always be considered whith any new change.

## Dependancies

In order for this script to function, the following modules would have to be installed. 

### Python

This script is run using python, and has been primarily tested and coded in [python 3.10.8](https://www.python.org/downloads/release/python-3108/)
within a windows based environment.

### [![Pillow Package Health Score](https://snyk.io/advisor/python/pillow/badge.svg)](https://snyk.io/advisor/python/pillow) Pillow
```
pip install pillow
```

Pillow is used as the main module for image manipulation. This module will need to be installed on your system before the script will function. Pillow is also the main module to use for dealing with pdf files.

### [![Shapely Package Health Score](https://snyk.io/advisor/python/shapely/badge.svg)](https://snyk.io/advisor/python/shapely) Shapely
```
pip install shapely
```

Shapely is the main module used to conduct geometrical calculations. Currently this is mainly used for making instruction manuals, but my hope is to expand this into other 
functions such as the deckbuilder (currently called mosaic).

### [![Python-Docx Package Health Score](https://snyk.io/advisor/python/python-docx/badge.svg)](https://snyk.io/advisor/python/python-docx) Python-Docx
```
pip install python-docx
```

this is a docx module which is mainly used to read a docx that is pulled from google a google drive. The score for this module is a bit low, but no vulnerabilities are currently known.
Since it is not a currently maintained project we would need to find a replacement methodology or module to handle pulling data from docx files through python, or another workaround.

###  Google-Api Libraries

#### [![Google-Api-Python-Client Package Health Score](https://snyk.io/advisor/python/google-api-python-client/badge.svg)](https://snyk.io/advisor/python/google-api-python-client) Python-Docxgoogle-api-python-client
#### [![Python-Docx Package Health Score](https://snyk.io/advisor/python/google-auth-httplib2/badge.svg)](https://snyk.io/advisor/python/google-auth-httplib2) Python-Docxgoogle-auth-httplib2
#### [![Python-Docx Package Health Score](https://snyk.io/advisor/python/google-auth-oauthlib/badge.svg)](https://snyk.io/advisor/python/google-auth-oauthlib) Python-Docxgoogle-auth-oauthlib
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

This is the set of modules that are primarily used to pull data from a google drive account. The platforms that can be used to pull data from may expand in the future, but currently
this is a good way to use out big toe to test the waters for this mode of data collection.

## Functions

The below are the different subcommands the script currently supports, as well as their intended purpose.

### Mosaic
// TODO: Revert Mosaic back to deckbuilder
// TODO: Add description for this function

### MapBuilder
// TODO: Add description for this function

### PDF
// TODO: Add description for this function

### Instruction_Manual
// TODO: Add description for this function
// TODO: Add description of config.yaml

### Usage
// TODO: Add description of how to use script
// TODO: Add examples

# RAW last readme
// TODO: Remove the below once the full readme above is done.

BASE OPTIONS (help menu)

```
usage: prototype-assist.py [-h] {mosaic,mapbuilder,pdf,instruction_manual} ...

Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}
                        used to organize the different sub functions of the script

=========
Examples:

Make deck face images for TableTop Simulator (TTS) from a directory filled with images,
        using a cardback image reference to match size.

python prototype-assist.py mosaic --glob /path/to/directory/ --reference /path/to/reference/image
=========
```

MOSAIC (help menu)

```
usage: prototype-assist.py [-h] {mosaic,mapbuilder,pdf,instruction_manual} ...

Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}
                        used to organize the different sub functions of the script

=========
Examples:

Make deck face images for TableTop Simulator (TTS) from a directory filled with images,
        using a cardback image reference to match size.

python prototype-assist.py mosaic --glob /path/to/directory/ --reference /path/to/reference/image
  --directory DIRECTORY                        path to directory that images will be output
  --gcreds GCREDS       path to the credential.json file for google-api access
  --keep_creds          tell the script to delete any tokens it generates during processing
  --glob GLOB           regex used to pull multiple files from a path
  --file FILE           path to a single file that will be used by the script
  --glink GLINK         link pointing to a file in a google drive
  --reference REFERENCE
                        path to the card back that will be used with tabletop simulator (TTS)
```

MAPBUILDER OPTIONS (help menu)

```
usage: prototype-assist.py [-h] {mosaic,mapbuilder,pdf,instruction_manual} ...

Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}

options:
  -h, --help            show this help message and exit

actions:
  {mosaic,mapbuilder,pdf,instruction_manual}
                        used to organize the different sub functions of the script

=========
Examples:

                        the max size TableTop Simulator (TTS) can handle for deck image attributes
  --deck_image_max_reference_size TTS_DECK_IMAGE_MAX_REFERANCE_SIZE
                        the max size TableTop Simulator (TTS) can handle for reference attributes
  --directory DIRECTORY
                        path to directory that images will be output  --gcreds GCREDS       path to the credential.json file for google-api access
  --keep_creds          tell the script to delete any tokens it generates during processing
  --glob GLOB           regex used to pull multiple files from a path
  --file FILE           path to a single file that will be used by the script
  --glink GLINK         link pointing to a file in a google drive  --assets ASSETS       path to the directory containing multiple images that are assets for the map
```

PDF (help menu)

```
usage: prototype-assist.py pdf [-h] [--deck_image_max_attribute_size TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE]
                               [--deck_image_max_reference_size TTS_DECK_IMAGE_MAX_REFERANCE_SIZE] [--directory DIRECTORY] [--gcreds GCREDS] [--keep_creds]
                               [--glob GLOB] [--file FILE] [--glink GLINK] [--author AUTHOR] [--title TITLE] [--subject SUBJECT]

options:
  -h, --help            show this help message and exit
  --deck_image_max_attribute_size TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE
                        the max size TableTop Simulator (TTS) can handle for deck image attributes
  --deck_image_max_reference_size TTS_DECK_IMAGE_MAX_REFERANCE_SIZE
                        the max size TableTop Simulator (TTS) can handle for reference attributes
  --directory DIRECTORY
                        path to directory that images will be output
  --gcreds GCREDS       path to the credential.json file for google-api access
  --keep_creds          tell the script to delete any tokens it generates during processing
  --glob GLOB           regex used to pull multiple files from a path
  --file FILE           path to a single file that will be used by the script
  --glink GLINK         link pointing to a file in a google drive
  --author AUTHOR       the author to put in the output pdf
  --title TITLE         the title to put in the output pdf
  --subject SUBJECT     the subject to put in the output pdf
```
