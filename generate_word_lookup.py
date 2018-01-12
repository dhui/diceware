"""
Generates the wordlists to use.

You'll need GnuPG installed to verify signatures.
Once GnuPG is installed, run "gpg --search-keys reinhold@world.std.com" to add the public keys.
Note: The key above is very old and needs GnuPG 1.4.19 or earlier to import and use.

To regenerate the word_lookups, run: "python generate_word_lookup.py > word_lookups.py"
"""

import logging

from distutils.version import LooseVersion

import gnupg
import requests

WORDLIST_URLS = {
    "diceware": "http://world.std.com/~reinhold/diceware.wordlist.asc",
    "beale": "http://world.std.com/~reinhold/beale.wordlist.asc"
}

MAX_GPG_VERSION_STR = "1.4.19"
MAX_GPG_VERSION = LooseVersion(MAX_GPG_VERSION_STR)

EXPECTED_WORDLIST_SIZE = 7776

logger = logging.getLogger("diceware")
logging.basicConfig(format="%(levelname)s %(message)s", level=logging.WARNING)


def convert_wordlist_row_to_python(row):
    row_s = row.split("\t")
    return (int(row_s[0]), row_s[1])


def main():
    # If gnupg may have issues finding your binary, so you may need to specify it e.g. gnupg.GPG("/usr/local/bin/gpg")
    # If gnupg may also have issues finding your gnupg home directory, so that may also need to be specified.
    gpg = gnupg.GPG("/usr/local/bin/gpg")
    if LooseVersion(gpg.binary_version) > MAX_GPG_VERSION:
        logger.error("gpg version (%s) is too new, it must be <= %s" % (gpg.binary_version, MAX_GPG_VERSION_STR))
        return

    for wordlist_name, url in WORDLIST_URLS.iteritems():
        response = requests.get(url)
        data = response.text

        if url.endswith(".asc"):
            decrypted = gpg.decrypt(response.text)  # decrypt will verify the signature if it's not encrypted
            if decrypted.valid:
                data = decrypted.data
            else:
                logger.warning("Skipping wordlist! Invalid signed response for wordlist: %s with url: %s" %
                               (wordlist_name, url))
                continue

        rows = [r for r in data.splitlines() if r]
        word_lookup = dict(convert_wordlist_row_to_python(r) for r in rows)
        if len(word_lookup) != EXPECTED_WORDLIST_SIZE:
            logger.warning("Skipping wordlist %s! %s entries found instead of %s" %
                           (wordlist_name, len(word_lookup), EXPECTED_WORDLIST_SIZE))
            continue
        if len(set(word_lookup.itervalues())) != EXPECTED_WORDLIST_SIZE:
            logger.warning("Skipping wordlist %s! %s unique words found instead of %s" %
                           (wordlist_name, len(word_lookup), EXPECTED_WORDLIST_SIZE))
            continue

        print "%s_WORD_LOOKUP = %s" % (wordlist_name.upper(), repr(word_lookup))


if __name__ == "__main__":
    main()
