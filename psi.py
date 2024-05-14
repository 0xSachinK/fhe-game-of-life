from concrete import fhe
import random
import time

def set_intersection(set1, set2):
    # Assuming set1 and set2 only contain binary values
    intersection = [set1[i] * set2[i] for i in range(len(set1))]
    # output = 0
    # for i in range(len(set1)):
    #     output += intersection[i]
    for i in range(len(set1)):
        output += intersection[i] * (2 ** i)
    return output

compiler = fhe.Compiler(set_intersection, {"set1": "encrypted", "set2": "encrypted"})

set_len = 2
inputset = [
    (
        [0 for i in range(set_len)], 
        [0 for i in range(set_len)]
    ), 
    (
        [1 for i in range(set_len)], 
        [1 for i in range(set_len)]
    )
]

start = time.time()
circuit = compiler.compile(inputset)
end = time.time()
print('Compilation', end - start)

start = time.time()
circuit.keygen()
end = time.time()
print('Keygen', end - start, 's')

circuit.keys.load()

start = time.time()
set_x = [random.randint(0, 1) for i in range(set_len)]
set_y = [random.randint(0, 1) for i in range(set_len)]
print('set_x', set_x)
print('set_y', set_y)
encrypted_x, encrypted_y = circuit.encrypt(set_x, set_y)
print()
end = time.time()
print('encryption', end - start, 's')

start = time.time()
encrypted_result = circuit.run(encrypted_x, encrypted_y)
end = time.time()
print('run', end - start, 's')

start = time.time()
result = circuit.decrypt(encrypted_result)
end = time.time()
print('decrypt', end - start, 's')


print(result)

print(set_intersection(set_x, set_y))