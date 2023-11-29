import numpy as np
from copy import deepcopy
import sys

# Bias Matrix (B1 is set to zero, as it is not used)
b_box = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
				[70, 151, 177, 186, 163, 183, 16, 10, 197, 55, 179, 201, 90, 40, 172, 100],
				[236, 171, 170, 198, 103, 149, 88, 13, 248, 154, 246, 110, 102, 220, 5, 61],
				[138, 195, 216, 137, 106, 233, 54, 73, 67, 191, 235, 212, 150, 155, 104, 160],
				[93, 87, 146, 31, 213, 113, 92, 187, 34, 193, 190, 123, 188, 153, 99, 148],
				[42, 97, 184, 52, 50, 25, 253, 251, 23, 64, 230, 81, 29, 65, 68, 143],
				[221, 4, 128, 222, 231, 49, 214, 127, 1, 162, 247, 57, 218, 111, 35, 202],
				[58, 208, 28, 209, 48, 62, 18, 161, 205, 15, 224, 168, 175, 130, 89, 44],
				[125, 173, 178, 239, 194, 135, 206, 117, 6, 19, 2, 144, 79, 46, 114, 51],
				[192, 141, 207, 169, 129, 226, 196, 39, 47, 108, 122, 159, 82, 225, 21, 56],
				[252, 32, 66, 199, 8, 228, 9, 85, 94, 140, 20, 118, 96, 255, 223, 215],
				[250, 11, 33, 0, 26, 249, 166, 185, 232, 158, 98, 76, 217, 145, 80, 210],
				[24, 180, 7, 132, 234, 91, 164, 200, 14, 203, 72, 105, 75, 78, 156, 53],
				[69, 77, 84, 229, 37, 60, 12, 74, 139, 63, 204, 167, 219, 107, 174, 244],
				[45, 243, 124, 109, 157, 181, 38, 116, 242, 147, 83, 176, 240, 17, 237, 131],
				[182, 3, 22, 115, 59, 30, 142, 112, 189, 134, 27, 71, 126, 36, 86, 241],
				[136, 70, 151, 177, 186, 163, 183, 16, 10, 197, 55, 179, 201, 90, 40, 172],
				[220, 134, 119, 215, 166, 17, 251, 244, 186, 146, 145, 100, 131, 241, 51, 239],
				[44, 181, 178, 43, 136, 209, 153, 203, 140, 132, 29, 20, 129, 151, 113, 202],
				[163, 139, 87, 60, 130, 196, 82, 92, 28, 232, 160, 4, 180, 133, 74, 246],
				[84, 182, 223, 12, 26, 142, 222, 224, 57, 252, 32, 155, 36, 78, 169, 152],
				[171, 242, 96, 208, 108, 234, 250, 199, 217, 0, 212, 31, 110, 67, 188, 236],
				[137, 254, 122, 93, 73, 201, 50, 194, 249, 154, 248, 109, 22, 219, 89, 150],
				[233, 205, 230, 70, 66, 143, 10, 193, 204, 185, 101, 176, 210, 198, 172, 30],
				[98, 41, 46, 14, 116, 80, 2, 90, 195, 37, 123, 138, 42, 91, 240, 6],
				[71, 111, 112, 157, 126, 16, 206, 18, 39, 213, 76, 79, 214, 121, 48, 104],
				[117, 125, 228, 237, 128, 106, 144, 55, 162, 94, 118, 170, 197, 127, 61, 175],
				[229, 25, 97, 253, 77, 124, 183, 11, 238, 173, 75, 34, 245, 231, 115, 35],
				[200, 5, 225, 102, 221, 179, 88, 105, 99, 86, 15, 161, 49, 149, 23, 7],
				[40, 1, 45, 226, 147, 190, 69, 21, 174, 120, 3, 135, 164, 184, 56, 207],
				[8, 103, 9, 148, 235, 38, 168, 107, 189, 24, 52, 27, 187, 191, 114, 247],
				[53, 72, 156, 81, 47, 59, 85, 227, 192, 159, 216, 211, 243, 141, 177, 255],
				[62, 220, 134, 119, 215, 166, 17, 251, 244, 186, 146, 145, 100, 131, 241, 51]])


# python3 main.py [-e | -d] [file.txt] "[key]"
mode = sys.argv[1]
original_file = sys.argv[2]
original_key = sys.argv[3]

key = [int(i, 16) for i in original_key.split()]
key_length = len(key)


def read_file(file):
	# reading in binary
	with open(file, "rb") as f:
		content = f.read()
		print(content)
		no_bytes = len(content)

		return [content[i:i + 16] for i in range(0, no_bytes, 16)]  # OPTIMIZE


def key_schedule():
	# General case
	# lambda x, k: ((x << k) & 0xFF) | (x >> 8 - k)

	# Specific case
	bit_rotation = lambda x: ((x << 3) & 0xFF) | (x >> 5)

	schedule = [original_key]  # list of subkeys from 1 to key length + 1 inclusive
	# (each subkey is a string of the length of the key)

	# create extra byte
	extra_byte = original_key[0]
	for i in original_key[1:]:
		extra_byte ^= i

	key_register = list(deepcopy(original_key)) + [extra_byte]  # load extra byte

	for i in range(key_length):
		key_register = [bit_rotation(j) for j in key_register]
		select = (key_register[i+1:] + key_register[:i])[:16]
		subkey = (np.array(select) + np.array(b_box[i+1])) % 256
		schedule.append(subkey)

	return np.array(schedule)


def encrypt():
	pass


def decrypt():
	pass


def main():
	global blocks
	blocks = read_file(original_file)

	if key_length not in (16, 24, 32):
		return 'Invalid key'

	if mode == '-e':
		encrypt()
	elif mode == '-d':
		decrypt()
	else:
		return 'Invalid mode'


print(main())
