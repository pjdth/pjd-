import time
from abc import ABC, abstractmethod

from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger
from atguigu.tool.task_utils import add_running_task, add_done_task, add_node_duration
class NodeBase(ABC):
    name: str = "NodeBase"
    def __init__(self):
        if self.name == "NodeBase":
            raise ValueError(f'{self.__class__.__name__}请输入name属性')
    def __call__(self,state:ImportGraphState):
        # 从 state 里取 task_id（web 上传时传入；命令行直接跑 main_graph 时为空）
        task_id = state.get("task_id", "")
        start_time = time.time()
        try:
            logger.info(f'{self.name}开始执行')
            # 有 task_id 才上报进度，避免命令行运行时污染内存态任务表
            if task_id:
                add_running_task(task_id, self.name)
            res = self.process(state)
            logger.info(f'{self.name}执行完毕')
            if task_id:
                add_done_task(task_id, self.name)
                add_node_duration(task_id, self.name, time.time() - start_time)
            return res
        except Exception as e:
            logger.error(f'{self.name}执行失败，错误信息为：{e}')
            raise e
    @abstractmethod
    def process(self,state:ImportGraphState):
        pass
