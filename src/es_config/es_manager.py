from elasticsearch import Elasticsearch
from typing import Dict, Any, List

class ElasticsearchManager:
    
    def __init__(self, client: Elasticsearch):
        
        self.es = client
        
    def create_index(self, index_name: str, mappings: Dict[str, Any] = None) -> bool:
        
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
        
        from elasticsearch.helpers import bulk
        
        actions = [
            {
: index_name,
: doc
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

EXAMPLE_MAPPINGS = {
: {
: {
: {"type": "keyword"},
: {"type": "text"},
: {"type": "text"},
: {"type": "keyword"},
: {"type": "integer"},
: {"type": "date"},
: {"type": "date"},
: {"type": "keyword"}
        }
    },
: {
: {
: {"type": "date"},
: {"type": "keyword"},
: {"type": "text"},
: {"type": "keyword"},
: {"type": "object"}
        }
    }
}
