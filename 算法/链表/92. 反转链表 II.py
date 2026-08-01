# 92.反转链表I
#
# 给你单链表的头指针head和两个整数left和right，其中left<= right。请你反转从位置left
# 到位置right的链表节点，返回反转后的链表。
# 示例 1:
#
# 输入:head=[1,2,3,4,5]，left = 2,right =4
# 输出：[1,4,3,2,5]
# 示例 2:
# 输入:head =[5]，left =1，right =1
# 输出：[5]
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if left == right:
            return head
        dummy = ListNode(-1, head)
        cur = head
        i=1
        cur_next=fin1=late=None
        while i<left:
            fin1=cur.next
            late=cur
            cur = cur.next
            i+=1
        while i<=right:
            cur_next = cur.next
            cur.next = late
            late = cur
            cur = cur_next
            i+=1
        head.next=late
        fin1.next=cur_next
        return dummy.next




