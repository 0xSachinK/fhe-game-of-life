from concrete import fhe
import random
import time

def add(a, b):
    c1 = a ^ b[0]
    r = a * b[0]
    c2 = r ^ b[1]
    r = r * b[1]
    c3 = r ^ b[2]
    return (c1, c2, c3)

def sum(elements, zeroes):
    result = add(elements[0], zeroes)
    for i in range(1, len(elements)):
        result = add(elements[i], result)
    return result



###### TESTING ######



compiler = fhe.Compiler(sum, {"elements": "encrypted", "zeroes": "encrypted"})

inputset = [
    ([0 for i in range(8)], [0 for i in range(3)]), 
    ([1 for i in range(8)], [0 for i in range(3)])
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
a = [random.randint(0, 1) for i in range(8)]
b = [0 for i in range(3)]
print('a', a)
print('b', b)
encrypted_a, encrypted_b = circuit.encrypt(a, b)
print(encrypted_a, encrypted_b)
end = time.time()
print('encryption', end - start, 's')

start = time.time()
encrypted_result = circuit.run(encrypted_a, encrypted_b)
end = time.time()
print('run', end - start, 's')

start = time.time()
result = circuit.decrypt(encrypted_result)
end = time.time()
print('decrypt', end - start, 's')


print(result)
print(sum(a, b))