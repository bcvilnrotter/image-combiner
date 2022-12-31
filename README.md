BASE OPTIONS (help menu)

```
usage: prototype-assist.py [-h] [--deck_image_max_attribute_size TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE] [--deck_image_max_cardback_size TTS_DECK_IMAGE_MAX_CARDBACK_SIZE] {deckbuilder,mapbuilder} ...

Python Pillow Module
--------------------
Features:
- deckbuilder: takes an original image and converts it into a deck image for us in TTS prototypes
- mapbuilder: takes a background image, and smaller resource images to randomly place across the background image

positional arguments:
  {deckbuilder,mapbuilder}
                        used to organize the different sub functions of the script

options:
  -h, --help            show this help message and exit
  --deck_image_max_attribute_size TTS_DECK_IMAGE_MAX_ATTRIBUTE_SIZE
                        the max size TableTop Simulator (TTS) can handle for deck image attributes
  --deck_image_max_cardback_size TTS_DECK_IMAGE_MAX_CARDBACK_SIZE
                        the max size TableTop Simulator (TTS) can handle for cardback attributes

=========
Examples:

Make deck face images for TableTop Simulator (TTS) from a directory filled with images,
        using a cardback image reference to match size.

python prototype-assist.py deckbuilder -d /path/to/directory/ -c /path/to/cardback/image
=========
```

DECKBUILDER OPTIONS (help menu)

```
usage: prototype-assist.py deckbuilder [-h] [-d DIRECTORY] [-i IMAGE] [-c CARDBACK] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        path to directory containing multiple base images
  -i IMAGE, --image IMAGE
                        Path to our base image
  -c CARDBACK, --cardback CARDBACK
                        path to the card back that will be used with tabletop simulator (TTS)
  -o OUTPUT, --output OUTPUT
                        optional path to output directory
```

MAPBUILDER OPTIONS (help menu)

```
usage: prototype-assist.py mapbuilder [-h] [-a ASSETS] [-i IMAGE]

options:
  -h, --help            show this help message and exit
  -a ASSETS, --assets ASSETS
                        path to the directory containing multiple images that are assets for the map
  -i IMAGE, --image IMAGE
                        path to the background image used for the map
```