from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

from app.core.config import settings as config


class VectorStoreService:
    def  __init__(self, embedding):
        self.vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=config.PERSIST_DIRECTORY,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": config.SIMILARITY_SEARCH_K})


if __name__ == "__main__":
    retriever = VectorStoreService(
        embedding=DashScopeEmbeddings(dashscope_api_key=config.dashscope_api_key,
                                      model=config.embedding_model_name)
    ).get_retriever()
    print(retriever.invoke("我的身高150cm，该穿多大尺码"))
    print(len(retriever.invoke("我的身高150cm，该穿多大尺码")))
