"""
    @Author:th
    @Time:2026/5/21
    @Desc:
"""
from typing import List
# 1052.爱生气的书店老板

# 有一个书店老板，他的书店开了分钟。每分钟都有一些顾客进入这家商店。给定一个长度为的整数数组customers，其中
# customers[i]是在第分钟开始时进入商店的顾客数量，所有这些顾客在第分钟结束后离开。
# 在某些分钟内，书店老板会生气。如果书店老板在第分钟生气，那么grumpy[i]=1，否则grumpy[i]=0。
# 当书店老板生气时，那一分钟的顾客就会不满意，若老板不生气则顾客是满意的。
# 书店老板知道一个秘密技巧，能抑制自己的情绪，可以让自己连续minutes分钟不生气，但却只能使用一次。
# 请你返回这一天营业下来，最多有多少客户能够感到满意。
# 示例 1:
# 输入:customers =[1,0,1,2,1,1,7,5],grumpy =[0,1,0,1,0,1,0,1],minutes = 3
# 输出：16
# 解释：书店老板在最后3分钟保持冷静。
# 感到满意的最大客户数量=1+1+1+1+7+5=16.
# 示例 2:
# 输入：customers =[1]，grumpy =[0]，minutes =1
# 输出：1
class Solution:
    def maxSatisfied(self, customers: List[int], grumpy: List[int], minutes: int) -> int:
        num1=[]
        maxSatisfied=0
        sumSatisfied=0
        for i in range(0,len(grumpy)):
            if grumpy[i] > 0:
                num1.append(0)
            else:num1.append(customers[i])
        for k,v in enumerate(num1):
            if k<=len(num1)-minutes:
                sumSatisfied +=customers[k]
                if(len(num1)==minutes):
                    maxSatisfied = max(maxSatisfied, sumSatisfied)
                    break
                i=k
                for i in range(i,len(num1)-1):
                    sumSatisfied +=num1[i]
            maxSatisfied = max(maxSatisfied,sumSatisfied)
        return maxSatisfied