# C8505- Assignment 2 - Steganography

To use the program (requires Python 2.7... probably; we haven't tested other versions ¯\_(ツ)_/¯):
* Install [Pillow](https://python-pillow.org/)
* Encode an image: `./dcstego -i [path to file to encode] carrierimage.bmp`
* Decode an image: `./dcstego stegodimage.bmp`
* Additional options control the output file; see `./dcstego -h`
* The carrier image must currently be a 24-bit RGB BMP image, but we may add support for other images

Image sources (images not listed here are our own images and can be used for whatever you want; they're CC0):
* mountain-landscape.bmp: https://pixabay.com/en/landscape-mountains-abendstimmung-640617
