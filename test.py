# -*- coding: utf-8 -*-

import os
print(os.device_encoding(1))
test = 'test'
test1 = "éè"



print(type(test1))
test1 = test1.encode('latin-1')
print(type(test1))

print(test1)
for c in test1:
    print(c)