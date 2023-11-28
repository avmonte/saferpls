import numpy as np
import math
from copy import deepcopy
import sys


# python3 main.py [-e | -d] [file.txt] [key]
mode = sys.argv[2]
original_file = sys.argv[3]
original_key = str(sys.argv[4])


def read_file(file):
	# reading in binary
	with open(file, "rb") as f:
		content = f.read()
		print(content)
		no_bytes = len(content)

		return [content[i:i+16] for i in range(0, no_bytes, 16)] # OPTIMIZE


def ensure_length(key):
	# ensures the one of the 3 allowed lengths and formats into bytes
	# TODO
	# must return a key length
	return len(key)


def key_schedule(key):
	key_length = ensure_length(key) #

	# General case
	# lambda x, k: ((x << k) & 0xFF) | (x >> 8 - k)
	#
	# Specific case
	bit_rotation = lambda x: ((x << 3) & 0xFF) | (x >> 5)

	schedule = [key]

	sth = key[0]
	for i in key[1:]:
		sth ^= i

	key_template = deepcopy(key).append(sth)

	for i in range(key_length):  # Are you sure?
		key_template = [bit_rotation(j) for j in key_template]
		schedule.append(key_template[i+1:] + key_template[:i])
		# One more operation remains to be added (Bias)


def encrypt():
	pass


def decrypt():
	pass


def main():
	global blocks
	blocks = read_file(original_file)

	# FIXME: validate the key length
	# if len(bin(original_key)) not in (128, 192, 256):
	#   return 'Invalid key'

	if mode == '-e':
		encrypt()
	elif mode == '-d':
		decrypt()
	else:
		return 'Invalid mode'


print(main())
