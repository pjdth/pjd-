"""
    @Author:th
    @Time:2026/6/27
    @Desc:
"""
from typing import Optional
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def getDecimalValue(self, head: Optional[ListNode]) -> int:
        sum1=0
        while head:
            sum1=sum1*2+head.val
            head=head.next
        return sum1