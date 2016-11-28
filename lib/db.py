import shelve

db = shelve.open('cache', writeback=True)
