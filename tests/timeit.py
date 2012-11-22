import requests
import datetime
import time
import numpy


REQUESTS = 100


times = []
for x in range(1, REQUESTS):
    start = time.time()
    x = requests.get('http://localhost:8000/api/poll')
    times.append(time.time() - start)

print 'requests: {}'.format(REQUESTS)
print 'total: {}'.format(sum(times))
print 'average: {}'.format(numpy.mean(times))
print '\n'
