"""
    @Author:th
    @Time:2026/6/28
    @Desc:
"""
from typing import Optional


# 2181.合并零之间的节点

# 给你一个链表的头节点head，该链表包含由分隔开的一连串整数。链表的开端和末尾的节点都满足
# Node.val== 0。
# 对于每两个相邻的，请你将它们之间的所有节点合并成一个节点，其值是所有已合并节点的值之和。然
# 后将所有移除，修改后的链表不应该含有任何。
# 返回修改后链表的头节点head。
# 示例 1:
# 输入:head=[0,3,1,0,4,5,2, 0]
# 输出：[4,11]
# 解释：
# 上图表示输入的链表。修改后的链表包含：
# 一标记为绿色的节点之和：3+1=4
# 一标记为红色的节点之和：4+5+2=11
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        sum1=0
        sz1=[]
        while head:
            sum1+=head.val
            if head.next.val==0:
                sz1.append(sum1)
                sum1=0
            if head.next.next is None:
                break
            head=head.next
        l=ListNode()
        l1=l
        for i in sz1:
            l1.next=ListNode(i)
            l1=l1.next
        return l.next