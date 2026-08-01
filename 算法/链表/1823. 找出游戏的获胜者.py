# 1823.找出游戏的获胜者

# 共有名小伙伴一起做游戏。小伙伴们围成一圈，按顺时针顺序从到编号。确切地说，从第名
# 小伙伴顺时针移动一位会到达第（i+1）名小伙伴的位置，其中1<i＜，从第名小伙伴顺时针移
# 动一位会回到第名小伙伴的位置。
# 游戏遵循如下规则：
# 1.从第名小伙伴所在位置开始。
# 2.沿着顺时针方向数名小伙伴，计数时需要包含起始时的那位小伙伴。逐个绕圈进行计数，一些小
# 伙伴可能会被数过不止一次。
# 3.你数到的最后一名小伙伴需要离开圈子，并视作输掉游戏。
# 4.如果圈子中仍然有不止一名小伙伴，从刚刚输掉的小伙伴的顺时针下一位小伙伴开始，回到步骤②
# 继续执行。
# 5.否则，圈子中最后一名小伙伴赢得游戏。
# 给你参与游戏的小伙伴总数，和一个整数，返回游戏的获胜者。

# 输入:n=5，k =2
# 输出：3
# 解释：游戏运行步骤如下：
# 1）从小伙伴1开始。
# 2）顺时针数2名小伙伴，也就是小伙伴1和2。
# 3）小伙伴2离开圈子。下一次从小伙伴3开始。
# 4）顺时针数2名小伙伴，也就是小伙伴3和4。
# 5）小伙伴4离开圈子。下一次从小伙伴5开始。
# 6）顺时针数2名小伙伴，也就是小伙伴5和1。
# 7）小伙伴1离开圈子。下一次从小伙伴3开始。
# 8）顺时针数2名小伙伴，也就是小伙伴3和5。
# 9）小伙伴5离开圈子。只剩下小伙伴3。所以小伙伴3是游戏的获胜者。
class ListNode(object):
    def __init__(self,val,next=None):
        self.val = val
        self.next = next
class Solution:
    def findTheWinner(self, n: int, k: int) -> int:
        head = ListNode(1)
        dummy=ListNode(-1,head)
        for i in range(2,n+1):
            head.next = ListNode(i)
            head = head.next
        head.next=dummy.next
        head = head.next

        while head.next!=head:
            for _ in range(k-1):
                head = head.next
            head.val=head.next.val
            head.next=head.next.next
        return head.val
