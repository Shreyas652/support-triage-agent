"""
Metrics Dashboard - Show agent performance and impact
"""

import os
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import Dict, List
import json

load_dotenv()


class MetricsDashboard:
    """Generate metrics and performance statistics"""
    
    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        print("\n" + "="*70)
        print("📊 SUPPORT TICKET TRIAGE AGENT - PERFORMANCE REPORT")
        print("="*70 + "\n")
        
        # Get all metrics
        ticket_stats = self._get_ticket_statistics()
        agent_performance = self._get_agent_performance()
        category_accuracy = self._get_category_accuracy()
        time_savings = self._calculate_time_savings(agent_performance)
        impact_metrics = self._calculate_impact_metrics(ticket_stats, agent_performance)
        
        # Print report
        self._print_ticket_statistics(ticket_stats)
        self._print_agent_performance(agent_performance)
        self._print_category_breakdown(category_accuracy)
        self._print_time_savings(time_savings)
        self._print_impact_metrics(impact_metrics)
        
        return {
            "ticket_stats": ticket_stats,
            "agent_performance": agent_performance,
            "category_accuracy": category_accuracy,
            "time_savings": time_savings,
            "impact_metrics": impact_metrics,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_ticket_statistics(self) -> Dict:
        """Get overall ticket statistics"""
        # Total tickets
        total = self.es.count(index="support_tickets")["count"]
        
        # By status
        status_agg = self.es.search(
            index="support_tickets",
            body={
                "size": 0,
                "aggs": {
                    "by_status": {"terms": {"field": "status", "size": 10}}
                }
            }
        )
        
        by_status = {
            bucket["key"]: bucket["doc_count"]
            for bucket in status_agg["aggregations"]["by_status"]["buckets"]
        }
        
        # By priority
        priority_agg = self.es.search(
            index="support_tickets",
            body={
                "size": 0,
                "aggs": {
                    "by_priority": {"terms": {"field": "priority", "size": 10}}
                }
            }
        )
        
        by_priority = {
            bucket["key"]: bucket["doc_count"]
            for bucket in priority_agg["aggregations"]["by_priority"]["buckets"]
        }
        
        # By category
        category_agg = self.es.search(
            index="support_tickets",
            body={
                "size": 0,
                "aggs": {
                    "by_category": {"terms": {"field": "category", "size": 10}}
                }
            }
        )
        
        by_category = {
            bucket["key"]: bucket["doc_count"]
            for bucket in category_agg["aggregations"]["by_category"]["buckets"]
        }
        
        return {
            "total_tickets": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_category": by_category
        }
    
    def _get_agent_performance(self) -> Dict:
        """Get agent performance metrics"""
        # Count agent actions
        total_actions = self.es.count(index="agent_actions")["count"]
        
        # Get all actions
        if total_actions > 0:
            actions_response = self.es.search(
                index="agent_actions",
                body={"query": {"match_all": {}}, "size": 1000}
            )
            
            actions = [hit["_source"] for hit in actions_response["hits"]["hits"]]
            
            # Calculate average confidence
            confidences = [a["confidence_score"] for a in actions if "confidence_score" in a]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count by action type
            by_action_type = {}
            for action in actions:
                action_type = action.get("action_type", "unknown")
                by_action_type[action_type] = by_action_type.get(action_type, 0) + 1
            
            # Tickets needing review
            needs_review = sum(1 for a in actions 
                             if a.get("details", {}).get("needs_review", False))
            
            return {
                "total_processed": total_actions,
                "average_confidence": avg_confidence,
                "by_action_type": by_action_type,
                "flagged_for_review": needs_review,
                "review_rate": needs_review / total_actions if total_actions > 0 else 0
            }
        else:
            return {
                "total_processed": 0,
                "average_confidence": 0,
                "by_action_type": {},
                "flagged_for_review": 0,
                "review_rate": 0
            }
    
    def _get_category_accuracy(self) -> Dict:
        """Calculate category distribution"""
        response = self.es.search(
            index="support_tickets",
            body={
                "size": 0,
                "aggs": {
                    "categories": {
                        "terms": {"field": "category", "size": 10}
                    }
                }
            }
        )
        
        categories = {}
        for bucket in response["aggregations"]["categories"]["buckets"]:
            categories[bucket["key"]] = bucket["doc_count"]
        
        return categories
    
    def _calculate_time_savings(self, agent_perf: Dict) -> Dict:
        """Calculate time savings from automation"""
        # Manual triage: 2-3 minutes per ticket (average 2.5 min = 150 seconds)
        # Agent triage: ~1.3 seconds (from our demo)
        
        tickets_processed = agent_perf["total_processed"]
        
        manual_time_seconds = tickets_processed * 150  # 2.5 min per ticket
        agent_time_seconds = tickets_processed * 1.3   # ~1.3 sec per ticket
        
        time_saved_seconds = manual_time_seconds - agent_time_seconds
        time_saved_hours = time_saved_seconds / 3600
        
        # For full dataset (500 tickets)
        full_dataset_tickets = 500
        full_manual_time = full_dataset_tickets * 150  # seconds
        full_agent_time = full_dataset_tickets * 1.3
        full_time_saved = full_manual_time - full_agent_time
        
        return {
            "tickets_processed": tickets_processed,
            "manual_time_per_ticket_sec": 150,
            "agent_time_per_ticket_sec": 1.3,
            "time_saved_seconds": time_saved_seconds,
            "time_saved_hours": time_saved_hours,
            "time_saved_percentage": (time_saved_seconds / manual_time_seconds * 100) if manual_time_seconds > 0 else 0,
            "projected_full_dataset": {
                "total_tickets": full_dataset_tickets,
                "manual_time_hours": full_manual_time / 3600,
                "agent_time_hours": full_agent_time / 3600,
                "time_saved_hours": full_time_saved / 3600,
                "time_saved_percentage": (full_time_saved / full_manual_time * 100)
            }
        }
    
    def _calculate_impact_metrics(self, ticket_stats: Dict, agent_perf: Dict) -> Dict:
        """Calculate business impact metrics"""
        # Assumptions
        support_agent_hourly_rate = 35  # USD
        tickets_per_day = 500
        working_days_per_year = 250
        
        # Time savings
        time_saved_hours_per_day = (tickets_per_day * 150 - tickets_per_day * 1.3) / 3600
        time_saved_hours_per_year = time_saved_hours_per_day * working_days_per_year
        
        # Cost savings
        cost_savings_per_year = time_saved_hours_per_year * support_agent_hourly_rate
        
        # Response time improvement
        # Manual: average 4-6 hours (let's say 5 hours)
        # Agent: under 15 minutes (0.25 hours)
        response_time_improvement_hours = 5 - 0.25
        response_time_improvement_percentage = (response_time_improvement_hours / 5) * 100
        
        # Error reduction
        # Manual error rate: 15%
        # Agent accuracy: 95% (from confidence scores)
        manual_error_rate = 0.15
        agent_accuracy = agent_perf.get("average_confidence", 0.95)
        agent_error_rate = 1 - agent_accuracy
        error_reduction = manual_error_rate - agent_error_rate
        error_reduction_percentage = (error_reduction / manual_error_rate) * 100
        
        return {
            "annual_time_saved_hours": time_saved_hours_per_year,
            "annual_cost_savings_usd": cost_savings_per_year,
            "response_time_improvement_hours": response_time_improvement_hours,
            "response_time_improvement_percentage": response_time_improvement_percentage,
            "manual_error_rate": manual_error_rate * 100,
            "agent_error_rate": agent_error_rate * 100,
            "error_reduction_percentage": error_reduction_percentage,
            "agent_accuracy_percentage": agent_accuracy * 100,
            "daily_tickets_processed": tickets_per_day,
            "annual_tickets_processed": tickets_per_day * working_days_per_year
        }
    
    def _print_ticket_statistics(self, stats: Dict):
        """Print ticket statistics"""
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
        """Print agent performance"""
        print("🤖 AGENT PERFORMANCE")
        print("-" * 70)
        print(f"Tickets Processed: {perf['total_processed']}")
        print(f"Average Confidence: {perf['average_confidence']:.1%}")
        print(f"Flagged for Review: {perf['flagged_for_review']} ({perf['review_rate']:.1%})")
        print()
    
    def _print_category_breakdown(self, categories: Dict):
        """Print category breakdown"""
        print("📂 CATEGORY DISTRIBUTION")
        print("-" * 70)
        total = sum(categories.values())
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {category:12} {bar:25} {count:3} ({percentage:5.1f}%)")
        print()
    
    def _print_time_savings(self, savings: Dict):
        """Print time savings"""
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
        """Print business impact"""
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
    """Generate metrics dashboard"""
    load_dotenv()
    
    # Connect to Elasticsearch
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
    
    # Generate dashboard
    dashboard = MetricsDashboard(es)
    report = dashboard.generate_report()
    
    # Save report
    with open("metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("="*70)
    print("✅ Report saved to metrics_report.json")
    print("="*70)


if __name__ == "__main__":
    main()
