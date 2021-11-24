#!/usr/bin/env python3
# Python3 code to rename multiple
# files in a directory or folder

# importing os module
import os
import re


# Function to rename multiple files
def main():
    for filename in os.listdir("./"):
        src = filename
        dst = re.sub(' +', ' ', filename)

        # rename() function will
        # rename all the files
        print(f"filename before {src} after {dst}")
        os.rename(src, dst)


# Driver Code
if __name__ == '__main__':
    # Calling main() function
    main()
