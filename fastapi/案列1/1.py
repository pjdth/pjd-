from queue import Queue
dict={}
dict[123]=Queue()
dict[123].put('我是红神1')
dict[123].put('我是红神2')
dict[123].put('我是红神3')
print(dict[123].get())
print(dict[123].get())
print(dict[123].get())

