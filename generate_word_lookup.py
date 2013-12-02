"""
Generates the wordlists to use.
You'll need GnuPG installed to verify signatures.
Once GnuPG is installed, run "gpg --search-keys reinhold@world.std.com" to add the public keys.
To regenerate the word_lookups, run: "python generate_word_lookup.py > word_lookups.py"
"""

import gnupg
import requests

WORDLIST_URLS = {
    "diceware": "http://world.std.com/~reinhold/diceware.wordlist.asc",
    "beale": "http://world.std.com/~reinhold/beale.wordlist.asc"
}


def convert_wordlist_row_to_python(row):
    row_s = row.split("\t")
    return (int(row_s[0]), row_s[1])


def main():
    gpg = gnupg.GPG()
    for wordlist_name, url in WORDLIST_URLS.iteritems():
        signed_response = requests.get(url)
        response = gpg.decrypt(signed_response.text)  # decrypt will verify the signature if it's not encrypted

        if not response.valid:
            print "Invalid signed response for wordlist: %s with url: %s" % (wordlist_name, url)
            continue

        word_lookup = dict(convert_wordlist_row_to_python(r) for r in response.data.splitlines() if r)
        print "%s_WORD_LOOKUP = %s" % (wordlist_name.upper(), repr(word_lookup))


if __name__ == "__main__":
    main()
