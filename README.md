# Knowledge-to-Chatbot
# Retrieval Augmented Generation (RAG) Chatbot with LlamaEdge and Qdrant

## Overview

This project implements a **Retrieval-Augmented Generation (RAG) chatbot** using a local Large Language Model (LLM). The system enhances responses by retrieving relevant information from a **vector database** before generating answers.

The project uses:

* **Llama models** for natural language generation
* **Qdrant** as the vector database
* **WasmEdge / LlamaEdge** for lightweight inference
* **Embedding models** for semantic search
* **Chemistry knowledge dataset** as the external knowledge base

This architecture allows the chatbot to answer **domain-specific questions** using retrieved context rather than relying only on the base language model.

---

## Architecture

User Question
↓
Embedding Generation
↓
Vector Search (Qdrant)
↓
Relevant Knowledge Retrieved
↓
Prompt Augmentation
↓
LLM Generates Response

This process improves accuracy by providing the model with **relevant context during inference**.

---

## Technologies Used

* **LlamaEdge**
* **WasmEdge Runtime**
* **Qdrant Vector Database**
* **Llama 3 / TinyLlama Models**
* **Nomic Embedding Model**
* **Docker**
* **Python**

---

## Project Structure

```
rag_llama_project
│
├── chemistry.txt
├── chemistry-by-chapter.txt
├── vectors_from_paragraph_chemistry.py
├── csv_embed.wasm
├── paragraph_embed.wasm
├── rag-api-server.wasm
├── llama-api-server.wasm
├── collection_status.txt
├── chemistry_snapshot.zip
├── README.md
└── .gitignore
```

### File Description

| File                                | Description                                |
| ----------------------------------- | ------------------------------------------ |
| chemistry.txt                       | Chemistry knowledge dataset                |
| chemistry-by-chapter.txt            | Textbook content divided by chapters       |
| vectors_from_paragraph_chemistry.py | Script to generate QA pairs for embeddings |
| csv_embed.wasm                      | Creates embeddings from QA dataset         |
| paragraph_embed.wasm                | Generates embeddings from text chunks      |
| rag-api-server.wasm                 | RAG API server for LLM inference           |
| llama-api-server.wasm               | LLM API server                             |
| collection_status.txt               | Vector collection status output            |
| chemistry_snapshot.zip              | Snapshot of Qdrant vector database         |

---

## Setup Instructions

### 1 Install Dependencies

Install Docker, WasmEdge and required tools.

```
docker pull qdrant/qdrant
```

Install WasmEdge:

```
curl -sSf https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install_v2.sh | bash
source $HOME/.wasmedge/env
```

---

### 2 Start Qdrant Vector Database

```
docker run -p 6333:6333 -p 6334:6334 \
-v $(pwd)/qdrant_storage:/qdrant/storage:z \
-v $(pwd)/qdrant_snapshots:/qdrant/snapshots:z \
qdrant/qdrant
```

---

### 3 Create Vector Collection

```
curl -X PUT 'http://localhost:6333/collections/chemistry' \
-H 'Content-Type: application/json' \
--data-raw '{
  "vectors": {
    "size": 768,
    "distance": "Cosine",
    "on_disk": true
  }
}'
```

---

### 4 Generate Embeddings

```
wasmedge --dir .:. \
--nn-preload embedding:GGML:AUTO:nomic-embed-text-v1.5.f16.gguf \
csv_embed.wasm embedding chemistry 768 chemistry-by-chapter.csv --ctx_size 8192
```

---

### 5 Start the RAG API Server

```
wasmedge --dir .:. \
--nn-preload default:GGML:AUTO:Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf \
--nn-preload embedding:GGML:AUTO:nomic-embed-text-v1.5.f16.gguf \
rag-api-server.wasm \
--prompt-template llama-3-chat,embedding \
--model-name llama31,nomic-embed \
--ctx-size 16384,8192 \
--batch-size 128,8192 \
--rag-policy system-message \
--qdrant-url http://127.0.0.1:6333 \
--qdrant-collection-name chemistry \
--socket-addr 0.0.0.0:8080
```

---

## Testing the API

Example query:

```
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"messages":[{"role":"user","content":"What is Mercury?"}]}'
```

---

## Example Output

The system retrieves relevant chemistry knowledge from the vector database and generates an answer using the LLM.

Example question:

What is Mercury?

Example answer:

Mercury is a chemical element with atomic number 80. It is a liquid metal at room temperature and has unique physical properties.

---

## Features

* Local LLM inference
* Retrieval Augmented Generation
* Vector search using Qdrant
* Domain knowledge integration
* OpenAI compatible API server
* Web-based chatbot support

---

## Future Improvements

* Add web chatbot UI
* Expand knowledge base
* Improve prompt engineering
* Add support for larger context models

---

Sri Harsha

