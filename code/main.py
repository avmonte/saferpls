from time import time
from re import match
from sys import argv

from constants import padding
from algo import encrypt, decrypt, generate_key_schedule


def validate_format():
	global filename
	# python3 main.py [-e | -d] [filepath] [key]

	# Validate number of arguments
	if len(argv) != 4:
		return 'Argument missing'

	# Validate the first argument (mode)
	mode = argv[1]
	if not match(r'-e|-d', mode):
		return 'Invalid mode'

	# Validate and format the second argument (file)
	filename = argv[2]
	with open(filename, "rb") as f:  # reading in binary
		content = f.read()
		no_bytes = len(content)

		# Padding
		off = no_bytes % 16
		if off != 0:
			content += (padding[off - 1:]).encode()

		# content += ("png" + 13 * " ").encode()  # TEST
		blocks = [list(content[i:i + 16]) for i in range(0, no_bytes, 16)]

	# Validate and format the third argument (key)
	# TODO: this be done through re
	original_key = argv[3]
	length = len(original_key)
	if all(i in '0123456789abcdefABCDEF' for i in original_key) and length in (32, 48, 64):
		key = [int(original_key[i:i+2], 16) for i in range(0, length, 2)]
		length //= 2
	elif len(original_key) in (16, 24, 32):
		key = [ord(i) for i in original_key]
	else:
		return 'Invalid key'

	return blocks, key, length, mode


def save(text, fname):
	with open(fname, "wb") as f:  # reading in binary
		for i in text:
			f.write(bytes(i))


def remove_padding(decrypted):
	for i in range(15, -1, -1):
		if chr(decrypted[-1][i]) != padding[i-1]:
			return decrypted[:-1] + [decrypted[-1][:i+1]]


def main():
	validation = validate_format()
	if type(validation) == str:
		return validation
	else:
		blocks, key, key_length, mode = validation

	key_schedule = generate_key_schedule(key, key_length)

	if mode == '-e':
		cipher = encrypt(blocks, key_schedule, key_length)
		save(cipher, "enc_" + filename.split('.')[0] + ".enc")
	else:
		plain = remove_padding(decrypt(blocks, key_schedule, key_length))
		save(plain, "dec_" + filename.split('.')[0] + ".txt")


start = time()

main()
print(f"RUNTIME ---> {time() - start}")
