# list=[]
# i=2
# for i in range (2,100):
#     j=2
#     for j in range(2,i):
#         if(i%j==0):
#             break
#     else:
#         list.append(i)
# print(list)



def count2(a):
    '''
        整数的二进制表达里有多少个1，复杂度仅为1的个数
    '''
    num = 0
    while a != 0:
        a = a & (a - 1)  # 就是这个操作，需要掌握，它的本质含义是抹去了0不考虑
        num += 1
    return num

print(count2(10))

print(bin(10))


a=5
print(bin(5))
print(bin(4))

print(a & (a - 1))


