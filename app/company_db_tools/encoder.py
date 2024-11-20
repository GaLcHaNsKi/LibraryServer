table = [
    ["c", "h", "r", "i", "s", "t", "a", "n", "b", "d", "e"],
    ["_", "g", "j", "k", "l", "I", "o", "p", "q", "u", "P"],
    ["w", "x", "y", "$", "A", "M", "C", "1", "E", "F", "G"],
    ["H", "m", "J", "Y", "L", "B", "N", "O", "v", "Q", "R"],
    ["S", "T", "U", "V", "W", "X", "K", "Z", "D", "2", "8"],
    ["4", "5", "6", "7", "3", "9", "0", "f", "#", "z", "@"],
]


def symbol_not_in_message(message):
    for row in table:
        for i in row:
            if i not in message:
                return i


def get_bigrams(message, filler):
    bigrams = []

    i = 1
    while i < len(message):
        if message[i] != message[i - 1]:
            bigrams += [message[i - 1:i + 1]]
            # если остался только один символ
            if i == len(message)-2:
                bigrams += [message[-1]+filler]
                break
            i += 2
            continue
        else:
            bigrams += [message[i - 1] + filler]
            # если остался только один символ
            if i == len(message)-1:
                bigrams += [message[-1]+filler]
                break
            i += 1

    return bigrams


def get_x_y(symbol):
    for y in range(6):
        for x in range(11):
            if symbol == table[y][x]:
                return x, y
    return -1, -1


def encode(message):
    encoded_message = ""
    filler = symbol_not_in_message(message)
    bigrams = get_bigrams(message, filler)

    encoded_bigrams = []
    for bigram in bigrams:
        x1, y1 = get_x_y(bigram[0])
        x2, y2 = get_x_y(bigram[1])
        encoded_bigram = ""

        if y1 == y2:
            encoded_bigram = table[y1][(x1+1)%11]+table[y1][(x2+1)%11]
        elif x1 == x2:
            encoded_bigram = table[(y1 + 1) % 6][x1] + table[(y2 + 1) % 6][x2]
        else:
            encoded_bigram = table[y2][x1] + table[y1][x2]

        encoded_bigrams += [encoded_bigram]

    encoded_message = "".join(encoded_bigrams)

    return encoded_message, filler