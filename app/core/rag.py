from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.core.vector_store import VectorStoreService
from app.core.config import settings as config
from app.core.history_store import get_history
from langchain_core.documents import Document


class RAG:
    def __init__(self):
        self.vector_store = VectorStoreService(
            embedding=DashScopeEmbeddings(dashscope_api_key=config.DASHSCOPE_API_KEY,
                                          model=config.EMBEDDING_MODEL_NAME),
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "以我提供的参考资料为依据，简介和专业地回答用户问题。参考资料：{context}。"),
            ("system", "并且我提供用户的对话历史记录。如下："),
            MessagesPlaceholder("history"),
            ("human", "请回答用户提问：{question}")
        ])
        self.chat_model = ChatTongyi(
            dashscope_api_key=config.DASHSCOPE_API_KEY,
            model=config.CHAT_MODEL_NAME
        )
        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_store.get_retriever()

        def format_for_retriever(value: dict) -> str:
            """包含历史记录的字典转字符串 value {'question‘: '', 'history': []}"""
            return value['question']

        def format_docs(docs: list[Document]) -> str:
            """检索器检索结果由文档列表转字符串"""
            if not docs:
                return "没有参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def format_for_prompt_template(prompt: dict):
            """
            提示词提取
            {'question': {'question':'', 'history': []}, 'context': ''} ->
            {'question':'', 'history': [], 'context': ''}
            """
            new_prompt = {
                "question": prompt['question']['question'],
                "history": prompt['question']['history'],
                "context": prompt['context']
            }
            return new_prompt

        def print_prompt(prompt):
            print("="*20, prompt, "="*20)
            return prompt

        chain = (
            {
                "question": RunnablePassthrough(),
                "context":  RunnableLambda(format_for_retriever) | retriever | format_docs
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            history_messages_key="history",
            input_messages_key="question"
        )

        return conversation_chain


if __name__ == "__main__":
    # session_id
    session_config = {
        "configurable": {
            "session_id": "user_001"
        }
    }
    rag = RAG()
    # print(rag.chain.invoke({"question": "我的身高160cm，该穿多大尺码"}, session_config))
    print(rag.chain.invoke({"question": "春天适合穿什么颜色的衣服"}, session_config))
