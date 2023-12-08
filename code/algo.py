import numpy as np
from copy import deepcopy

from tools import *

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
