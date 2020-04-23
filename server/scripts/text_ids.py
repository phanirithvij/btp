import sys

# python server\scripts\text_ids.py corpora\toi_text.txt corpora\out.txt

assert len(sys.argv) == 3

with open(sys.argv[1], 'r') as inp:
    with open(sys.argv[2], 'w+') as out:
        x = 0
        for line in inp.readlines():
            # remove empty lines
            if line.strip() != '':
                x += 1
                out.write(str(x) + "||" + line)
