table = [
    ["c", "h", "r", "i", "s", "t", "a", "n", "b", "d", "e"],
    ["_", "g", "j", "k", "l", "I", "o", "p", "q", "u", "P"],
    ["w", "x", "y", "$", "A", "M", "C", "1", "E", "F", "G"],
    ["H", "m", "J", "Y", "L", "B", "N", "O", "v", "Q", "R"],
    ["S", "T", "U", "V", "W", "X", "K", "Z", "D", "2", "8"],
    ["4", "5", "6", "7", "3", "9", "0", "f", "#", "z", "@"],
]


def get_bigrams(message):
    bigrams = []

    i = 1
    while i < len(message):
        bigrams += [message[i - 1:i + 1]]
        i += 2

    return bigrams


def get_x_y(symbol):
    for y in range(6):
        for x in range(11):
            if symbol == table[y][x]:
                return x, y
    return -1, -1


def decode(encoded_message, filler):
    encoded_bigrams = get_bigrams(encoded_message)

    bigrams = []
    for encoded_bigram in encoded_bigrams:
        x1, y1 = get_x_y(encoded_bigram[0])
        x2, y2 = get_x_y(encoded_bigram[1])
        bigram = ""

        if y1 == y2:
            bigram = table[y1][(x1-1) % 11]+table[y1][(x2-1) % 11]
        elif x1 == x2:
            bigram = table[(y1 - 1) % 6][x1] + table[(y2 - 1) % 6][x2]
        else:
            bigram = table[y2][x1] + table[y1][x2]

        bigrams += [bigram]

    message = "".join(bigrams)

    return message.replace(filler, "")