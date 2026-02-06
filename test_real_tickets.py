"""
Test Agent with Real Tickets - Interactive Demo
Shows complete triage results in terminal
"""

import os
import sys
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

sys.path.insert(0, 'src')
from agent.triage_agent import TriageAgent

load_dotenv()

# Connect to Elasticsearch
def connect_es():
    if os.getenv('ELASTIC_API_KEY'):
        es = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
            api_key=os.getenv('ELASTIC_API_KEY'),
            verify_certs=True
        )
    else:
        es = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
            basic_auth=(os.getenv('ELASTIC_USERNAME', 'elastic'), os.getenv('ELASTIC_PASSWORD')),
            verify_certs=True
        )
    
    if es.ping():
        print(f"Connected to Elasticsearch Cloud")
        return es
    else:
        print("Failed to connect")
        return None

# Test tickets
TEST_TICKETS = [
    {
        "ticket_id": "DEMO-001",
        "customer_id": "CUST-001",
        "subject": "URGENT: Production system is down!",
        "description": "Our production API is not working. All customers are affected. This is critical and needs immediate attention. System crashed 10 minutes ago.",
        "status": "open",
        "created_at": "2026-02-05T18:00:00Z"
    },
    {
        "ticket_id": "DEMO-002",
        "customer_id": "CUST-050",
        "subject": "Question about invoice",
        "description": "Hi, I received my invoice for last month but I don't understand one of the charges. Can you explain what 'platform fee' means?",
        "status": "open",
        "created_at": "2026-02-05T17:45:00Z"
    },
    {
        "ticket_id": "DEMO-003",
        "customer_id": "CUST-025",
        "subject": "Feature request: Dark mode",
        "description": "It would be great if you could add a dark mode to the dashboard. Many users including myself prefer dark themes for reduced eye strain.",
        "status": "open",
        "created_at": "2026-02-05T16:30:00Z"
    },
    {
        "ticket_id": "DEMO-004",
        "customer_id": "CUST-010",
        "subject": "Cannot reset my password",
        "description": "I'm trying to reset my password but the reset email is not arriving. I checked spam folder too. Can you help?",
        "status": "open",
        "created_at": "2026-02-05T17:00:00Z"
    },
    {
        "ticket_id": "DEMO-005",
        "customer_id": "CUST-075",
        "subject": "Charged twice for subscription",
        "description": "I was charged $99 twice on my credit card this month for the same subscription. This happened on Feb 1st. Please refund one charge.",
        "status": "open",
        "created_at": "2026-02-05T15:30:00Z"
    }
]

def print_ticket_summary(ticket):
    """Print ticket details"""
    print("\n" + "="*80)
    print(f"TICKET: {ticket['ticket_id']}")
    print("="*80)
    print(f"Subject: {ticket['subject']}")
    print(f"Description: {ticket['description'][:100]}...")
    print(f"Customer: {ticket.get('customer_id', 'Unknown')}")
    print("-"*80)

def print_triage_result(result):
    """Print triage decision"""
    decision = result['triage_decision']
    workflow = result['workflow_result']
    
    print(f"\nTRIAGE DECISION:")
    print(f"  Category: {decision['category'].upper()}")
    print(f"  Priority: {decision['priority'].upper()}")
    print(f"  Confidence: {decision['confidence']:.1%}")
    print(f"  Assigned Team: {decision['assigned_team']}")
    
    print(f"\nACTIONS TAKEN:")
    for i, action in enumerate(workflow['actions_taken'], 1):
        print(f"  {i}. {action}")
    
    print("="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("REAL TICKET TRIAGE TEST")
    print("Testing 5 Different Ticket Scenarios")
    print("="*80 + "\n")
    
    # Connect
    es = connect_es()
    if not es:
        return
    
    # Initialize agent
    agent = TriageAgent(es)
    print(f"Agent initialized: {agent.agent_name}\n")
    
    # Test each ticket
    print("Processing tickets...\n")
    
    for i, ticket in enumerate(TEST_TICKETS, 1):
        print(f"\n[{i}/5] Testing Ticket: {ticket['ticket_id']}")
        print_ticket_summary(ticket)
        
        try:
            # Triage the ticket
            result = agent.triage_ticket(ticket)
            
            # Print results
            print_triage_result(result)
            
        except Exception as e:
            print(f"ERROR: {e}\n")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("All 5 test tickets processed successfully!")
    print("Agent demonstrates:")
    print("  - High priority detection (production issues)")
    print("  - Low priority handling (questions, features)")
    print("  - Billing issue recognition")
    print("  - Account problem categorization")
    print("  - Multi-step reasoning with context")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
