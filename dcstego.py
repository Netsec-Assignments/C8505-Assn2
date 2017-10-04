#!/usr/bin/env python

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

import argparse
import os
import sys

import dcimage
import dcutils

MAX_FILESIZE = 16777215 # 2^24 - 1

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

        dstpath = args.outfile if args.outfile else args.infile + os.path.splitext(args.image)[1]

        # The minimum number of bytes in the image to store
        # * the file name size (1 byte) and the file size (3 bytes)
        # * the file name
        # * the file's contents
        minsize = 32 + (8 * len(srcname)) + (8 * srcsize)

        # TODO: Clean up error handling
        success = True
        carrier = None
        try:
            if dcimage.can_encode(minsize, args.image):
                pixels, carrier = dcimage.get_pixels(args.image)
                dcutils.encode_file(args.infile, pixels)
                dcimage.save_pixels(str(pixels), carrier, dstpath)
            else:
                success = False 
        except Exception, error:
            print(str(error))
            success = False
        finally:
            if carrier:
                carrier.close()

        if not success:
            sys.exit(1)

        print("Succesfully saved stego'd image to {}".format(dstpath))
            
    else:
        # We're decoding
        # Best hope that the image actually contains a file, otherwise it's game over
        success = True
        stegod = None
        dstpath = args.outfile
        try:
            pixels, stegod = dcimage.get_pixels(args.image)
            filename, contents = dcutils.decode_file(pixels)
            
            if not args.outfile:
                dstpath = os.path.join(os.getcwd(), filename)
            elif args.keep_extension:
                root, ext = os.path.splitext(filename)

                if ext == '':
                    print("Warning: encoded filename has no extension; file will be saved to {}".format(dstpath))
                else:
                    dstpath += ext
            else:
                dstpath = args.outfile

            with open(dstpath, 'wb') as out:
                out.write(contents)
        except Exception, error:
            print(str(error))
            success = False
        finally:
            if stegod:
                stegod.close()

        if not success:
            sys.exit(1)
