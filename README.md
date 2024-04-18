# NHS Research RAG Demo

## Getting Started

Create and activate a Python environment

```pip install -r requirements```

Place all of the data, preferably in MD files, into a directory named 'data' and run:

```chainlit run app.py```

A vector store will be created using the data in the data directory. This can take some time depending on the amount of data. When subsequently running this, the previously created vector store will be used.

IMPORTANT: Requires an OpenAI API Key

```export OPENAI_API_KEY="sk... ```
