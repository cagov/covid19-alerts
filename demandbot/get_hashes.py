import argparse

parser = argparse.ArgumentParser(description='demandbot')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('words', nargs='+', help='Words to hash')
args = parser.parse_args()

def hashCode(w):
    hash = 0
    if len(w) == 0:
        return hash
    for chr in w:
        hash = ((hash << 5) - hash) + ord(chr)
        hash &= 0xFFFFFFFF
    if hash & 0x80000000:
        hash -= 0x100000000
    return hash

for word in args.words:
    print(word,hashCode(word))
