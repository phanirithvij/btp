import sys


def split(filename, interval=1000) -> int:
    """
    Splits the [file] into chunks of equal length of [interval] except the last file
    Returns the number of files split into.
    """
    with open(filename, 'r') as inp:
        lines = []
        ind = 0
        for x, line in enumerate(inp.readlines()):
            lines.append(line)
            if (x+1) % interval == 0:
                ind += 1
                with open(f"out{ind}.txt", 'w+') as out:
                    out.writelines(lines)
                lines.clear()
        ind += 1
        with open(f"out{ind}.txt", 'w+') as out:
            out.writelines(lines)
        lines.clear()

    return ind


if __name__ == '__main__':
    # python server\scripts\split.py corpora\out.txt

    assert len(sys.argv) == 2

    print("Number of files", split(sys.argv[1]))
