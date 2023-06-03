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