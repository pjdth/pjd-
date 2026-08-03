from langgraph.constants import END,START
from langgraph.graph import StateGraph

from atguigu.import_process.state import ImportGraphState
from atguigu.nodes.node_bge_embedding import NodeBGEEmbedding
from atguigu.nodes.node_document_split import NodeDocumentSplit
from atguigu.nodes.node_entry import NodeEntry
from atguigu.nodes.node_import_milvus import NodeImportMilvus
from atguigu.nodes.node_item_name_recognition import NodeItemNameRecognition
from atguigu.nodes.node_md_img import NodeMDImg
from atguigu.nodes.node_pdf_to_md import NodePDFToMD
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger


class ImportMainGraphRunner:
    def __init__(self):
        self.builder=StateGraph(state_schema=ImportGraphState)
        self.add_node()
        self.add_edge()
    def add_node(self):

        self.builder.add_node(NodeEntry.name, NodeEntry())
        self.builder.add_node(NodeMDImg.name,NodeMDImg())
        self.builder.add_node(NodePDFToMD.name,NodePDFToMD())
        self.builder.add_node(NodeDocumentSplit.name,NodeDocumentSplit())
        self.builder.add_node(NodeItemNameRecognition.name,NodeItemNameRecognition())
        self.builder.add_node(NodeBGEEmbedding.name,NodeBGEEmbedding())
        self.builder.add_node(NodeImportMilvus.name,NodeImportMilvus())

    def after_entry_router(self,state: ImportGraphState):
        md_bool=state.get("is_md_read_enabled",False)
        pdf_bool=state.get("is_pdf_read_enabled",False)
        if md_bool:
            return NodeMDImg.name
        elif pdf_bool:
            return NodePDFToMD.name
        else:
            return END

    def add_edge(self):
        self.builder.set_entry_point(NodeEntry.name)
        self.builder.add_conditional_edges(NodeEntry.name, self.after_entry_router)
        self.builder.add_edge(NodePDFToMD.name, NodeMDImg.name)
        self.builder.add_edge(NodeMDImg.name, NodeDocumentSplit.name)
        self.builder.add_edge(NodeDocumentSplit.name, NodeItemNameRecognition.name)
        self.builder.add_edge(NodeItemNameRecognition.name, NodeBGEEmbedding.name)
        self.builder.add_edge(NodeBGEEmbedding.name, NodeImportMilvus.name)
        self.builder.add_edge(NodeImportMilvus.name,END)

    def garph_invoke(self,state:ImportGraphState):
        graph=self.builder.compile()
        return graph.invoke(state)

    @classmethod
    def create_run(cls,state:ImportGraphState):
        return cls().garph_invoke(state)

if __name__ == '__main__':
    runer=ImportMainGraphRunner()
    state={
        "local_file_path":r"D:\code\uv1\data\hak180产品安全手册.pdf"
    }
    logger.info((json_tool(runer.create_run(state))))


