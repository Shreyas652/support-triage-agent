"""
Initialize Elasticsearch indices for the project
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from es_manager import ElasticsearchManager, EXAMPLE_MAPPINGS

load_dotenv()

def main():
    """Initialize all required Elasticsearch indices"""
    print("🔧 Initializing Elasticsearch indices...")
    
    # Connect to Elasticsearch
    if os.getenv('ELASTIC_CLOUD_ID') and os.getenv('ELASTIC_API_KEY'):
        es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            api_key=os.getenv('ELASTIC_API_KEY')
        )
    elif os.getenv('ELASTICSEARCH_URL'):
        es = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
            basic_auth=(
                os.getenv('ELASTIC_USERNAME', 'elastic'),
                os.getenv('ELASTIC_PASSWORD')
            )
        )
    else:
        raise ValueError("Missing Elasticsearch configuration")
    
    # Initialize manager
    manager = ElasticsearchManager(es)
    
    # Create indices
    print("\n📋 Creating indices...")
    for index_name, mappings in EXAMPLE_MAPPINGS.items():
        manager.create_index(index_name, mappings)
    
    print("\n✅ Elasticsearch initialization complete!")
    print("\nCreated indices:")
    for index_name in EXAMPLE_MAPPINGS.keys():
        print(f"  - {index_name}")

if __name__ == "__main__":
    main()
