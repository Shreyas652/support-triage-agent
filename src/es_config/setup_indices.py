"""
Elasticsearch Setup - Create indices and load data
"""

import os
import json
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Index mappings
TICKET_MAPPING = {
    "properties": {
        "ticket_id": {"type": "keyword"},
        "subject": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "description": {
            "type": "text",
            "fields": {"keyword": {"type": "keyword"}}
        },
        "customer_id": {"type": "keyword"},
        "customer_email": {"type": "keyword"},
        "customer_plan": {"type": "keyword"},
        "status": {"type": "keyword"},
        "category": {"type": "keyword"},
        "priority": {"type": "keyword"},
        "assigned_team": {"type": "keyword"},
        "assigned_to": {"type": "keyword"},
        "sentiment": {"type": "keyword"},
        "urgency_score": {"type": "integer"},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "resolved_at": {"type": "date"},
        "tags": {"type": "keyword"},
        "resolution_time_minutes": {"type": "integer"}
    }
}

CUSTOMER_MAPPING = {
    "properties": {
        "customer_id": {"type": "keyword"},
        "email": {"type": "keyword"},
        "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "plan": {"type": "keyword"},
        "signup_date": {"type": "date"},
        "total_tickets": {"type": "integer"},
        "satisfaction_score": {"type": "float"}
    }
}

KB_MAPPING = {
    "properties": {
        "article_id": {"type": "keyword"},
        "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "content": {"type": "text"},
        "category": {"type": "keyword"},
        "tags": {"type": "keyword"},
        "view_count": {"type": "integer"},
        "helpful_count": {"type": "integer"},
        "updated_at": {"type": "date"}
    }
}

AGENT_ACTION_MAPPING = {
    "properties": {
        "action_id": {"type": "keyword"},
        "ticket_id": {"type": "keyword"},
        "agent_name": {"type": "keyword"},
        "action_type": {"type": "keyword"},
        "details": {"type": "object", "enabled": True},
        "confidence_score": {"type": "float"},
        "timestamp": {"type": "date"}
    }
}


def get_es_client():
    """Get Elasticsearch client"""
    # Try URL method first (more reliable)
    if os.getenv('ELASTICSEARCH_URL'):
        # For Elastic Cloud with API key
        if os.getenv('ELASTIC_API_KEY'):
            return Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                api_key=os.getenv('ELASTIC_API_KEY'),
                verify_certs=True
            )
        # For basic auth
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
    """Create index with mapping"""
    if es.indices.exists(index=index_name):
        print(f"⚠️  Index '{index_name}' already exists, deleting...")
        es.indices.delete(index=index_name)
    
    es.indices.create(
        index=index_name,
        body={"mappings": mapping}
    )
    print(f"✅ Created index: {index_name}")


def bulk_index_data(es: Elasticsearch, index_name: str, data: List[Dict], id_field: str):
    """Bulk index documents"""
    actions = [
        {
            "_index": index_name,
            "_id": doc[id_field],
            "_source": doc
        }
        for doc in data
    ]
    
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    print(f"✅ Indexed {success} documents into {index_name}")
    if failed:
        print(f"⚠️  Failed to index {len(failed)} documents")
    
    return success


def load_data_from_file(filepath: str) -> List[Dict]:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def setup_elasticsearch():
    """Main setup function"""
    print("🚀 Setting up Elasticsearch for Support Triage Agent\n")
    
    # Connect to Elasticsearch
    print("📡 Connecting to Elasticsearch...")
    es = get_es_client()
    
    if es.ping():
        info = es.info()
        print(f"✅ Connected to Elasticsearch")
        print(f"   Cluster: {info['cluster_name']}")
        print(f"   Version: {info['version']['number']}\n")
    else:
        raise ConnectionError("Failed to connect to Elasticsearch")
    
    # Create indices
    print("📋 Creating indices...")
    create_index(es, "support_tickets", TICKET_MAPPING)
    create_index(es, "customers", CUSTOMER_MAPPING)
    create_index(es, "knowledge_base", KB_MAPPING)
    create_index(es, "agent_actions", AGENT_ACTION_MAPPING)
    print()
    
    # Load and index data
    print("📊 Loading data...")
    data_dir = "data"
    
    # Index customers
    customers = load_data_from_file(f"{data_dir}/customers.json")
    bulk_index_data(es, "customers", customers, "customer_id")
    
    # Index tickets
    tickets = load_data_from_file(f"{data_dir}/tickets.json")
    bulk_index_data(es, "support_tickets", tickets, "ticket_id")
    
    # Index KB articles
    kb_articles = load_data_from_file(f"{data_dir}/kb_articles.json")
    bulk_index_data(es, "knowledge_base", kb_articles, "article_id")
    
    print()
    
    # Refresh indices
    print("🔄 Refreshing indices...")
    es.indices.refresh(index="support_tickets,customers,knowledge_base,agent_actions")
    
    # Verify data
    print("\n✅ Setup complete! Index statistics:")
    for index in ["support_tickets", "customers", "knowledge_base", "agent_actions"]:
        count = es.count(index=index)["count"]
        print(f"   - {index}: {count} documents")
    
    print("\n🎯 Elasticsearch is ready for the Triage Agent!")
    return es


if __name__ == "__main__":
    setup_elasticsearch()
