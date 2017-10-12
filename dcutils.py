########################################################################################################
# FILE
#
#    Name: dcutils.py
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-20
#
#    Description:
#      This file implements the encoding and decoding of 
#
#    Revisions:
#    (none)
#
#########################################################################################################

import os

MASKS = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

#########################################################################################################
# FUNCTION
#
#    Name: encode_byte
#
#    Prototype:	def encode_byte(srcbyte, dstbytes, dstoffset)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#	   srcbyte   - the byte to be encoded
#      dstbytes  - the bytes into which srcbyte will be encoded
#      dstoffset - the offset into dstbytes at which to start encoding; len(dstbytes) - dstoffset >= 8
#
#    Return Values:
#	   The dstoffset that should be passed to start encoding another byte, assuming that bytes are encoded
#      sequentially.
#
#    Description:
#      Splits srcbyte into bits and encodes the result into the least significant bits
#      of 8 bytes in dstbytes starting at dstoffset
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def encode_byte(srcbyte, dstbytes, dstoffset):
    for i in range(8):
        mask = MASKS[i]
        bit = (srcbyte & mask) >> (7 - i)

        byte = dstbytes[dstoffset + i]
        byte &= 0xFE # zero the last
        byte |= bit  # set the last bit to the one we want to encode

        dstbytes[dstoffset + i] = byte

    return dstoffset + 8

#########################################################################################################
# FUNCTION
#
#    Name: decode_byte
#
#    Prototype:	def decode_byte(srcbytes, srcoffset)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#	   srcbytes  - the bytes containing an encoded byte
#      srcoffset - the offset into srcbytes at which to start decoding; len(srcbytes) - srcoffset >= 8
#
#    Return Values:
#	   A tuple containing the decoded byte and the srcoffset that should be passed to start decoding
#      another byte, assuming that bytes are encoded sequentially.
#
#    Description:
#      Constructs a byte from the least signfificant bits of 8 bytes in srcbytes starting at srcoffset.
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def decode_byte(srcbytes, srcoffset):
    result = 0
    
    for i, byte in enumerate(srcbytes[srcoffset:srcoffset + 8]):
        bit = byte & 0x01
        result |= bit << (7 - i)

    return (result, srcoffset + 8)

#########################################################################################################
# FUNCTION
#
#    Name: encode_filename
#
#    Prototype:	def encode_filename(filename, dstbytes)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#	   filename - the file name to encode - must be <= 255 bytes
#      dstbytes - the bytes into which the name will be encoded
#
#    Return Values:
#	   The offset into dstbytes to start encoding the file's data.
#
#    Description:
#      Encodes the length of filename followed by filename itself into the least significant bits of the
#      first (8 + 8 * len(filename)) bytes in dstbytes.
#
#    Revisions:
#	   (none)
#
#    TODO:
#      Maybe handle Unicode in file names
#    
#########################################################################################################
def encode_filename(filename, dstbytes):
    namesize = len(filename)
    offset = encode_byte(namesize, dstbytes, 0)
    
    for char in filename:
        byte = ord(char)
        offset = encode_byte(byte, dstbytes, offset)

    return offset

#########################################################################################################
# FUNCTION
#
#    Name: decode_filename
#
#    Prototype:	def decode_filename(srcbytes)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#      srcbytes - the bytes containing the file name to decode
#
#    Return Values:
#	   A tuple containing the file name and the offset into srcbytes at which the file's data starts.
#
#    Description:
#      Decodes a filename encoded in srcbytes, starting at byte 0.
#
#    Revisions:
#	   (none)
#
#    TODO:
#      Maybe handle Unicode in file names
#    
#########################################################################################################
def decode_filename(srcbytes):
    name = ""
    namesize, offset = decode_byte(srcbytes, 0)
    
    offset = 8
    for i in range(namesize):
        char, offset = decode_byte(srcbytes, offset)
        name += chr(char)

    return (name, offset)

#########################################################################################################
# FUNCTION
#
#    Name: encode_file
#
#    Prototype:	encode_file(srcpath, dstbytes)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#      srcpath  - the path to the file to encode
#      dstbytes - the buffer into which the file will be encoded
#
#    Return Values:
#	   Whether the encoding succeeded.
#
#    Description:
#      Encodes the contents of the file at srcpath into dstbytes using LSB steganography.
#
#    Revisions:
#	   (none)
#
#########################################################################################################
def encode_file(srcpath, dstbytes):
    filename = os.path.basename(srcpath)
    filesize = os.path.getsize(srcpath)
   
    # Encode the data into the image
    with open(srcpath, 'rb') as payload:
        offset = encode_filename(filename, dstbytes)
        filesizebytes = [(filesize & 0xFF0000) >> 16, (filesize & 0x00FF00) >> 8, filesize & 0x0000FF]

        for byte in filesizebytes:
            offset = encode_byte(byte, dstbytes, offset)

        try:
            strbyte = payload.read(1)
        except:
            print("Failed to read from source file")
            raise

        while strbyte != "":
            byte = ord(strbyte)
            offset = encode_byte(byte, dstbytes, offset)

            try:
                strbyte = payload.read(1)
            except:
                print("Failed to read from source file")
                raise
    
#########################################################################################################
# FUNCTION
#
#    Name: decode_file
#
#    Prototype:	decode_file(srcbytes, dstpath, keep_extension)
#
#    Developers: Mat Siwoski/Shane Spoor
#
#    Created On: 2017-09-30
#
#    Parameters:
#      srcbytes - the buffer containing the encoded file
#
#    Return Values:
#	   A tuple containing (decoded filename, decoded file contents in bytearray).
#
#    Description:
#      Decodes the file contained in srcbytes using LSB steganography.
#
#    Revisions:
#	   (none)
#    
#########################################################################################################
def decode_file(srcbytes):

    filename, offset = decode_filename(srcbytes)

    buf = bytearray()
    filesize = 0
    for i in range(3):
        filesizebyte, offset = decode_byte(srcbytes, offset)
        filesize += filesizebyte << ((2 - i) * 8)

    for i in range(filesize):
        byte, offset = decode_byte(srcbytes, offset)
        buf.append(byte)

    return (filename, buf)
