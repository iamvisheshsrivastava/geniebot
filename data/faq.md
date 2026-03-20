# Frequently Asked Questions

## What is GenieBot?
GenieBot is an AI-powered assistant that combines Retrieval-Augmented Generation (RAG) with vision capabilities. It can answer questions based on your documents and analyze images.

## How do I ask questions?
Use the `/ask` command followed by your question. For example: `/ask What is the return policy?`

## Can GenieBot understand images?
Yes! Use the `/image` command and upload an image. GenieBot will generate a caption and extract relevant tags.

## What documents can I upload?
GenieBot supports text-based documents including FAQs, policies, documentation, and knowledge bases.

## How long does it take to get a response?
Typically, you'll get a response within a few seconds. The first query may take slightly longer as the models initialize.

## Is my data secure?
All processing happens locally. Your documents and queries are not sent to external servers.

## What models does GenieBot use?
- LLM: Ollama with Llama2 or Mistral
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Vision: Salesforce BLIP for image captioning

## How many past conversations are remembered?
GenieBot maintains the last 3 interactions per user for context.
