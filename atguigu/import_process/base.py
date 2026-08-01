from abc import ABC, abstractmethod

from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger
class NodeBase(ABC):
    name: str = "NodeBase"
    def __init__(self):
        if self.name == "NodeBase":
            raise ValueError(f'{self.__class__.__name__}请输入name属性')
    def __cal__(self,state:ImportGraphState):
        try:
            logger.info(f'{self.name}开始执行')
            res=self.process(state)
            logger.info(f'{self.name}执行完毕')
            return res
        except Exception as e:
            logger.error(f'{self.name}执行失败，错误信息为：{e}')
            raise e
    @abstractmethod
    def process(self,state:ImportGraphState):
        pass
