# 19.删除链表的倒数第N个结点
#
# 给你一个链表，删除链表的倒数第个结点，并且返回链表的头结点。
# 示例 1:
# 输入:head=[1,2,3,4,5]，n = 2
# 输出：[1,2,3,5]
# 示例 2:
# 输入：head=[1]，n=1
# 输出：[]
from typing import Optional
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(next=head)
        cur=dummy
        last = dummy
        for _ in range(n):
            cur=cur.next
        while cur.next:
            cur = cur.next
            last=last.next
        last.next = last.next.next
        return dummy.next