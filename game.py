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


####### GAME FUNCTIONS #########

def sum(elements, zero):
    result = elements[0] + zero
    for i in range(1, len(elements)):
        result = elements[i] + result
    return result

# The encryption of zero is different under different key
def is_alive(cell, neighbours, zero):
    sum_neighbours = sum(neighbours, zero)
    sum_is_2 = sum_neighbours == 2
    sum_is_3 = sum_neighbours == 3
    sum_is_2_or_3 = sum_is_2 | sum_is_3
    alive = sum_is_3 | (cell * sum_is_2_or_3)
    return alive

@fhe.compiler({"enc_states": "encrypted", "enc_zero": "encrypted"})
def board_update(
    enc_states,
    enc_zero
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
            next_is_alive = is_alive(enc_cell, enc_neighbours, enc_zero)
            new_enc_states.append(next_is_alive)

    return fhe.array(new_enc_states)


###### TESTING ######

def print_state(state):
    n = int(len(state) ** 0.5)
    for i in range(n):
        print(''.join('⬛' if state[i * n + j] == 1 else '⬜' for j in range(n)))
    print()


print('Compiling...')
# Could probably switch a bit here for further optimization, because we don't care about sum = 9
inputset = [
    ([0 for _ in range(N_ROWS * N_COLS)], 0), 
    ([1 for _ in range(N_ROWS * N_COLS)], 0)
]
circuit = board_update.compile(inputset, composable=True)
print('Keygen...')
circuit.keygen()


states = [
    1, 0, 0, 0, 0, 0,
    0, 1, 1, 0, 0, 0,
    1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
]
zero = 0

# Simulate the board
rounds = 5
print_state(states)

enc_states, enc_zero = circuit.encrypt(states, zero)

for i in range(rounds):
    # enc_states, enc_zero = execute_and_time('Encrypt', circuit.encrypt, states, zero)
    enc_states = execute_and_time('Run', circuit.run, enc_states, enc_zero)

    # Don't need to decrypt; Decryption is only for printing
    states = execute_and_time('Decrypt', circuit.decrypt, enc_states)
    print_state(states)

