# Run as `perl -ni remove-private-index-urls.pl <requirements files>`.
# Removes pip index options that point anywhere but https://pypi.org/.
# Matches -i and the long forms, with a space or `=` before the value.
print unless /^\s*(?:-i|--index-url|--extra-index-url|--trusted-host)(?:\s+|\s*=\s*)(?!https:\/\/pypi\.org\/)/;
