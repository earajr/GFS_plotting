import os
import numpy as np

dir = os.environ['SWIFT_GFS']

test = (os.popen("cat %s/controls/namelist | grep 'fore:' | awk -F: '{print $2}' | tr ',' ' '"%(dir))).read().split()
test = [np.int(f) for f in test]


#for f in test:
#   print(f.lstrip("0"))

print(test)

