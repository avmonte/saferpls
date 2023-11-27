import numpy as np
import math
import sys

# python3 main.py [-e | -d] file.txt
mode = sys.argv[2]
original_file = sys.argv[3]


def read_file(file):
	# reading in binary
	with open(file, "rb") as f:
		content = f.read()
		print(content)
		no_bytes = len(content)

		return [content[i:i+16] for i in range(0, no_bytes, 16)] # OPTIMIZE


def encrypt():
	pass


def decrypt():
	pass


def main():
	global blocks
	blocks = read_file(original_file)
	if mode == '-e':
		encrypt()
	elif mode == '-d':
		decrypt()
	else:
		return 'Invalid mode'


print(main())
