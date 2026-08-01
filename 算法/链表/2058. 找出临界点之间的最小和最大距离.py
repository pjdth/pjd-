# 2058.找出临界点之间的最小和最大距离
# 算术评级:4第265场周赛Q2第二季度C同步题目状态
import math
from typing import Optional, List


# 链表中的临界点定义为一个局部极大值点或局部极小值点。
# 如果当前节点的值严格大于前一个节点和后一个节点，那么这个节点就是一个局部极大值点。
# 如果当前节点的值严格小于前一个节点和后一个节点，那么这个节点就是一个局部极小值点。
# 注意：节点只有在同时存在前一个节点和后一个节点的情况下，才能成为一个局部极大值点/极小值点。
# 给你一个链表head，返回一个长度为2的数组[minDistance，maxDistance]，其中minDistance是
# 任意两个不同临界点之间的最小距离，maxDistance是任意两个不同临界点之间的最大距离。如果临界点
# 少于两个，则返回[-1，-1]。

# 输入:head=[5,3,1,2,5,1,2]
# 输出：[1,3]
# 解释：存在三个临界点：
# -[5,3,1,2,5,1,2]：第三个节点是一个局部极小值点，因为1比3和2小。
# -[5,3,1,2,5,1,2]：第五个节点是一个局部极大值点，因为5比2和1大。
# 一[5,3,1,2,5,1,2]：第六个节点是一个局部极小值点，因为1比5和2小。
# 第五个节点和第六个节点之间距离最小。minDistance=6-5=1。
# 第三个节点和第六个节点之间距离最大。maxDistance=6-3=3。
# 示例3:
# 输入：head=[1,3,2,2,3,2,2,2,7]
# 输出：[3,3]
# 解释：存在两个临界点：
# -[1,3,2,2,3,2,2,2,7]：第二个节点是一个局部极大值点，因为3比1和2大。
# -[1,3,2,2,3,2,2,2,7]：第五个节点是一个局部极大值点，因为3比2和2大。
# 最小和最大距离都存在于第二个节点和第五个节点之间。
# 因此，minDistance和maxDistance是 5-2=3。
# 注意，最后一个节点不算一个局部极大值点，因为它之后就没有节点了。

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def nodesBetweenCriticalPoints(self, head: Optional[ListNode]) -> List[int]:
        first, second,final = 0,-math.inf,0
        max1, min1 = -math.inf, math.inf
        a=head.val
        left=0
        while head and head.next is not None:
            if (a<head.val and head.val>head.next.val) or (a>head.val and head.val<head.next.val):
                if first==0:
                    first=left
                    second=left
                elif final==0:
                    final=left
                    min1 = min(min1, final - second)
                else:
                    second=final
                    final=left
                    min1 = min(min1, final-second)
            a = head.val
            head = head.next
            left = left + 1
        if final==0:
            return [-1,-1]
        max1=final-first
        return [min1,max1]

