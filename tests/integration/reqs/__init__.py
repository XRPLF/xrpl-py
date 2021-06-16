# We named this module `reqs` instead of `requests` to get around a name
# collision with the `requests` library when running integration tests. Seems
# to be an issue with `unittest discover` and the fact that each directory
# needs to be its own module, meaning that if this were called `requests`
# then it does actually conflict with the library....
