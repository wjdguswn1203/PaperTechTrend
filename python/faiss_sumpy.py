import os
from llama_index import SimpleDirectoryReader, ServiceContext, StorageContext, LangchainEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from langchain.embeddings import HuggingFaceEmbeddings
import faiss
from transformers import pipeline

# 문서 데이터 로드
documents = SimpleDirectoryReader('data').load_data()
print('Documents loaded successfully')

# 요약 모델 초기화
summarization_pipe = pipeline("summarization", model="Falconsai/text_summarization")
print('Summarization model initialized successfully')

# 임베딩 모델 초기화
embed_model = LangchainEmbedding(HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
))
print('Embedding model initialized successfully')

# Faiss 벡터 스토어 초기화
faiss_index = faiss.IndexFlatL2(384)
vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
service_context = ServiceContext.from_defaults(embed_model=embed_model)
print("Faiss Index and Vector Store initialized successfully")

# 요약 후 벡터화 및 Faiss 인덱스에 추가
for doc in documents:
    # 문서 내용 요약
    summary = summarization_pipe(doc.content, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    print(f"Original Text: {doc.content[:200]}...")  # 처음 200자만 출력
    print(f"Summary: {summary}\n")

    # 요약된 내용을 벡터로 변환
    vector = embed_model.embed(summary)  # 요약된 텍스트를 벡터로 변환
    faiss_index.add(vector)  # 벡터를 Faiss 인덱스에 추가

print('Summarized vectors added to Faiss Index successfully')
