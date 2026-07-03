import os
import dotenv
import hashlib
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

dotenv.load_dotenv()

llm = embedding_model = NVIDIAEmbeddings(model="nvidia/nv-embed-v1")

pc = Pinecone()
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))


def store(namespace: str):
    return PineconeVectorStore(
        index=index,
        embedding=embedding_model,
        namespace=namespace,
        text_key="text",
    )


def chunking(pdf, chunk_size):
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=300
        )
        loader = PyPDFLoader(pdf)
        doc =loader.load()
        texts = splitter.split_documents(doc)
        docs = [
            Document(
                page_content=i.page_content,
                metadata={"source": i.metadata["source"], "page": i.metadata["page"]},
            )
            for i in texts
        ]
        for doc in docs:
            doc_id = hashlib.md5(doc.page_content.encode()).hexdigest()
            doc.metadata["id"] = doc_id
        return docs
    except Exception as e:
        return "Error while chunking documents"


def upsert(namespace, pdf, chunk_size=1500):
    try:
        docs = chunking(pdf, chunk_size)
        vector_store = store(namespace)
        vector_store.add_documents(docs, ids=[d.metadata["id"] for d in docs])
        return "Successfully added documents to vector store"
    except Exception as e:
        return "Error while uploading vector to vector store"

async def retriever(query: str, namespace: str):
    try:
        vector_store = store(namespace)
        res =await vector_store.as_retriever(search_kwargs={"k": 5}).ainvoke(query)
        docs=[]
        for i in res:
            docs.append(i.page_content)
        return docs
    except Exception as e:
        return "Error while retrieving vectors from vector store"

