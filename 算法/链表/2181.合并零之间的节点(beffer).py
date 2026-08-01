"""
    @Author:th
    @Time:2026/6/28
    @Desc:
"""
from typing import Optional
class ListNode(object):
    def __init__(self):
        self.val = 0
        self.next = None
class Solution:
    def mergeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        l1=head
        l2=head.next
        while l2.next:
            if l2.val:
                l1.val += l2.val
            else:
                l1=l2.next
            l2=l2.next
        return l1



