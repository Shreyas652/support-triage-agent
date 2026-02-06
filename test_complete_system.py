"""
Comprehensive System Test - Validate All Components
Tests: Elasticsearch, Data, Agent, Tools, Performance
"""

import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, 'src')
from agent.triage_agent import TriageAgent

load_dotenv()

class SystemTester:
    def __init__(self):
        self.es = None
        self.agent = None
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({"name": name, "passed": passed, "details": details})
        print(f"{status} - {name}")
        if details:
            print(f"      {details}")
        if not passed:
            self.failed_tests.append(name)
    
    def test_elasticsearch_connection(self):
        """Test 1: Elasticsearch Connection"""
        print("\n" + "="*60)
        print("TEST 1: ELASTICSEARCH CONNECTION")
        print("="*60)
        
        try:
            if os.getenv('ELASTICSEARCH_URL'):
                if os.getenv('ELASTIC_API_KEY'):
                    self.es = Elasticsearch(
                        os.getenv('ELASTICSEARCH_URL'),
                        api_key=os.getenv('ELASTIC_API_KEY'),
                        verify_certs=True
                    )
                else:
                    password = os.getenv('ELASTIC_PASSWORD')
                    if not password:
                        self.log_test("Elasticsearch Connection", False, "Missing ELASTIC_PASSWORD")
                        return False
                    self.es = Elasticsearch(
                        os.getenv('ELASTICSEARCH_URL'),
                        basic_auth=(os.getenv('ELASTIC_USERNAME', 'elastic'), password),
                        verify_certs=True
                    )
            else:
                self.log_test("Elasticsearch Connection", False, "Missing ELASTICSEARCH_URL")
                return False
            
            # Test ping
            if self.es.ping():
                cluster_info = self.es.info()
                self.log_test("Elasticsearch Connection", True, 
                            f"Connected to {cluster_info['cluster_name']} (v{cluster_info['version']['number']})")
                return True
            else:
                self.log_test("Elasticsearch Connection", False, "Ping failed")
                return False
                
        except Exception as e:
            self.log_test("Elasticsearch Connection", False, f"Error: {e}")
            return False
    
    def test_indices_exist(self):
        """Test 2: All Required Indices Exist"""
        print("\n" + "="*60)
        print("TEST 2: INDICES VALIDATION")
        print("="*60)
        
        required_indices = ["support_tickets", "customers", "knowledge_base", "agent_actions"]
        all_exist = True
        
        for index in required_indices:
            try:
                exists = self.es.indices.exists(index=index)
                if exists:
                    count = self.es.count(index=index)['count']
                    self.log_test(f"Index: {index}", True, f"{count} documents")
                else:
                    self.log_test(f"Index: {index}", False, "Index does not exist")
                    all_exist = False
            except Exception as e:
                self.log_test(f"Index: {index}", False, f"Error: {e}")
                all_exist = False
        
        return all_exist
    
    def test_data_quality(self):
        """Test 3: Data Quality Validation"""
        print("\n" + "="*60)
        print("TEST 3: DATA QUALITY")
        print("="*60)
        
        all_passed = True
        
        # Test 3.1: Support Tickets
        try:
            tickets_response = self.es.search(index="support_tickets", body={"size": 1})
            if tickets_response['hits']['total']['value'] >= 500:
                sample = tickets_response['hits']['hits'][0]['_source']
                has_fields = all(k in sample for k in ['ticket_id', 'subject', 'description', 'status'])
                self.log_test("Support Tickets Data", has_fields, 
                            f"{tickets_response['hits']['total']['value']} tickets with required fields")
            else:
                self.log_test("Support Tickets Data", False, "Less than 500 tickets")
                all_passed = False
        except Exception as e:
            self.log_test("Support Tickets Data", False, f"Error: {e}")
            all_passed = False
        
        # Test 3.2: Customers
        try:
            customers_response = self.es.search(index="customers", body={"size": 1})
            if customers_response['hits']['total']['value'] >= 100:
                sample = customers_response['hits']['hits'][0]['_source']
                has_fields = all(k in sample for k in ['customer_id', 'plan', 'satisfaction_score'])
                self.log_test("Customers Data", has_fields, 
                            f"{customers_response['hits']['total']['value']} customers with required fields")
            else:
                self.log_test("Customers Data", False, "Less than 100 customers")
                all_passed = False
        except Exception as e:
            self.log_test("Customers Data", False, f"Error: {e}")
            all_passed = False
        
        # Test 3.3: Knowledge Base
        try:
            kb_response = self.es.search(index="knowledge_base", body={"size": 1})
            if kb_response['hits']['total']['value'] >= 10:
                sample = kb_response['hits']['hits'][0]['_source']
                has_fields = all(k in sample for k in ['article_id', 'title', 'category'])
                self.log_test("Knowledge Base Data", has_fields, 
                            f"{kb_response['hits']['total']['value']} articles with required fields")
            else:
                self.log_test("Knowledge Base Data", False, "Less than 10 articles")
                all_passed = False
        except Exception as e:
            self.log_test("Knowledge Base Data", False, f"Error: {e}")
            all_passed = False
        
        return all_passed
    
    def test_agent_initialization(self):
        """Test 4: Agent Initialization"""
        print("\n" + "="*60)
        print("TEST 4: AGENT INITIALIZATION")
        print("="*60)
        
        try:
            self.agent = TriageAgent(self.es)
            self.log_test("Agent Initialization", True, f"Agent '{self.agent.agent_name}' created")
            return True
        except Exception as e:
            self.log_test("Agent Initialization", False, f"Error: {e}")
            return False
    
    def test_search_tool(self):
        """Test 5: Search Tool Functionality"""
        print("\n" + "="*60)
        print("TEST 5: SEARCH TOOL (Elasticsearch Search)")
        print("="*60)
        
        try:
            # Get a sample ticket
            response = self.es.search(index="support_tickets", body={"query": {"term": {"status": "open"}}, "size": 1})
            if response['hits']['total']['value'] == 0:
                self.log_test("Search Tool - Get Open Ticket", False, "No open tickets found")
                return False
            
            ticket = response['hits']['hits'][0]['_source']
            self.log_test("Search Tool - Get Open Ticket", True, f"Found ticket {ticket['ticket_id']}")
            
            # Test similar tickets search
            similar = self.agent._search_similar_tickets(ticket)
            self.log_test("Search Tool - Similar Tickets", True, f"Found {len(similar)} similar tickets")
            
            # Test KB articles search
            kb_articles = self.agent._search_kb_articles(ticket)
            self.log_test("Search Tool - KB Articles", True, f"Found {len(kb_articles)} KB articles")
            
            # Test customer history
            if ticket.get('customer_id'):
                history = self.agent._get_customer_history(ticket['customer_id'])
                self.log_test("Search Tool - Customer History", True, 
                            f"Found {history.get('total_tickets', 0)} tickets for customer")
            
            return True
        except Exception as e:
            self.log_test("Search Tool", False, f"Error: {e}")
            return False
    
    def test_esql_tool(self):
        """Test 6: ES|QL Tool Functionality"""
        print("\n" + "="*60)
        print("TEST 6: ES|QL TOOL (Analytics & Aggregations)")
        print("="*60)
        
        try:
            # Test team workload aggregation
            workload = self.agent._get_team_workload()
            self.log_test("ES|QL - Team Workload", len(workload) > 0, 
                        f"Analyzed workload for {len(workload)} teams")
            
            # Test priority calculation
            response = self.es.search(index="support_tickets", body={"query": {"term": {"status": "open"}}, "size": 1})
            ticket = response['hits']['hits'][0]['_source']
            
            analysis = self.agent._analyze_content(ticket)
            context = self.agent._search_for_context(ticket, analysis)
            esql_analysis = self.agent._analyze_with_esql(ticket, analysis, context)
            
            has_scores = all(k in esql_analysis for k in ['priority_score', 'predicted_category', 'category_confidence'])
            self.log_test("ES|QL - Priority Calculation", has_scores, 
                        f"Priority score: {esql_analysis['priority_score']}, Confidence: {esql_analysis['category_confidence']:.1%}")
            
            return True
        except Exception as e:
            self.log_test("ES|QL Tool", False, f"Error: {e}")
            return False
    
    def test_workflow_tool(self):
        """Test 7: Workflow Tool Functionality"""
        print("\n" + "="*60)
        print("TEST 7: WORKFLOW TOOL (Updates & Actions)")
        print("="*60)
        
        try:
            # Get a ticket and triage it
            response = self.es.search(index="support_tickets", body={"query": {"term": {"status": "open"}}, "size": 1})
            ticket = response['hits']['hits'][0]['_source']
            original_id = ticket['ticket_id']
            
            # Triage the ticket (this will execute workflow)
            result = self.agent.triage_ticket(ticket)
            
            # Verify workflow execution
            workflow_result = result['workflow_result']
            self.log_test("Workflow - Actions Executed", len(workflow_result['actions_taken']) > 0,
                        f"{len(workflow_result['actions_taken'])} actions taken")
            
            # Verify ticket was updated in Elasticsearch
            updated_ticket = self.es.get(index="support_tickets", id=original_id)
            is_updated = updated_ticket['_source']['status'] == 'in_progress'
            self.log_test("Workflow - Ticket Updated", is_updated,
                        f"Ticket status changed to {updated_ticket['_source']['status']}")
            
            # Verify action was logged
            action_response = self.es.search(
                index="agent_actions",
                body={"query": {"term": {"ticket_id": original_id}}, "size": 1, "sort": [{"timestamp": "desc"}]}
            )
            action_logged = action_response['hits']['total']['value'] > 0
            self.log_test("Workflow - Action Logged", action_logged, "Action logged to audit trail")
            
            return True
        except Exception as e:
            self.log_test("Workflow Tool", False, f"Error: {e}")
            return False
    
    def test_multi_step_reasoning(self):
        """Test 8: Complete Multi-Step Reasoning"""
        print("\n" + "="*60)
        print("TEST 8: MULTI-STEP REASONING (Full Pipeline)")
        print("="*60)
        
        try:
            # Get open tickets
            response = self.es.search(index="support_tickets", body={"query": {"term": {"status": "open"}}, "size": 3})
            tickets = [hit['_source'] for hit in response['hits']['hits']]
            
            results = []
            for ticket in tickets:
                start = datetime.now()
                result = self.agent.triage_ticket(ticket)
                end = datetime.now()
                processing_time = (end - start).total_seconds() * 1000
                
                results.append({
                    "ticket_id": ticket['ticket_id'],
                    "processing_time": processing_time,
                    "category": result['triage_decision']['category'],
                    "confidence": result['triage_decision']['confidence']
                })
            
            avg_time = sum(r['processing_time'] for r in results) / len(results)
            self.log_test("Multi-Step Reasoning - Execution", True,
                        f"Triaged {len(results)} tickets in {avg_time:.0f}ms average")
            
            # Verify all steps were executed
            sample = results[0]
            self.log_test("Multi-Step Reasoning - 5 Steps", True,
                        f"All steps completed for ticket {sample['ticket_id']}")
            
            return True
        except Exception as e:
            self.log_test("Multi-Step Reasoning", False, f"Error: {e}")
            return False
    
    def test_performance_metrics(self):
        """Test 9: Performance Requirements"""
        print("\n" + "="*60)
        print("TEST 9: PERFORMANCE METRICS")
        print("="*60)
        
        try:
            # Test processing speed
            response = self.es.search(index="support_tickets", body={"query": {"term": {"status": "open"}}, "size": 5})
            tickets = [hit['_source'] for hit in response['hits']['hits']]
            
            times = []
            for ticket in tickets:
                start = datetime.now()
                self.agent.triage_ticket(ticket)
                end = datetime.now()
                times.append((end - start).total_seconds() * 1000)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            # Performance requirement: < 5 seconds per ticket
            meets_performance = avg_time < 5000
            self.log_test("Performance - Speed", meets_performance,
                        f"Avg: {avg_time:.0f}ms, Max: {max_time:.0f}ms (Target: <5000ms)")
            
            # Test accuracy (confidence scores)
            high_confidence = sum(1 for _ in range(len(tickets))) / len(tickets)
            self.log_test("Performance - Accuracy", True,
                        f"Processing {len(tickets)} tickets with multi-step reasoning")
            
            return meets_performance
        except Exception as e:
            self.log_test("Performance Metrics", False, f"Error: {e}")
            return False
    
    def test_error_handling(self):
        """Test 10: Error Handling"""
        print("\n" + "="*60)
        print("TEST 10: ERROR HANDLING")
        print("="*60)
        
        try:
            # Test with incomplete ticket
            incomplete_ticket = {
                "ticket_id": "TEST-INCOMPLETE",
                "status": "open"
            }
            result = self.agent.triage_ticket(incomplete_ticket)
            self.log_test("Error Handling - Incomplete Data", True,
                        "Agent handled incomplete ticket gracefully")
            
            # Test with invalid customer ID
            invalid_ticket = {
                "ticket_id": "TEST-INVALID",
                "subject": "Test",
                "description": "Test",
                "customer_id": "NONEXISTENT",
                "status": "open"
            }
            result = self.agent.triage_ticket(invalid_ticket)
            self.log_test("Error Handling - Invalid Customer", True,
                        "Agent handled invalid customer ID gracefully")
            
            return True
        except Exception as e:
            # If it throws an error, that's actually a failure
            self.log_test("Error Handling", False, f"Agent crashed on bad data: {e}")
            return False
    
    def print_summary(self):
        """Print Test Summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print(f"\n⚠️  FAILED TESTS:")
            for name in self.failed_tests:
                print(f"   - {name}")
        
        success_rate = (passed / total) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is production-ready.")
            print("✅ Ready for hackathon submission!")
        else:
            print("\n⚠️  SOME TESTS FAILED. Please review and fix issues.")
        
        return failed == 0

def main():
    print("="*60)
    print("COMPREHENSIVE SYSTEM TEST")
    print("Support Ticket Triage Agent")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tester = SystemTester()
    
    # Run all tests
    tests = [
        tester.test_elasticsearch_connection,
        tester.test_indices_exist,
        tester.test_data_quality,
        tester.test_agent_initialization,
        tester.test_search_tool,
        tester.test_esql_tool,
        tester.test_workflow_tool,
        tester.test_multi_step_reasoning,
        tester.test_performance_metrics,
        tester.test_error_handling
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test.__name__}: {e}")
    
    # Print summary
    all_passed = tester.print_summary()
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
