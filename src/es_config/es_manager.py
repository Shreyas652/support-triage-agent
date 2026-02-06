"""
Elasticsearch Integration
Handle Elasticsearch connections, indices, and operations
"""

from elasticsearch import Elasticsearch
from typing import Dict, Any, List

class ElasticsearchManager:
    """
    Manages Elasticsearch operations and indices
    """
    
    def __init__(self, client: Elasticsearch):
        """
        Initialize the Elasticsearch manager
        
        Args:
            client: Elasticsearch client instance
        """
        self.es = client
        
    def create_index(self, index_name: str, mappings: Dict[str, Any] = None) -> bool:
        """
        Create an Elasticsearch index
        
        Args:
            index_name: Name of the index to create
            mappings: Optional index mappings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.es.indices.exists(index=index_name):
                print(f"ℹ️  Index '{index_name}' already exists")
                return True
                
            body = {}
            if mappings:
                body["mappings"] = mappings
                
            self.es.indices.create(index=index_name, body=body)
            print(f"✅ Created index: {index_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating index '{index_name}': {e}")
            return False
            
    def index_document(self, index_name: str, document: Dict[str, Any], doc_id: str = None) -> bool:
        """
        Index a document in Elasticsearch
        
        Args:
            index_name: Name of the index
            document: Document to index
            doc_id: Optional document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if doc_id:
                self.es.index(index=index_name, id=doc_id, body=document)
            else:
                self.es.index(index=index_name, body=document)
            return True
        except Exception as e:
            print(f"❌ Error indexing document: {e}")
            return False
            
    def bulk_index(self, index_name: str, documents: List[Dict[str, Any]]) -> int:
        """
        Bulk index multiple documents
        
        Args:
            index_name: Name of the index
            documents: List of documents to index
            
        Returns:
            Number of successfully indexed documents
        """
        from elasticsearch.helpers import bulk
        
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in documents
        ]
        
        try:
            success, failed = bulk(self.es, actions)
            print(f"✅ Indexed {success} documents")
            if failed:
                print(f"⚠️  Failed to index {len(failed)} documents")
            return success
        except Exception as e:
            print(f"❌ Bulk indexing error: {e}")
            return 0
            
    def search(self, index_name: str, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents
        
        Args:
            index_name: Name of the index to search
            query: Elasticsearch query
            size: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            response = self.es.search(
                index=index_name,
                body={"query": query, "size": size}
            )
            return [hit['_source'] for hit in response['hits']['hits']]
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
            
    def delete_index(self, index_name: str) -> bool:
        """
        Delete an index
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.es.indices.exists(index=index_name):
                self.es.indices.delete(index=index_name)
                print(f"✅ Deleted index: {index_name}")
                return True
            else:
                print(f"ℹ️  Index '{index_name}' does not exist")
                return False
        except Exception as e:
            print(f"❌ Error deleting index: {e}")
            return False

# Example index mappings
EXAMPLE_MAPPINGS = {
    "tasks": {
        "properties": {
            "task_id": {"type": "keyword"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "status": {"type": "keyword"},
            "priority": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "tags": {"type": "keyword"}
        }
    },
    "logs": {
        "properties": {
            "timestamp": {"type": "date"},
            "level": {"type": "keyword"},
            "message": {"type": "text"},
            "source": {"type": "keyword"},
            "metadata": {"type": "object"}
        }
    }
}
