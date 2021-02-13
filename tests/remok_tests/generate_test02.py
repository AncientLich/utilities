import random

with open('test01.txt', 'r', encoding='utf-8') as fi:
    text=fi.read().split('\n')


with open('test02.txt', 'w', encoding='utf-8') as fo:
    print('# this is a fake file randomizing the order of the same content of test01.txt'
          '\n# this file is obtained running the generate_test02.py script\n', file=fo)
    while len(text) > 1:
        val = random.randint(0, (len(text) -1))
        line = text.pop(val)
        print(line, file=fo)
    print(text[0], file=fo)

    
