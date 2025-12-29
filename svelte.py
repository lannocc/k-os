#!/usr/bin/env python3
# @%@~LICENSE:OK~@%@

print('kvin')

import k.db as kdb
from k.web import Master

try:
    Master(kdb).run()

except KeyboardInterrupt:
    pass

finally:
    kdb.close()

print('kvoff')

