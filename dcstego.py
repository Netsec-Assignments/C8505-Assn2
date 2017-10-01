#!/usr/bin/env python

#/*********************************************************************************************
#       Name:	dcstego.py
#
#       Developer:	Mat Siwoski/Shane Spoor
#
#       Created On: 2017-09-20
#
#       Description:
#       This is a program is a simple LSB stego application. The basic application will be 
#       command-line (bonus marks for UIs), with the appropriate switches to perform the 
#       various functions. The two main functions will be the embedding (hide) and the 
#       extraction functions. The filenames of the cover image, secret image, and output file
#       will also be specified as part of the command line invocation of the program.
#
#       The main function of this file is that it will contain the general functionality such as
#       parsing command line arguments, checking file sizes, file formats, etc. 
#
#    Revisions:
#    (none)
#
###################################################################################################

from __future__ import print_function
from PIL import Image

import argparse
import os
import struct
import sys

MAX_FILESIZE = 16777215 # 2^24 - 1

# TODO: Separate these functions into the correct files

# dcutils.py
MASKS = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

# dcutils.py
#
# splits srcbyte into bits and encodes the result into the least significant bits
# of 8 bytes in dstbytes starting at dstoffset
# 
# len(dstbytes) - dstoffset must be >= 8
#
# returns the new dstoffset
def encode_byte(srcbyte, dstbytes, dstoffset):
    for i in range(8):
        mask = MASKS[i]
        bit = (srcbyte & mask) >> (7 - i)

        byte = dstbytes[dstoffset + i]
        byte &= 0xFE # zero the last
        byte |= bit  # set the last bit to the one we want to encode

        dstbytes[dstoffset + i] = byte

    return dstoffset + 8

# dcutils.py
#
# constructs a byte from the least signfificant bits of 8 bytes in srcbytes, starting at
# srcoffset
#
# len(srcbytes) - srcoffset must be >= 8
#
# returns a tuple containing the decoded byte and the new srcoffset
def decode_byte(srcbytes, srcoffset):
    result = 0
    
    for i, byte in enumerate(srcbytes[srcoffset:srcoffset + 8]):
        bit = ord(byte) & 0x01
        result |= bit << (7 - i)

    return (result, srcoffset + 8)

# dcutils.py
# 
# encodes the file name and its size into the destination bytes, starting at byte 0;
# the file name must be <= 255 bytes
#
# returns the byte offset at which the last character of the file name finishes
#
# TODO: Maybe handle Unicode in file names
def encode_filename(filename, dstbytes):
    namesize = len(filename)
    offset = encode_byte(namesize, dstbytes, 0)
    
    for char in filename:
        byte = ord(char)
        offset = encode_byte(byte, dstbytes, offset)

    return offset

# dcutils.py
# 
# encodes the file name and its size into the destination bytes, starting at byte 0
# the file name must be <= 255 bytes
#
# returns a tuple containing the file name and the byte offset at which the last character of the file name finishes
#
# TODO: Maybe handle Unicode in file names
def decode_filename(srcbytes):
    name = ""
    namesize, offset = decode_byte(srcbytes, 0)
    
    offset = 8
    for i in range(namesize):
        char, offset = decode_byte(srcbytes, offset)
        name += chr(char)

    return (name, offset)

# dcutils.py
#
# encodes the file into the given image, saving the result to dstpath
#
# srcpath is the path to the file, carrier is an Image object, dstpath is pretty self-explanatory
# everything passed to this function is assumed to already exist, so it needs to have been validated in dcstego.py
def encode_file(srcpath, carrier, dstpath):
    filename = os.path.basename(srcpath)
    filesize = os.path.getsize(srcpath)
    
    pixels = bytearray(carrier.tobytes())
   
    # Encode the data into the image
    with open(srcpath, 'rb') as payload:
        offset = encode_filename(filename, pixels)
        filesizebytes = [(filesize & 0xFF0000) >> 16, (filesize & 0x00FF00) >> 8, filesize & 0x0000FF]

        for byte in filesizebytes:
            offset = encode_byte(byte, pixels, offset)

        try:
            strbyte = payload.read(1)
        except:
            print("Failed to read from source file")
            return

        while strbyte != "":
            byte = ord(strbyte)
            offset = encode_byte(byte, pixels, offset)

            try:
                strbyte = payload.read(1)
            except:
                print("Failed to read from source file")
                return

    # save the image to the destination path
    # TODO: Find a way to make this immutable without incurring a copy? Image.frombytes requires an immutable buffer,
    # so have to copy the bytearray
    dstimage = Image.frombytes(carrier.mode, carrier.size, bytes(pixels))
    try:
        dstimage.save(dstpath, carrier.format)
    except:
        print("Couldn't save result image.")
        return

    print("Succesfully saved stego'd image to {}".format(dstpath))
    

# dcutils.py
#
# decodes the file in the given image, saving it to "dstpath" and appending
# the extension from the original file (if any)
#
# img is an Image object, dstpath is a string, keep_extension is a bool
# if dstpath is None, saves to the current dir with the encoded filename
# if dstpath isn't None and keep_extension is True, saves to dstpath + the encoded extension
def decode_file(img, dstpath, keep_extension):
    pixels = img.tobytes()

    filename, offset = decode_filename(pixels)
    if dstpath is None:
        dstpath = os.path.join(os.getcwd(), filename)
    elif keep_extension:
        parts = os.path.splitext(filename)
        if len(parts) < 2:
            print("Warning: encoded filename has no extension; file will be saved to {}".format(dstpath))
        else:
            dstpath += parts[1]

    with open(dstpath, 'wb') as out:
        filesize = 0
        for i in range(3):
            filesizebyte, offset = decode_byte(pixels, offset)
            filesize += filesizebyte << ((2 - i) * 8)

        for i in range(filesize):
            byte, offset = decode_byte(pixels, offset)
            try:
                out.write(chr(byte))
            except:
                print("Failed to write to file.")
                return

    print("Succesfully decoded file and wrote it to {}.".format(dstpath))

# dcstego.py
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="if -i is specified, this is the path to the carrier image; otherwise, it's the path to the stego'd image")
    parser.add_argument("-i", "--infile", help="path to a file to encode in image; if unspecified, assumes that image is a stego'd image")
    parser.add_argument("-o", "--outfile",help="path to the output file; if unspecified and -i is specified, appends .bmp to INFILE, otherwise uses the file name encoded in image")
    parser.add_argument("-e", "--keep-extension", action="store_true", help="if image is a stego'd image, appends the extension of the file name encoded in the image to OUTFILE")
    args = parser.parse_args()

    if args.infile:
        # If infile is specified, we're encoding
        if not os.path.exists(args.infile):
            print("No such file {}".format(args.infile))
            sys.exit(1)
        elif not os.path.isfile(args.infile):
            print("{} must be a regular file but is either a directory or special file".format(args.infile))
            sys.exit(1)

        srcname = os.path.basename(args.infile)
        srcsize = os.path.getsize(args.infile)

        if srcsize > MAX_FILESIZE:
            print("{} is too big; must be <= {} bytes, is {} bytes".format(args.infile, MAX_FILESIZE, srcsize))
            sys.exit(1)

        dstpath = args.outfile if args.outfile else args.infile + ".bmp"

        # The minimum number of bytes in the image to store
        # * the file name size (1 byte) and the file size (3 bytes)
        # * the file name
        # * the file's contents
        minsize = 32 + (8 * len(srcname)) + (8 * srcsize)

        try:
            carrier = Image.open(args.image, 'r')
        except:
            print("Could not open {}.".format(args.image))
            sys.exit(1)

        w, h = carrier.size
    
        # Assume RGB images for now - we'll get to more complicated stuff later if there's time
        carriersize = w * h * 3
        if carriersize < minsize:
            carrier.close()
            print("Image is too small to hold file's contents: image size is {} bytes, but minimum required is {} bytes.".format(carriersize, minsize))
            sys.exit(1)
    
        encode_file(args.infile, carrier, dstpath)
        carrier.close()
    else:
        # We're decoding
        try:
            stegod = Image.open(args.image, 'r')
        except:
            print("Could not open {}.".format(args.image))
            sys.exit(1)

        decode_file(stegod, args.outfile, args.keep_extension)
        stegod.close()

