
"""SOME TEST ON TIME IN PROJECT"""


from datetime import datetime

a = datetime.now()

b = '2023-03-14 21:31:17.501973'

c = datetime.fromisoformat(b)

print(c)

d = datetime.now().isoformat()

z = datetime.fromisoformat('2023-03-14 23:20:42.052749')


a = '2023-03-15 00:30:19.112114'

b = '2023-03-15 00:36:44.001889'

print(datetime.fromisoformat(a) <= datetime.fromisoformat(b))