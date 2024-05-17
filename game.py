from concrete import fhe
import random
import time

N_ROWS = 6
N_COLS = 6

####### UTILS ##########

def execute_and_time(message, f, *args):
    start_time = time.time()
    result = f(*args)
    end_time = time.time()
    print(f"INFO: {message}; Execution time : {end_time - start_time} seconds")
    return result


####### BOOLEAN FUNCITONS #######

# Todo: Try fhe.not, fhe.and, fhe.or

def NOT(a):
    return a ^ 1


def AND(a, b):
    return a * b


def OR(a, b):
    return NOT(AND(NOT(a), NOT(b)))


####### GAME FUNCTIONS #########

def add(a, b):
    c1 = a ^ b[0]
    r = a * b[0]
    c2 = r ^ b[1]
    r = r * b[1]
    c3 = r ^ b[2]
    return (c1, c2, c3)

def sum(elements, zeros):
    result = add(elements[0], zeros)
    for i in range(1, len(elements)):
        result = add(elements[i], result)
    return result

# The encryption of zero is different under different key
def is_alive(cell, neighbours, zeros):
    sum_neighbours = sum(neighbours, zeros)
    sum_is_2_or_3 = AND(sum_neighbours[1], NOT(sum_neighbours[2]))
    sum_is_3 = AND(sum_neighbours[0], AND(sum_neighbours[1], NOT(sum_neighbours[2])))
    alive = OR(sum_is_3, (cell * sum_is_2_or_3))
    return alive

@fhe.compiler({"enc_states": "encrypted", "enc_zeros": "encrypted"})
def board_update(
    enc_states,
    enc_zeros
):

    n_rows = N_ROWS
    n_cols = N_COLS

    new_enc_states = []
    for i in range(n_rows):
        # Is this computation "equivalent" to non-constrained computation
        im = n_rows - 1 if i == 0 else i - 1
        ip = 0 if i == n_rows - 1 else i + 1

        for j in range(n_cols):
            jm = n_cols - 1 if j == 0 else j - 1
            jp = 0 if j == n_cols - 1 else j + 1

            # get neighbours
            n1 = enc_states[im * n_cols + jm]
            n2 = enc_states[im * n_cols + j]
            n3 = enc_states[im * n_cols + jp]
            n4 = enc_states[i * n_cols + jm]
            n5 = enc_states[i * n_cols + jp]
            n6 = enc_states[ip * n_cols + jm]
            n7 = enc_states[ip * n_cols + j]
            n8 = enc_states[ip * n_cols + jp]
            
            enc_cell = enc_states[i * n_cols + j]
            enc_neighbours = [n1, n2, n3, n4, n5, n6, n7, n8]
            next_is_alive = is_alive(enc_cell, enc_neighbours, enc_zeros)
            new_enc_states.append(next_is_alive)

    return fhe.array(new_enc_states)


###### TESTING ######

def print_state(state):
    n = int(len(state) ** 0.5)
    for i in range(n):
        print(''.join('⬛' if state[i * n + j] == 1 else '⬜' for j in range(n)))
    print()


print('Compiling...')
inputset = [
    ([0 for _ in range(N_ROWS * N_COLS)], [0 for _ in range(3)]), 
    ([1 for _ in range(N_ROWS * N_COLS)], [0 for _ in range(3)])
]
circuit = board_update.compile(inputset, composable=True)
print('Keygen...')
circuit.keygen()


states = [
    0, 0, 0, 0, 0, 0,
    0, 1, 1, 0, 0, 0,
    0, 1, 1, 0, 1, 0,
    0, 0, 0, 1, 1, 0,
    0, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0
]
zeros = [0 for _ in range(3)]


# Simulate the board
rounds = 5
print_state(states)

enc_states, enc_zeros = circuit.encrypt(states, zeros)

for i in range(rounds):
    # enc_states, enc_zeros = execute_and_time('Encrypt', circuit.encrypt, states, zeros)
    enc_states = execute_and_time('Run', circuit.run, enc_states, enc_zeros)

    # Don't need to decrypt; Decryption is only for printing
    states = execute_and_time('Decrypt', circuit.decrypt, enc_states)
    print_state(states)

