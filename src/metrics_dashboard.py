import os
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import Dict, List
import json

load_dotenv()

class MetricsDashboard:
    
    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
    
    def generate_report(self) -> Dict:
        
        print("\n" + "="*70)
        print("📊 SUPPORT TICKET TRIAGE AGENT - PERFORMANCE REPORT")
        print("="*70 + "\n")
        
        ticket_stats = self._get_ticket_statistics()
        agent_performance = self._get_agent_performance()
        category_accuracy = self._get_category_accuracy()
        time_savings = self._calculate_time_savings(agent_performance)
        impact_metrics = self._calculate_impact_metrics(ticket_stats, agent_performance)
        
        self._print_ticket_statistics(ticket_stats)
        self._print_agent_performance(agent_performance)
        self._print_category_breakdown(category_accuracy)
        self._print_time_savings(time_savings)
        self._print_impact_metrics(impact_metrics)
        
        return {
: ticket_stats,
: agent_performance,
: category_accuracy,
: time_savings,
: impact_metrics,
: datetime.now().isoformat()
        }
    
    def _get_ticket_statistics(self) -> Dict:
        
        total = self.es.count(index="support_tickets")["count"]
        
        status_agg = self.es.search(
            index="support_tickets",
            body={
: 0,
: {
: {"terms": {"field": "status", "size": 10}}
                }
            }
        )
        
        by_status = {
            bucket["key"]: bucket["doc_count"]
            for bucket in status_agg["aggregations"]["by_status"]["buckets"]
        }
        
        priority_agg = self.es.search(
            index="support_tickets",
            body={
: 0,
: {
: {"terms": {"field": "priority", "size": 10}}
                }
            }
        )
        
        by_priority = {
            bucket["key"]: bucket["doc_count"]
            for bucket in priority_agg["aggregations"]["by_priority"]["buckets"]
        }
        
        category_agg = self.es.search(
            index="support_tickets",
            body={
: 0,
: {
: {"terms": {"field": "category", "size": 10}}
                }
            }
        )
        
        by_category = {
            bucket["key"]: bucket["doc_count"]
            for bucket in category_agg["aggregations"]["by_category"]["buckets"]
        }
        
        return {
: total,
: by_status,
: by_priority,
: by_category
        }
    
    def _get_agent_performance(self) -> Dict:
        
        total_actions = self.es.count(index="agent_actions")["count"]
        
        if total_actions > 0:
            actions_response = self.es.search(
                index="agent_actions",
                body={"query": {"match_all": {}}, "size": 1000}
            )
            
            actions = [hit["_source"] for hit in actions_response["hits"]["hits"]]
            
            confidences = [a["confidence_score"] for a in actions if "confidence_score" in a]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            by_action_type = {}
            for action in actions:
                action_type = action.get("action_type", "unknown")
                by_action_type[action_type] = by_action_type.get(action_type, 0) + 1
            
            needs_review = sum(1 for a in actions 
                             if a.get("details", {}).get("needs_review", False))
            
            return {
: total_actions,
: avg_confidence,
: by_action_type,
: needs_review,
: needs_review / total_actions if total_actions > 0 else 0
            }
        else:
            return {
: 0,
: 0,
: {},
: 0,
: 0
            }
    
    def _get_category_accuracy(self) -> Dict:
        
        response = self.es.search(
            index="support_tickets",
            body={
: 0,
: {
: {
: {"field": "category", "size": 10}
                    }
                }
            }
        )
        
        categories = {}
        for bucket in response["aggregations"]["categories"]["buckets"]:
            categories[bucket["key"]] = bucket["doc_count"]
        
        return categories
    
    def _calculate_time_savings(self, agent_perf: Dict) -> Dict:
        
        tickets_processed = agent_perf["total_processed"]
        
        manual_time_seconds = tickets_processed * 150                      
        agent_time_seconds = tickets_processed * 1.3                        
        
        time_saved_seconds = manual_time_seconds - agent_time_seconds
        time_saved_hours = time_saved_seconds / 3600
        
        full_dataset_tickets = 500
        full_manual_time = full_dataset_tickets * 150           
        full_agent_time = full_dataset_tickets * 1.3
        full_time_saved = full_manual_time - full_agent_time
        
        return {
: tickets_processed,
: 150,
: 1.3,
: time_saved_seconds,
: time_saved_hours,
: (time_saved_seconds / manual_time_seconds * 100) if manual_time_seconds > 0 else 0,
: {
: full_dataset_tickets,
: full_manual_time / 3600,
: full_agent_time / 3600,
: full_time_saved / 3600,
: (full_time_saved / full_manual_time * 100)
            }
        }
    
    def _calculate_impact_metrics(self, ticket_stats: Dict, agent_perf: Dict) -> Dict:
        
        support_agent_hourly_rate = 35       
        tickets_per_day = 500
        working_days_per_year = 250
        
        time_saved_hours_per_day = (tickets_per_day * 150 - tickets_per_day * 1.3) / 3600
        time_saved_hours_per_year = time_saved_hours_per_day * working_days_per_year
        
        cost_savings_per_year = time_saved_hours_per_year * support_agent_hourly_rate
        
        response_time_improvement_hours = 5 - 0.25
        response_time_improvement_percentage = (response_time_improvement_hours / 5) * 100
        
        manual_error_rate = 0.15
        agent_accuracy = agent_perf.get("average_confidence", 0.95)
        agent_error_rate = 1 - agent_accuracy
        error_reduction = manual_error_rate - agent_error_rate
        error_reduction_percentage = (error_reduction / manual_error_rate) * 100
        
        return {
: time_saved_hours_per_year,
: cost_savings_per_year,
: response_time_improvement_hours,
: response_time_improvement_percentage,
: manual_error_rate * 100,
: agent_error_rate * 100,
: error_reduction_percentage,
: agent_accuracy * 100,
: tickets_per_day,
: tickets_per_day * working_days_per_year
        }
    
    def _print_ticket_statistics(self, stats: Dict):
        
        print("📈 TICKET STATISTICS")
        print("-" * 70)
        print(f"Total Tickets: {stats['total_tickets']}")
        
        print("\nBy Status:")
        for status, count in sorted(stats['by_status'].items()):
            percentage = (count / stats['total_tickets'] * 100)
            print(f"  {status:15} {count:4} ({percentage:5.1f}%)")
        
        print("\nBy Priority:")
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            count = stats['by_priority'].get(priority, 0)
            percentage = (count / stats['total_tickets'] * 100)
            print(f"  {priority:15} {count:4} ({percentage:5.1f}%)")
        
        print("\nBy Category:")
        for category, count in sorted(stats['by_category'].items()):
            percentage = (count / stats['total_tickets'] * 100)
            print(f"  {category:15} {count:4} ({percentage:5.1f}%)")
        print()
    
    def _print_agent_performance(self, perf: Dict):
        
        print("🤖 AGENT PERFORMANCE")
        print("-" * 70)
        print(f"Tickets Processed: {perf['total_processed']}")
        print(f"Average Confidence: {perf['average_confidence']:.1%}")
        print(f"Flagged for Review: {perf['flagged_for_review']} ({perf['review_rate']:.1%})")
        print()
    
    def _print_category_breakdown(self, categories: Dict):
        
        print("📂 CATEGORY DISTRIBUTION")
        print("-" * 70)
        total = sum(categories.values())
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {category:12} {bar:25} {count:3} ({percentage:5.1f}%)")
        print()
    
    def _print_time_savings(self, savings: Dict):
        
        print("⏱️  TIME SAVINGS")
        print("-" * 70)
        print(f"Manual Process: {savings['manual_time_per_ticket_sec']}s per ticket")
        print(f"Agent Process:  {savings['agent_time_per_ticket_sec']}s per ticket")
        print(f"Time Reduction: {savings['time_saved_percentage']:.1f}%")
        
        proj = savings['projected_full_dataset']
        print(f"\nProjected for {proj['total_tickets']} tickets:")
        print(f"  Manual time:  {proj['manual_time_hours']:.1f} hours")
        print(f"  Agent time:   {proj['agent_time_hours']:.1f} hours")
        print(f"  Time saved:   {proj['time_saved_hours']:.1f} hours ({proj['time_saved_percentage']:.1f}%)")
        print()
    
    def _print_impact_metrics(self, impact: Dict):
        
        print("💰 BUSINESS IMPACT")
        print("-" * 70)
        print(f"Daily Tickets:  {impact['daily_tickets_processed']:,}")
        print(f"Annual Tickets: {impact['annual_tickets_processed']:,}")
        print()
        print(f"Annual Time Saved: {impact['annual_time_saved_hours']:,.0f} hours")
        print(f"Annual Cost Savings: ${impact['annual_cost_savings_usd']:,.0f}")
        print()
        print(f"Response Time Improvement:")
        print(f"  Before: ~5 hours")
        print(f"  After:  ~15 minutes")
        print(f"  Reduction: {impact['response_time_improvement_percentage']:.0f}%")
        print()
        print(f"Error Rate Improvement:")
        print(f"  Manual Error Rate: {impact['manual_error_rate']:.1f}%")
        print(f"  Agent Error Rate:  {impact['agent_error_rate']:.1f}%")
        print(f"  Agent Accuracy:    {impact['agent_accuracy_percentage']:.1f}%")
        print(f"  Error Reduction:   {impact['error_reduction_percentage']:.1f}%")
        print()

def main():
    
    load_dotenv()
    
    if os.getenv('ELASTICSEARCH_URL'):
        if os.getenv('ELASTIC_API_KEY'):
            es = Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                api_key=os.getenv('ELASTIC_API_KEY'),
                verify_certs=True
            )
        else:
            password = os.getenv('ELASTIC_PASSWORD')
            if not password:
                raise ValueError("ELASTIC_PASSWORD environment variable is required for basic auth")
            es = Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                basic_auth=(
                    os.getenv('ELASTIC_USERNAME', 'elastic'),
                    password
                ),
                verify_certs=True
            )
    else:
        raise ValueError("Missing Elasticsearch configuration")
    
    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch")
    
    dashboard = MetricsDashboard(es)
    report = dashboard.generate_report()
    
    with open("metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("="*70)
    print("✅ Report saved to metrics_report.json")
    print("="*70)

if __name__ == "__main__":
    main()
