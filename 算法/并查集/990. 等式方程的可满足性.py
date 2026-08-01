"""
    @Author:th
    @Time:2026/6/26
    @Desc:
"""
from typing import List
# 990.等式方程的可满足性
#
# 给定一个由表示变量之间关系的字符串方程组成的数组，每个字符串方程equations[i]的长度为4，并
# 采用两种不同的形式之一："a==b"或"a！=b"。在这里，a和b是小写字母（不一定不同），表示单字母变
# 量名。
# 只有当可以将整数分配给变量名，以便满足所有给定的方程时才返回true，否则返回false。
# 示例 1:
# 输入：["a==b","b!=a"]
# 输出：false
# 解释：如果我们指定，a=1且b=1，那么可以满足第一个方程，但无法满足第二个方程。没有办
# 法分配变量同时满足这两个方程。
# 示例 2:
# 输入：["b==a","a==b"]
# 输出：true
# 解释：我们可以指定a=1且b=1以满足满足这两个方程。
# 示例 3:
# 输入：["a==b","b==c","a==c"]
# 输出：true
class Solution:
    def equationsPossible(self, equations: List[str]) -> bool:
        sz=[i for i in range(27)]
        def find(i):
            if sz[i]!=i:
                sz[i]=find(sz[i])
            return sz[i]
        def zip1(left,right):
            l1=find(left)
            r1=find(right)
            sz[l1]=r1

        for e in equations:
            if e[1]=='=':
                zip1(ord(e[0])-97,ord(e[-1])-97)
        for e in equations:
            if e[1]=='!':
                if sz[ord(e[0])-97] == sz[ord(e[-1])-97]:
                    return False
        return True