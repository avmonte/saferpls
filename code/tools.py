# Helper functions defined to structure the main source

def bit_rotate(x, k):
	return ((x << k) & 0xFF) | (x >> 8 - k)


def discrete_log(x):
	for j in range(257):
		check = pow(45, j + 1, 257)
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
				out.append((45 ** i) % 257 if i != 128 else 0)
			case 'l':  # log
				out.append(discrete_log(i) if i != 0 else 128)

	return out
