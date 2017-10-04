########################################################################################################
# FILE
#
#    Name: dcstego.py
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-20
#
#    Description:
#     This file drives the steganography program by interpreting command line arguments to
#     which files to encode or decode.
#
#    Revisions:
#    (none)
#
#########################################################################################################

from __future__ import print_function
from PIL import Image

#########################################################################################################
# FUNCTION
#
#    Name: can_encode
#
#    Prototype:	def can_encode(minsize, imgpath)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#	   minsize - the minimum number of bytes that the image must be able to encode
#      imgpath - the path to the image
#
#    Return Values:
#	   True if the image can encode the specified number of bytes, False otherwise. Rethrows exceptions
#      encountered on opening the image.
#
#    Description:
#      Determines whether the image at imgpath can encode at least minsize bytes. If not, prints an error
#      message and returns False.
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def can_encode(minsize, imgpath):
    # check if the image is large enough to hold minsize bytes
    try:
        carrier = Image.open(imgpath, 'r')
    except:
        print("Could not open {}.".format(imgpath))

    w, h = carrier.size
    
    # Assume RGB images for now - we'll get to more complicated stuff later if there's time
    bytesize = w * h * 3

    carrier.close()

    if bytesize < minsize:
        print("Image is too small to hold file's contents: image size is {} bytes, but minimum required is {} bytes.".format(carriersize, minsize))
        return False

    return True

#########################################################################################################
# FUNCTION
#
#    Name: get_pixels
#
#    Prototype:	def get_pixels(imgpath)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#      imgpath - the path to the image
#
#    Return Values:
#	   A tuple containing a writable buffer of raw pixels and an Image object describing the image.
#      Rethrows exceptions encountered on opening the file.
#
#    Description:
#      Attempts to open the image at imgpath and get a buffer of its pixels for writing.
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def get_pixels(imgpath):
    try:
        img = Image.open(imgpath, 'r')
    except:
        print("Could not open {}.".format(imgpath))
        raise

    return (bytearray(img.tobytes()), img)

#########################################################################################################
# FUNCTION
#
#    Name: save_pixels
#
#    Prototype:	def save_pixels(pixels, carrier, dstpath)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#      pixels  - the pixels to save as an image; must be a read-only buffer (e.g. bytes() or str())
#      carrier - the Image object retrieved from get_pixels
#      dstpath - the location to which the resulting image should be saved
#
#    Return Values:
#	   None. Rethrows exceptions encountered on saving the file.
#
#    Description:
#      Attempts to save the pixels to dstpath with the same image format as the carrier image. Note that
#      saving to a path with an extension other than the original image isn't checked here, so you could
#      e.g. open a BMP in get_pixels and pass a dstpath that ends in '.png', but it will still save in the
#      BMP format.
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def save_pixels(pixels, carrier, dstpath):
    try:
        dstimage = Image.frombytes(carrier.mode, carrier.size, pixels)
        dstimage.save(dstpath, carrier.format)
    except Exception, error:
        print("Couldn't save result image to {}.".format(dstpath))
        raise
