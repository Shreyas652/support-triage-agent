import os
import json
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

TICKET_MAPPING = {
: {
: {"type": "keyword"},
: {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
: {
: "text",
: {"keyword": {"type": "keyword"}}
        },
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "integer"},
: {"type": "date"},
: {"type": "date"},
: {"type": "date"},
: {"type": "keyword"},
: {"type": "integer"}
    }
}

CUSTOMER_MAPPING = {
: {
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
: {"type": "keyword"},
: {"type": "date"},
: {"type": "integer"},
: {"type": "float"}
    }
}

KB_MAPPING = {
: {
: {"type": "keyword"},
: {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
: {"type": "text"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "integer"},
: {"type": "integer"},
: {"type": "date"}
    }
}

AGENT_ACTION_MAPPING = {
: {
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "keyword"},
: {"type": "object", "enabled": True},
: {"type": "float"},
: {"type": "date"}
    }
}

def get_es_client():
    
    if os.getenv('ELASTICSEARCH_URL'):
                                        
        if os.getenv('ELASTIC_API_KEY'):
            return Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                api_key=os.getenv('ELASTIC_API_KEY'),
                verify_certs=True
            )
                        
        else:
            return Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                basic_auth=(
                    os.getenv('ELASTIC_USERNAME', 'elastic'),
                    os.getenv('ELASTIC_PASSWORD')
                ),
                verify_certs=True
            )
    elif os.getenv('ELASTIC_CLOUD_ID') and os.getenv('ELASTIC_API_KEY'):
        return Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            api_key=os.getenv('ELASTIC_API_KEY')
        )
    else:
        raise ValueError("Missing Elasticsearch configuration")

def create_index(es: Elasticsearch, index_name: str, mapping: Dict):
    
    if es.indices.exists(index=index_name):
        print(f"⚠️  Index '{index_name}' already exists, deleting...")
        es.indices.delete(index=index_name)
    
    es.indices.create(
        index=index_name,
        body={"mappings": mapping}
    )
    print(f"✅ Created index: {index_name}")

def bulk_index_data(es: Elasticsearch, index_name: str, data: List[Dict], id_field: str):
    
    actions = [
        {
: index_name,
: doc[id_field],
: doc
        }
        for doc in data
    ]
    
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    print(f"✅ Indexed {success} documents into {index_name}")
    if failed:
        print(f"⚠️  Failed to index {len(failed)} documents")
    
    return success

def load_data_from_file(filepath: str) -> List[Dict]:
    
    with open(filepath, 'r') as f:
        return json.load(f)

def setup_elasticsearch():
    
    print("🚀 Setting up Elasticsearch for Support Triage Agent\n")
    
    print("📡 Connecting to Elasticsearch...")
    es = get_es_client()
    
    if es.ping():
        info = es.info()
        print(f"✅ Connected to Elasticsearch")
        print(f"   Cluster: {info['cluster_name']}")
        print(f"   Version: {info['version']['number']}\n")
    else:
        raise ConnectionError("Failed to connect to Elasticsearch")
    
    print("📋 Creating indices...")
    create_index(es, "support_tickets", TICKET_MAPPING)
    create_index(es, "customers", CUSTOMER_MAPPING)
    create_index(es, "knowledge_base", KB_MAPPING)
    create_index(es, "agent_actions", AGENT_ACTION_MAPPING)
    print()
    
    print("📊 Loading data...")
    data_dir = "data"
    
    customers = load_data_from_file(f"{data_dir}/customers.json")
    bulk_index_data(es, "customers", customers, "customer_id")
    
    tickets = load_data_from_file(f"{data_dir}/tickets.json")
    bulk_index_data(es, "support_tickets", tickets, "ticket_id")
    
    kb_articles = load_data_from_file(f"{data_dir}/kb_articles.json")
    bulk_index_data(es, "knowledge_base", kb_articles, "article_id")
    
    print()
    
    print("🔄 Refreshing indices...")
    es.indices.refresh(index="support_tickets,customers,knowledge_base,agent_actions")
    
    print("\n✅ Setup complete! Index statistics:")
    for index in ["support_tickets", "customers", "knowledge_base", "agent_actions"]:
        count = es.count(index=index)["count"]
        print(f"   - {index}: {count} documents")
    
    print("\n🎯 Elasticsearch is ready for the Triage Agent!")
    return es

if __name__ == "__main__":
    setup_elasticsearch()
