# We named this module `asyn` instead of `asyncio` to get around a name
# collision with the `asyncio` library when running integration tests. Seems
# to be an issue with `unittest discover` and the fact that each directory
# needs to be its own module, meaning that if this were called `asyncio`
# then it does actually conflict with the standard library....
