from concrete import fhe
import random
import time


####### UTILS ##########

def execute_and_time(f, *args):
    start_time = time.time()
    result = f(*args)
    end_time = time.time()
    print(f"Execution time : {end_time - start_time} seconds")
    return result


####### BOOLEAN FUNCITONS #######

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

def is_alive_in_native(cell, neighbours, zeros):
    sum_neighbours = sum(neighbours, zeros)
    sum_is_2_or_3 = sum_neighbours[1] and (not sum_neighbours[2])
    sum_is_3 = sum_neighbours[0] and sum_neighbours[1] and (not sum_neighbours[2])    
    alive = sum_is_3 or (cell and sum_is_2_or_3)
    return int(alive)

# The encryption of zero is different under different key
def is_alive(cell, neighbours, zeros):
    sum_neighbours = sum(neighbours, zeros)
    sum_is_2_or_3 = AND(sum_neighbours[1], NOT(sum_neighbours[2]))
    sum_is_3 = AND(sum_neighbours[0], AND(sum_neighbours[1], NOT(sum_neighbours[2])))
    alive = OR(sum_is_3, (cell * sum_is_2_or_3))
    return alive

###### TESTING ######


def execute_on_inputs(circuit, cell, neighbours, zeros):
    encrypted_cell, encrypted_neighbours, encrypted_zeros = circuit.encrypt(cell, neighbours, zeros)
    # print('Encrypted inputs:', encrypted_cell.serialize(), encrypted_neighbours.serialize(), encrypted_zeros.serialize())

    encrypted_result = circuit.run(encrypted_cell, encrypted_neighbours, encrypted_zeros)
    # print('Encrypted Result', encrypted_result.serialize())

    return circuit.decrypt(encrypted_result)


inputset = [
    (0, [0 for i in range(8)], [0 for i in range(3)]), 
    (1, [1 for i in range(8)], [0 for i in range(3)])
]
compiler = fhe.Compiler(
    is_alive, 
    {"cell": "encrypted", "neighbours": "encrypted", "zeros": "encrypted"}
)
print('Compiling...')
circuit = compiler.compile(inputset)
print('Keygen...')
circuit.keygen()


print('Running function on inputs')

# Test 1
cell = 1
neighbours = [1, 1, 1, 1, 1, 1, 1, 1]
zeros = [0, 0, 0]
result = execute_on_inputs(circuit, cell, neighbours, zeros)
print('Result:', result, 'Result (native execution):', is_alive_in_native(cell, neighbours, zeros))


# Test 2
cell = 0
neighbours = [1, 1, 1, 0, 0, 0, 0, 0]
zeros = [0, 0, 0]
result = execute_on_inputs(circuit, cell, neighbours, zeros)
print('Result:', result, 'Result (native execution):', is_alive_in_native(cell, neighbours, zeros))


# Test 3
cell = 1
neighbours = [1, 1, 1, 0, 0, 0, 0, 0]
zeros = [0, 0, 0]
result = execute_on_inputs(circuit, cell, neighbours, zeros)
print('Result:', result, 'Result (native execution):', is_alive_in_native(cell, neighbours, zeros))

# Test 4
cell = 1
neighbours = [1, 1, 0, 0, 0, 0, 0, 0]
zeros = [0, 0, 0]
result = execute_on_inputs(circuit, cell, neighbours, zeros)
print('Result:', result, 'Result (native execution):', is_alive_in_native(cell, neighbours, zeros))


