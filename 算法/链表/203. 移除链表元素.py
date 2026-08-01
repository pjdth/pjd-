# 203.移除链表元素
#
# 给你一个链表的头节点head和一个整数val，请你删除链表中所有满足Node.val一val的节点，并
# 返回新的头节点。
# 示例 1:
# 输入:head= [1,2,6,3,4,5,6]，val =6
# 输出：[1,2,3,4,5]
# 示例 2:
# 输入:head=[]，val=1
# 输出：[]
# 示例 3:
# 输入:head=[7,7,7,7]，val=7
# 输出：[]
# Definition for singly-linked list.
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def removeElements(self, head: Optional[ListNode], val: int) -> Optional[ListNode]:
        cur=cur1=ListNode(next=head)
        while cur.next:
            if cur.next.val==val:
                cur.next=cur.next.next
            else:
                cur=cur.next
        return cur1.next
