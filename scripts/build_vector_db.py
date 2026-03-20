"""Build or refresh persistent SQLite embedding index for GenieBot RAG."""

import argparse
from pathlib import Path

from rag.system import RAGSystem


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GenieBot SQLite embedding DB")
    parser.add_argument("--data-dir", default="data", help="Directory containing .txt/.md docs")
    parser.add_argument("--db-path", default="data/rag_embeddings.db", help="SQLite DB file path")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model")
    parser.add_argument("--chunk-size", type=int, default=300, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    args = parser.parse_args()

    rag = RAGSystem(
        model_name=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        db_path=args.db_path,
    )
    rag.load_documents(args.data_dir)

    stats = rag.get_stats()
    print("SQLite embedding index ready")
    print(f"Chunks: {stats.get('total_chunks', 0)}")
    print(f"DB: {stats.get('db_path')}")


if __name__ == "__main__":
    main()
