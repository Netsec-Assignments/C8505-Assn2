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

#!/usr/bin/env python3


#########################################################################################################
# FUNCTION
#
#    Name:		intro
#
#    Prototype:	def intro
#
#    Developer:	Mat Siwoski
#
#    Created On: 2017-09-20
#
#    Parameters:
#
#    Return Values:
#	
#    Description:
#    This function prints the intro to the user.
#
#    Revisions:
#	(none)
#    
#########################################################################################################
def intro():
    print("")
    print("    C8505 - Assignment 2 - Stegonography")
    

#########################################################################################################
# FUNCTION
#
#    Name:		main_menu
#
#    Prototype:	def main_menu
#
#    Developer:	Mat Siwoski
#
#    Created On: 2017-09-20
#
#    Parameters:
#
#    Return Values:
#	
#    Description:
#    This function takes the options for the user and displays the menu.
#
#    Revisions:
#	(none)
#    
#########################################################################################################
def main_menu():
    choice = 0
    print("")
    print("        1. Server")
    print("        2. Client")
    print("        3. Set Host IP")
    print("        4. Quit")
    print("")
    choice = input("Please choose an option: ")
    if choice == "1":
        print(" Choice 1")
    elif choice == "2":
        print(" Choice 2")
        #else:
        #    main_menu() 
    elif choice == "3":
        print(" Choice 3")
    elif choice == "4":
        print(" Choice 4")

#########################################################################################################
# FUNCTION
#
#    Name:		main
#
#    Prototype:	def main
#
#    Developer:	Mat Siwoski
#
#    Created On: 2017-09-20
#
#    Parameters:
#
#    Return Values:
#	
#    Description:
#    This function runs the program.
#
#    Revisions:
#	(none)
#    
#########################################################################################################
def main():
    intro()    
    main_menu()

main()
