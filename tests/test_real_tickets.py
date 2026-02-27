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

# Test tickets - various priority levels
TEST_TICKETS = [
    # CRITICAL Priority Test - Should score 75+
    {
        "ticket_id": "DEMO-CRITICAL",
        "customer_id": "CUST-001",
        "subject": "CRITICAL EMERGENCY: Production database completely down - All customers affected!",
        "description": "URGENT CRITICAL EMERGENCY! Our production database crashed 45 minutes ago and is completely down. ALL customers are impacted and cannot access the system. This is a production outage causing massive revenue loss. System is broken and not working at all. API is failing with errors. This is the third critical incident this week. Need immediate emergency help ASAP! Customers are calling and complaining.",
        "status": "open",
        "created_at": "2026-02-05T18:00:00Z"
    },
    # HIGH Priority Test - Should score 50-74
    {
        "ticket_id": "DEMO-HIGH",
        "customer_id": "CUST-005",
        "subject": "URGENT: Payment processing system is broken - customers cannot checkout",
        "description": "Our payment API is not working and customers are unable to complete purchases. This is causing immediate revenue impact. The error started 2 hours ago during peak sales time. Multiple customers have reported the issue. System is critically broken and needs urgent attention. This is blocking all transactions.",
        "status": "open",
        "created_at": "2026-02-05T17:30:00Z"
    },
    # MEDIUM Priority Test - Should score 25-49
    {
        "ticket_id": "DEMO-MEDIUM",
        "customer_id": "CUST-010",
        "subject": "API integration not working properly",
        "description": "Our API integration with your system has been intermittently failing since this morning. It's not completely down but errors are occurring frequently. This is affecting our workflow and we need it fixed soon.",
        "status": "open",
        "created_at": "2026-02-05T16:00:00Z"
    },
    # LOW Priority Tests - Should score <25
    {
        "ticket_id": "DEMO-LOW-1",
        "customer_id": "CUST-050",
        "subject": "Question about invoice",
        "description": "Hi, I received my invoice for last month but I don't understand one of the charges. Can you explain what 'platform fee' means?",
        "status": "open",
        "created_at": "2026-02-05T15:45:00Z"
    },
    {
        "ticket_id": "DEMO-LOW-2",
        "customer_id": "CUST-025",
        "subject": "Feature request: Dark mode",
        "description": "It would be great if you could add a dark mode to the dashboard. Many users including myself prefer dark themes for reduced eye strain.",
        "status": "open",
        "created_at": "2026-02-05T14:30:00Z"
    },
    {
        "ticket_id": "DEMO-LOW-3",
        "customer_id": "CUST-075",
        "subject": "How to export reports?",
        "description": "I'm trying to export my monthly reports but can't find the export button. Could you point me in the right direction?",
        "status": "open",
        "created_at": "2026-02-05T13:00:00Z"
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
    print("PRIORITY LEVEL VALIDATION TEST")
    print("Testing Agent Priority Detection: Critical, High, Medium, Low")
    print("="*80 + "\n")
    
    # Connect
    es = connect_es()
    if not es:
        return
    
    # Initialize agent
    agent = TriageAgent(es)
    print(f"Agent initialized: {agent.agent_name}\n")
    
    # Test each ticket
    print("Processing tickets across all priority levels...\n")
    
    results = []
    for i, ticket in enumerate(TEST_TICKETS, 1):
        print(f"\n[{i}/{len(TEST_TICKETS)}] Testing Ticket: {ticket['ticket_id']}")
        print_ticket_summary(ticket)
        
        try:
            # Triage the ticket
            result = agent.triage_ticket(ticket)
            results.append(result)
            
            # Print results
            print_triage_result(result)
            
        except Exception as e:
            print(f"ERROR: {e}\n")
    
    print("\n" + "="*80)
    print("PRIORITY DISTRIBUTION SUMMARY")
    print("="*80)
    
    # Count priorities
    priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for result in results:
        priority = result['triage_decision']['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print(f"\nCRITICAL (≥75): {priority_counts['critical']} tickets")
    print(f"HIGH (≥50):     {priority_counts['high']} tickets")
    print(f"MEDIUM (≥25):   {priority_counts['medium']} tickets")
    print(f"LOW (<25):      {priority_counts['low']} tickets")
    
    print("\nDETAILED RESULTS:")
    print("-"*80)
    for result in results:
        decision = result['triage_decision']
        ticket_id = result['ticket_id']
        priority = decision['priority'].upper()
        category = decision['category']
        team = decision['assigned_team']
        score = result['analysis']['priority_score']
        
        print(f"{ticket_id}: {priority:8} (score: {score:3}) | {category:12} | Team: {team}")
    
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    # Validate expectations
    validation_passed = True
    
    # Check if we have at least one of each priority
    if priority_counts['critical'] == 0:
        print("⚠️  WARNING: No CRITICAL priority tickets detected")
        validation_passed = False
    else:
        print(f"✓ CRITICAL priority working: {priority_counts['critical']} ticket(s)")
    
    if priority_counts['high'] == 0:
        print("⚠️  WARNING: No HIGH priority tickets detected")
        validation_passed = False
    else:
        print(f"✓ HIGH priority working: {priority_counts['high']} ticket(s)")
    
    if priority_counts['medium'] == 0:
        print("⚠️  WARNING: No MEDIUM priority tickets detected")
        validation_passed = False
    else:
        print(f"✓ MEDIUM priority working: {priority_counts['medium']} ticket(s)")
    
    if priority_counts['low'] == 0:
        print("⚠️  WARNING: No LOW priority tickets detected")
        validation_passed = False
    else:
        print(f"✓ LOW priority working: {priority_counts['low']} ticket(s)")
    
    if validation_passed:
        print("\n✅ AGENT VALIDATION PASSED: All priority levels working correctly!")
    else:
        print("\n⚠️  AGENT VALIDATION INCOMPLETE: Some priority levels not triggered")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
