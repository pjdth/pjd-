"""
    @Author:th
    @Time:2026/7/28
    @Desc:
"""
from typing import Optional

# 21. 合并两个有序链表
# 将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。
# 示例 1:
# 输入：11 =[1,2,4]，12 =[1,3,4]
# 输出：[1,1,2,3,4,4]
# 示例 2:
# 输入:11=[]，12=[]
# 输出：[]
# 示例3:
# 输入：11=[]，12 =[0]
# 输出：[0]
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy =ListNode(val=-1,next= None)
        cur=dummy
        while list1 and list2:
            if list1.val < list2.val:
                cur.next = ListNode()
                cur.next.val = list1.val
                list1 = list1.next
                cur = cur.next
            else:
                cur.next = ListNode()
                cur.next.val = list2.val
                list2 = list2.next
                cur = cur.next
        if list1:
            cur.next = list1
        if list2:
            cur.next = list2
        return dummy.next