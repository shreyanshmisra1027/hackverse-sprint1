#number input
n=int(input('Enter the number of lists: '))
l=[]
for i in range(n):
    k=input().split()
    l.append(k)
l=tuple(l)
print(l)
d=dict()
for i in l:
    for j in i:
        if j in d:
            d[j]+=1
        else:
            d[j]=1
o=max(d.values())
m=[]
for i in d.keys():
    if d.get(i)==o:
        m.append(i)
if len(m)==1:
    print(m[0])
else:
    m.sort()
    print(m[0])

