import argparse
import curses
import random
import sys
import time

import word_lookups

__version__ = "2.0.0"

URANDOM = random.SystemRandom()
NUM_DIE_ROLLS_PER_WORD = 5  # Diceware does 5 die rolls per word

# Declares get_time() as a method that gets the time with microsecond precision across all platforms.
# Code from Python's timeit module
# http://hg.python.org/cpython/file/2.7/Lib/timeit.py
if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    get_time = time.clock
else:
    # On most other platforms the best timer is time.time()
    get_time = time.time


def roll_dice(window, options, rolls_left):
    """
    Simulate a dice roll. Returns an integer value between 1 and 6 (inclusive)
    """
    if options.urandom:
        return URANDOM.randint(1, 6)

    # print the number of rolls left
    y, x = window.getyx()
    window.clrtoeol()
    window.addstr(y, x, str(rolls_left))
    window.move(y, x)

    start_time = get_time()
    window.getch()  # block until a key is pressed
    stop_time = get_time()

    delta = abs(stop_time - start_time)  # TODO: use a monotonically increasing clock time (available in Python 3.3)
    delta_microseconds = (delta - int(delta)) * 1000000
    # Fraction should always be between [0, 1)
    # Using the last 3 digits which strikes a good balance between more digits
    # (more digits means more even distribution across buckets)
    # and delta time precision (higher precision, i.e. fewer digits, means more randomness and less keypress cadence)
    fraction = float(delta_microseconds % 1000) / 1000
    return int(fraction * 6) + 1


def generate_passphrases(window, options):
    window.scrollok(True)
    window.idlok(True)

    word_lookup = word_lookups.EFF_WORD_LOOKUP
    if options.wordlist == "diceware":
        word_lookup = word_lookups.DICEWARE_WORD_LOOKUP
    elif options.wordlist == "beale":
        word_lookup = word_lookups.BEALE_WORD_LOOKUP

    if not options.urandom:
        window.addstr("Die rolls are calculated using the microseconds between your keypresses.\n")

    generate_passphrases = True
    while generate_passphrases:
        rolls_left = options.num_words * NUM_DIE_ROLLS_PER_WORD

        if not options.urandom:
            window.addstr("Key presses left: ")

        words = []
        for word_n in range(options.num_words):
            word_index = 0  # Accumulator for the die rolls per word
            for dice_n in range(NUM_DIE_ROLLS_PER_WORD):
                word_index += (10 ** dice_n) * roll_dice(window, options, rolls_left)
                rolls_left -= 1

            words.append(word_lookup[word_index])

        if not options.urandom:
            window.addstr("\n")

        window.addstr("Generated passphrase: %s\n" % " ".join(words))
        window.addstr("Do you want to generate another password? [y/n]")
        user_input = None
        while True:
            user_input = chr(window.getch()).lower()
            if user_input in ("y", "n"):
                y, x = window.getyx()
                window.insstr(y, x, user_input)
                break

        generate_passphrases = user_input == "y"
        window.addstr("\n")


def main():
    parser = argparse.ArgumentParser(description="Generates passphrases using the Diceware method.\n"
                                     "See http://world.std.com/~reinhold/diceware.html")
    parser.add_argument("-n", "--num_words", dest="num_words", type=int, default=5,
                        help="The number of words in the passphrase to generate")
    parser.add_argument("--urandom", dest="urandom", action="store_true",
                        help="Use urandom (supposedly cryptographically secure, depending on your entropy pool)")
    parser.add_argument("--wordlist", dest="wordlist", default="eff", choices=("eff", "diceware", "beale"),
                        help="The wordlist to use. All wordlists provide the same level of security "
                        "but different levels of usability. The default (eff) is the most usable.")
    parser.add_argument("-v", "--version", action="version", version=__version__)

    options = parser.parse_args()

    curses.wrapper(generate_passphrases, options)


if __name__ == "__main__":
    main()
