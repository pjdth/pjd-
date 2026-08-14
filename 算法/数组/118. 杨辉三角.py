# 118.杨辉三角
# 相关企业
# 给定一个非负整数
# numRows，生成「杨辉三角」的前
# numRows行。
#
# 在「杨辉三角」中，每个数是它左上方和右上方的数的和。
# 示例
# 1:
# 输入: numRows = 5
# 输出: [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]
# 示例
# 2:
# 输入: numRows = 1
# 输出: [[1]]
from typing import List
class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        fin_sz=[]
        for i in range(numRows):
            if i ==1:
                fin_sz.append([1])
            elif i==2:
                fin_sz.append([1,1])
            else:
                sz1=[]
                for row in range(1,i-1):
                    sz1.append(1)
                    sz1.append(fin_sz[i-1][row-1]+fin_sz[i-1][row])
                sz1.append(1)
                fin_sz.append(sz1)
        return fin_sz

