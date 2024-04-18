from llama_index.response.schema import Response, StreamingResponse
from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.callbacks.base import CallbackManager
from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from langchain.chat_models import ChatOpenAI
import chainlit as cl

STREAMING = False

# from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
# documents = SimpleDirectoryReader("./data").load_data()
# index = GPTVectorStoreIndex.from_documents(documents)
# index.storage_context.persist(persist_dir="vector_store")

import os
if os.path.isdir('vector_store'):
    try:
        print("Loading VectorStore")
        storage_context = StorageContext.from_defaults(persist_dir="vector_store")
        index = load_index_from_storage(storage_context)
    except:
        print("Error loading VectorStore")
else:
    print("Vectorstore doesn't exists. Creating one.")
    from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
    documents = SimpleDirectoryReader("./data").load_data()
    index = GPTVectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir="vector_store")
    pass

# try:
#     # rebuild storage context
#     storage_context = StorageContext.from_defaults(persist_dir="vector_store")
#     # load index
#     index = load_index_from_storage(storage_context)
# except:
#     # from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
#     # documents = SimpleDirectoryReader("./nice_data").load_data()
#     # index = GPTVectorStoreIndex.from_documents(documents)
#     # index.storage_context.persist()
#     pass


@cl.on_chat_start
async def factory():
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
            temperature=0,
            model_name="gpt-4",
            streaming=STREAMING
        ),
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        chunk_size=512,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
    )

    query_engine = index.as_query_engine(
        service_context=service_context,
        streaming=STREAMING,
    )

    cl.user_session.set("query_engine", query_engine)


@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine")  # type: RetrieverQueryEngine
    response = await cl.make_async(query_engine.query)(message)

    response_message = cl.Message(content="")
    await response_message.send()

    if isinstance(response, Response):
        response_message.content = str(response)
        await response_message.update()
    elif isinstance(response, StreamingResponse):
        gen = response.response_gen
        for token in gen:
            await response_message.stream_token(token=token)

        if response.response_txt:
            response_message = response.response_txt

        await response_message.update()