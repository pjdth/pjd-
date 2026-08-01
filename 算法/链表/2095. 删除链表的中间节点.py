# 2095. 删除链表的中间节点
# 给你一个链表的头节点head。删除链表的中间节点，并返回修改后的链表的头节点head。
# 长度为链表的中间节点是从头数起第[n／2】个节点（下标从0开始），其中[x」表示小于或等于
# 的最大整数。
# ●对于=、2、3、4和5的情况，中间节点的下标分别是◎、、、②和②。
# 示例 1:
#
# 输入:head=[1,3,4,7,1,2,6]
# 输出：[1,3,4,1,2,6]
# 解释：
# 上图表示给出的链表。节点的下标分别标注在每个节点的下方。
# 由于n=7，值为7的节点3是中间节点，用红色标注。
# 返回结果为移除节点后的新链表。
from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head.next is None:
            return None
        left = head
        right = head
        while right and right.next:
            left = left.next
            right = right.next.next
        if left.next is None:
            head.next = None
            return head
        left.val=left.next.val
        left.next=left.next.next
        return head



