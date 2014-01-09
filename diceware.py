import argparse
import curses
import random
import time

import word_lookups

__version__ = "0.1.0"

URANDOM = random.SystemRandom()
NUM_DIE_ROLLS_PER_WORD = 5  # Diceware does 5 die rolls per word


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

    start_time = time.time()
    window.getch()  # block until a key is pressed
    stop_time = time.time()

    delta = abs(stop_time - start_time)  # TODO: use a monotonically increasing clock time (available in Python 3.3)
    return (int(delta * 1000000) % 6) + 1  # Use the microsecond precision


def generate_passphrases(window, options):
    window.scrollok(True)
    window.idlok(True)

    word_lookup = word_lookups.DICEWARE_WORD_LOOKUP
    if options.beale:
        word_lookup = word_lookups.BEALE_WORD_LOOKUP

    if not options.urandom:
        window.addstr("Die rolls are calculated using the microseconds between your keypresses.\n")

    generate_passphrases = True
    while generate_passphrases:
        rolls_left = options.num_words * NUM_DIE_ROLLS_PER_WORD

        if not options.urandom:
            window.addstr("Key presses left: ")

        words = []
        for word_n in xrange(options.num_words):
            word_index = 0  # Accumulator for the die rolls per word
            for dice_n in xrange(NUM_DIE_ROLLS_PER_WORD):
                word_index += (10 ** dice_n) * roll_dice(window, options, rolls_left)
                rolls_left -= 1

            words.append(word_lookup[word_index])

        if not options.urandom:
            window.addstr("\n")

        window.addstr("Generated passphrase: %s\n" % " ".join(words))
        window.addstr("Do you want to generate another password? [y/n]")
        user_input = None
        while True:
            user_input = unichr(window.getch()).lower()
            if user_input in ("y", "n"):
                y, x = window.getyx()
                window.insstr(y, x, user_input)
                break

        generate_passphrases = user_input == "y"
        window.addstr("\n")


def main():
    parser = argparse.ArgumentParser(description="Generates passphrases using the Diceware method.\nSee http://world.std.com/~reinhold/diceware.html")
    parser.add_argument("-n", "--num_words", dest="num_words", type=int, default=5, help="The number of words in the passphrase to generate")
    parser.add_argument("--urandom", dest="urandom", action="store_true", help="Use urandom (supposedly cryptographically secure, depending on your entropy pool)")
    parser.add_argument("--beale", dest="beale", action="store_true", help="Use Alan Beale's wordlist")
    parser.add_argument("-v", "--version", action="version", version=__version__)

    options = parser.parse_args()

    curses.wrapper(generate_passphrases, options)


if __name__ == "__main__":
    main()
