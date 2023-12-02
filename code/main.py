import sys
import re
import numpy as np
from copy import deepcopy
from time import time

from tools import *


def validate_format():
	# python3 main.py [-e | -d] [file.txt] "[key]"
	args = sys.argv

	# Validate number of arguments
	if len(args) != 4:
		return 'Argument missing'

	# Validate the first argument (mode)
	mode = args[1]
	if not re.match(r'-e|-d', mode):
		return 'Invalid mode'

	# Validate and format the second argument (file)
	with open(args[2], "rb") as f: # reading in binary
		content = f.read()
		no_bytes = len(content)

		# Padding
		off = no_bytes % 16
		if off != 0:
			content += (padding[off - 1:]).encode()

		blocks = [content[i:i + 16] for i in range(0, no_bytes, 16)]

	# Validate and format the third argument (key)
	# TODO: this be done through re
	original_key = args[3]
	length = len(original_key)
	if all(i in '0123456789abcdefABCDEF' for i in original_key) and length in (32, 48, 64):
		key = [int(original_key[i:i+2], 16) for i in range(0, length, 2)]
		length //= 2
	elif len(original_key) in (16, 24, 32):
		key = [ord(i) for i in original_key]
	else:
		return 'Invalid key'

	return blocks, key, length, mode


def generate_key_schedule(key, key_length):
	schedule = [key[:16]]  # list of subkeys from 1 to key length + 1 inclusive
	# (each subkey is a string of the length of the key)

	# create extra byte
	extra_byte = key[0]
	for i in key[1:]:
		extra_byte ^= i

	key_register = list(deepcopy(key)) + [extra_byte]  # load extra byte

	for i in range(key_length):
		key_register = [bit_rotate(j, 3) for j in key_register]
		select = (key_register[i+1:] + key_register[:i])[:16]
		subkey = (np.array(select) + np.array(B_BOX[i + 1])) % 256
		schedule.append(subkey)

	return np.array(schedule)


def step_four_arm(c):
	current = deepcopy(c)
	for k in range(3):
		# 2-PHT
		for j in range(0, BLOCK_SIZE, 2):
			current[j], current[j + 1] = (2 * current[j] + current[j + 1]) % 256, (current[j] + current[j + 1]) % 256

		# Armenian shuffle
		current = [current[ARMENIAN_PATTERN[i] - 1] for i in range(BLOCK_SIZE)]

	# 2-PHT
	for j in range(0, BLOCK_SIZE, 2):
		current[j], current[j + 1] = (2 * current[j] + current[j + 1]) % 256, (current[j] + current[j + 1]) % 256

	return current


def step_four_matrix(c):
	return ((np.array(c) @ np.array(M)) % 256).tolist()


def reverse_step_four_arm(c):
	current = deepcopy(c)
	for k in range(3):
		# 2-PHT
		for j in range(0, BLOCK_SIZE, 2):
			current[j], current[j + 1] = (current[j] - current[j + 1]) % 256, (2 * current[j + 1] - current[j]) % 256

		# Armenian shuffle
		current = [current[ARMENIAN_PATTERN.index(i+1)] for i in range(BLOCK_SIZE)]

	# 2-PHT
	for j in range(0, BLOCK_SIZE, 2):
		current[j], current[j + 1] = (current[j] - current[j + 1]) % 256, (2 * current[j + 1] - current[j]) % 256

	return current


def reverse_step_four_matrix(c):
	# TODO
	pass


def encrypt(blocks, key_schedule, key_length):
	cipher = []

	for block in blocks:
		current = deepcopy(block)  # create a block copy

		# Encryption: Rounds
		for i in range(key_length // 2):
			current = correspond(current, key_schedule[2*i], '^++^' * 4)  # step 1/4
			current = correspond(current, [1] * BLOCK_SIZE, 'elle' * 4)  # step 2/4
			current = correspond(current, key_schedule[2*i+1], '+^^+' * 4)  # step 3/4
			current = step_four_arm(current)  # step_four_matrix(current)

		# Encryption: Last Step
		current = correspond(current, key_schedule[key_length], '^++^' * 4)  # 2 * (key_length // 2)

		cipher.append(current)  # Save manipulated block copy

	return cipher


def decrypt(blocks, key_schedule, key_length):
	plain = []

	for block in blocks:
		current = deepcopy(block)  # create a block copy

		# Encryption: Last Step
		current = correspond(current, key_schedule[key_length], '^--^' * 4)  # 2 * (key_length // 2)

		# Encryption: Rounds
		for i in range((key_length // 2) - 1, -1, -1):
			current = reverse_step_four_arm(current)
			current = correspond(current, key_schedule[2 * i + 1], '-^^-' * 4)
			current = correspond(current, [1] * BLOCK_SIZE, 'leel' * 4)
			current = correspond(current, key_schedule[2 * i], '^--^' * 4)

		plain.append(current)  # Save manipulated block copy

	return plain


def convert_back_to_original_format():
	# TODO: incorporate remove_padding() into this function
	pass


def remove_padding(decrypted):  # TEST
	for i in range(15, -1, -1):
		if decrypted[i] != padding[i]:
			return decrypted[:-1] + decrypted[-1][:i+1]


def main():
	validation = validate_format()
	if len(validation) == 1:
		return validation
	else:
		blocks, key, key_length, mode = validation

	key_schedule = generate_key_schedule(key, key_length)

	print(f"\nKEY ---------> {np.array(key)}")
	if mode == '-e':
		print(f"PLAIN -------> {np.array(blocks)}")
		print(f"CIPHER ------> ", end='')
		return np.array(encrypt(blocks, key_schedule, key_length))
	else:
		print(f"CIPHER -------> {np.array(blocks)}")
		print(f"PLAIN ------> ", end='')
		return np.array(decrypt(blocks, key_schedule, key_length))


start = time()

print(main(), '\n')
print(f"RUNTIME ----> {time() - start}")
