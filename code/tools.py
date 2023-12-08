# Helper functions defined to structure the main source
from constants import *


def bit_rotate(x, k):
	return ((x << k) & 0xFF) | (x >> 8 - k)


def discrete_log(x):
	for j in range(257):
		check = pow(45, j, 257)
		if check == x:
			return j


def correspond(input_register, subkey, operator_seq):
	out = []
	for i, k, o in zip(input_register, subkey, operator_seq):
		match o:
			case '^':  # xor
				out.append(i ^ k)
			case '+':  # add
				out.append((i + k) % 256)
			case '-':  # sub
				out.append((i - k) % 256)
			case 'e':  # exp
				out.append(exp_f[i])  # WOW
			case 'l':  # log
				out.append(log_f[i])

	return out
