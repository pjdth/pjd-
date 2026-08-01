# 61.旋转链表
from typing import Optional


# 给你一个链表的头节点head，旋转链表，将链表每个节点向右移动个位置。
# 示例 1:
# 输入:head=[1,2,3,4,5]，k= 2
# 输出：[4,5,1,2,3]
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or not head.next or k == 0:
            return head
        dummy = ListNode(-1, head)
        i = 1
        tail = head
        while tail.next:
            tail = tail.next
            i += 1

        k = k % i
        tail.next = dummy.next

        for _ in range(i-k):
            tail = tail.next

        first1 = tail.next
        tail.next = None
        dummy.next = first1
        return dummy.next
