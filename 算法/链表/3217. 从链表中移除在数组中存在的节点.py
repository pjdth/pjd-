from typing import List, Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def modifiedList(self, nums: List[int], head: Optional[ListNode]) -> Optional[ListNode]:
        hax={}
        for n in nums:
            hax[n]=1
        cur=cur1=ListNode(next=head)
        while cur.next:
            if cur.next.val in hax:
                cur.next=cur.next.next
            else:
                cur=cur.next
        return cur1.next