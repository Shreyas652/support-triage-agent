import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import uuid

load_dotenv()

class TriageAgent:

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.agent_name = "intelligent_triage_agent"

    def triage_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n{'='*60}")
        print(f"[TICKET] {ticket.get('ticket_id', 'UNKNOWN')}")
        print(f"Subject: {ticket.get('subject', 'No subject')}")
        print(f"{'='*60}\n")

        analysis = self._analyze_content(ticket)
        print(f"[STEP 1] Content Analysis")
        print(f"  - Sentiment: {analysis['sentiment']}")
        print(f"  - Urgency indicators: {len(analysis['urgency_keywords'])}")

        search_context = self._search_for_context(ticket, analysis)
        print(f"\n[STEP 2] Search Tool - Context Discovery")
        print(f"  - Similar tickets: {len(search_context['similar_tickets'])}")
        print(f"  - KB articles: {len(search_context['kb_articles'])}")
        print(f"  - Customer history: {search_context['customer_history'].get('total_tickets', 0)} previous tickets")

        esql_analysis = self._analyze_with_esql(ticket, analysis, search_context)
        print(f"\n[STEP 3] ES|QL Tool - Pattern Analysis")
        print(f"  - Priority score: {esql_analysis['priority_score']}")
        print(f"  - Category confidence: {esql_analysis['category_confidence']:.1%}")
        print(f"  - Recommended team: {esql_analysis['recommended_team']}")

        decision = self._make_decision(ticket, analysis, search_context, esql_analysis)
        print(f"\n[STEP 4] Triage Decision")
        print(f"  - Category: {decision['category']}")
        print(f"  - Priority: {decision['priority']}")
        print(f"  - Assigned team: {decision['assigned_team']}")
        print(f"  - Confidence: {decision['confidence']:.1%}")

        workflow_result = self._execute_workflow(ticket, decision, search_context)
        print(f"\n[STEP 5] Workflow Tool - Actions Executed")
        for action in workflow_result['actions_taken']:
            print(f"  + {action}")

        ticket_id = ticket.get("ticket_id", "UNKNOWN")
        result = {
            "ticket_id": ticket_id,
            "original_status": ticket.get("status", "open"),
            "triage_decision": decision,
            "context": {
                "similar_tickets_found": len(search_context['similar_tickets']),
                "kb_articles_found": len(search_context['kb_articles']),
                "customer_history": search_context['customer_history']
            },
            "analysis": esql_analysis,
            "workflow_result": workflow_result,
            "suggested_response": self._generate_response(ticket, search_context, decision),
            "processing_time_ms": 0
        }

        self._log_agent_action(ticket_id, decision, result)

        print(f"\n[COMPLETE] Triage finished successfully")
        print(f"{'='*60}\n")

        return result

    def _analyze_content(self, ticket: Dict[str, Any]) -> Dict[str, Any]:

        subject = str(ticket.get('subject', ''))
        description = str(ticket.get('description', ''))
        text = f"{subject} {description}".lower()

        negative_words = ['frustrated', 'angry', 'terrible', 'worst', 'unacceptable',
                         'disappointed', 'furious', 'immediately', 'urgent', 'charged',
                         'double charged', 'locked', 'blocked', 'denied', 'failed', 'wrong']
        positive_words = ['thanks', 'appreciate', 'great', 'love', 'excellent']

        negative_count = sum(1 for word in negative_words if word in text)
        positive_count = sum(1 for word in positive_words if word in text)

        if negative_count > positive_count:
            sentiment = 'negative'
        elif positive_count > 0:
            sentiment = 'positive'
        else:
            sentiment = 'neutral'

        urgency_keywords = ['urgent', 'immediately', 'critical', 'emergency', 'asap',
                           'production', 'down', 'not working', 'broken', 'cant', 'cannot',
                           'stopped working', 'crashed', 'error', 'failing', 'charged',
                           'double charged', 'cancelled', 'locked out', 'data loss',
                           'security', 'breach', 'outage', 'unreachable', 'refund']

        found_keywords = [kw for kw in urgency_keywords if kw in text]

        return {
            'sentiment': sentiment,
            'urgency_keywords': found_keywords,
            'negative_count': negative_count,
            'positive_count': positive_count
        }

    def _search_for_context(self, ticket: Dict[str, Any], analysis: Dict) -> Dict[str, Any]:

        similar_tickets = self._search_similar_tickets(ticket)

        kb_articles = self._search_kb_articles(ticket)

        customer_id = ticket.get('customer_id')
        customer_history = self._get_customer_history(customer_id) if customer_id else {}

        return {
            'similar_tickets': similar_tickets,
            'kb_articles': kb_articles,
            'customer_history': customer_history
        }

    def _search_similar_tickets(self, ticket: Dict[str, Any]) -> List[Dict]:
        try:
            query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": ticket.get('subject', ''),
                                "fields": ["subject^2", "description"],
                                "type": "best_fields"
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"status": "resolved"}}
                    ]
                }
            }

            response = self.es.search(
                index="support_tickets",
                body={"query": query, "size": 5}
            )

            return [
                {
                    "ticket_id": hit["_source"]["ticket_id"],
                    "subject": hit["_source"]["subject"],
                    "category": hit["_source"]["category"],
                    "priority": hit["_source"]["priority"],
                    "resolution_time": hit["_source"].get("resolution_time_minutes"),
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        except Exception as e:
            print(f"[WARNING] Error searching similar tickets: {e}")
            return []

    def _search_kb_articles(self, ticket: Dict[str, Any]) -> List[Dict]:
        try:
            query = {
                "multi_match": {
                    "query": f"{ticket.get('subject', '')} {ticket.get('description', '')}",
                    "fields": ["title^3", "content", "tags^2"]
                }
            }

            response = self.es.search(
                index="knowledge_base",
                body={"query": query, "size": 3}
            )

            return [
                {
                    "article_id": hit["_source"]["article_id"],
                    "title": hit["_source"]["title"],
                    "category": hit["_source"]["category"],
                    "helpful_count": hit["_source"]["helpful_count"],
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        except Exception as e:
            print(f"[WARNING] Error searching KB: {e}")
            return []

    def _get_customer_history(self, customer_id: str) -> Dict:
        try:

            customer_response = self.es.get(index="customers", id=customer_id)
            customer = customer_response["_source"]

            tickets_response = self.es.search(
                index="support_tickets",
                body={
                    "query": {"term": {"customer_id": customer_id}},
                    "size": 10,
                    "sort": [{"created_at": "desc"}]
                }
            )

            past_tickets = [hit["_source"] for hit in tickets_response["hits"]["hits"]]

            return {
                "customer_id": customer_id,
                "plan": customer.get("plan", "free"),
                "satisfaction_score": customer.get("satisfaction_score", 3.0),
                "total_tickets": len(past_tickets),
                "past_tickets": past_tickets[:5]
            }
        except Exception as e:
            print(f"[WARNING] Error getting customer history: {e}")
            return {
                "customer_id": customer_id,
                "plan": "free",
                "satisfaction_score": 3.0,
                "total_tickets": 0,
                "past_tickets": []
            }

    def _analyze_with_esql(self, ticket: Dict, analysis: Dict, context: Dict) -> Dict:

        priority_score = 0

        priority_score += len(analysis['urgency_keywords']) * 15

        if analysis['sentiment'] == 'negative':
            priority_score += 20
        elif analysis['sentiment'] == 'positive':
            priority_score -= 5

        plan_multipliers = {
            'enterprise': 2.0,
            'business': 1.5,
            'pro': 1.0,
            'free': 0.5
        }
        plan = context['customer_history'].get('plan', 'free')
        priority_score = int(priority_score * plan_multipliers[plan])

        satisfaction = context['customer_history'].get('satisfaction_score', 3.0)
        if satisfaction < 3.0:
            priority_score += 15

        priority_score = min(priority_score, 100)

        category_votes = {}
        for similar in context['similar_tickets']:
            cat = similar['category']
            category_votes[cat] = category_votes.get(cat, 0) + 1

        if category_votes:
            predicted_category = max(category_votes.items(), key=lambda x: x[1])[0]
            category_confidence = category_votes[predicted_category] / len(context['similar_tickets'])
        else:

            predicted_category = self._classify_by_keywords(ticket)
            category_confidence = 0.6

        team_mapping = {
            'technical': 'engineering',
            'billing': 'billing',
            'account': 'success',
            'feature': 'product'
        }
        recommended_team = team_mapping.get(predicted_category, 'support')

        team_workload = self._get_team_workload()

        return {
            'priority_score': priority_score,
            'predicted_category': predicted_category,
            'category_confidence': category_confidence,
            'recommended_team': recommended_team,
            'team_workload': team_workload,
            'factors': {
                'urgency_keywords': len(analysis['urgency_keywords']),
                'sentiment': analysis['sentiment'],
                'customer_plan': plan,
                'customer_satisfaction': satisfaction
            }
        }

    def _classify_by_keywords(self, ticket: Dict) -> str:
        text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

        category_keywords = {
            'technical': ['error', 'crash', 'bug', 'not working', 'broken', 'api', 'integration', 'performance', 'slow'],
            'billing': ['charge', 'payment', 'invoice', 'refund', 'subscription', 'billing', 'credit card'],
            'account': ['login', 'password', 'access', 'account', 'email', 'locked', 'reset'],
            'feature': ['request', 'feature', 'suggestion', 'would like', 'can you add', 'need']
        }

        scores = {}
        for category, keywords in category_keywords.items():
            scores[category] = sum(1 for kw in keywords if kw in text)

        return max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else 'technical'

    def _get_team_workload(self) -> Dict[str, int]:
        try:
            response = self.es.search(
                index="support_tickets",
                body={
                    "size": 0,
                    "query": {"term": {"status": "open"}},
                    "aggs": {
                        "by_team": {
                            "terms": {"field": "assigned_team", "size": 10}
                        }
                    }
                }
            )

            workload = {}
            for bucket in response["aggregations"]["by_team"]["buckets"]:
                workload[bucket["key"]] = bucket["doc_count"]

            return workload
        except Exception as e:
            print(f"[WARNING] Error getting team workload: {e}")
            return {}

    def _make_decision(self, ticket: Dict, analysis: Dict,
                      context: Dict, esql_analysis: Dict) -> Dict:

        priority_score = esql_analysis['priority_score']
        if priority_score >= 75:
            priority = 'critical'
        elif priority_score >= 50:
            priority = 'high'
        elif priority_score >= 25:
            priority = 'medium'
        else:
            priority = 'low'

        category = esql_analysis['predicted_category']

        assigned_team = esql_analysis['recommended_team']

        confidence = esql_analysis['category_confidence']

        needs_human_review = confidence < 0.7 or priority == 'critical'

        return {
            'category': category,
            'priority': priority,
            'assigned_team': assigned_team,
            'confidence': confidence,
            'needs_human_review': needs_human_review,
            'reasoning': {
                'priority_factors': esql_analysis['factors'],
                'similar_tickets_used': len(context['similar_tickets']),
                'kb_articles_found': len(context['kb_articles'])
            }
        }

    def _execute_workflow(self, ticket: Dict, decision: Dict, context: Dict) -> Dict:
        actions_taken = []

        ticket_id = ticket.get("ticket_id", "UNKNOWN")

        try:
            if ticket_id != "UNKNOWN":
                self.es.update(
                    index="support_tickets",
                    id=ticket_id,
                    body={
                        "doc": {
                            "category": decision['category'],
                            "priority": decision['priority'],
                            "assigned_team": decision['assigned_team'],
                            "status": "in_progress",
                            "updated_at": datetime.now().isoformat()
                        }
                    }
                )
                actions_taken.append(f"Updated ticket fields (category={decision['category']}, priority={decision['priority']})")
            else:
                actions_taken.append("Skipped ticket update (no ticket ID)")
        except Exception as e:
            print(f"[WARNING] Error updating ticket: {e}")
            actions_taken.append(f"Failed to update ticket: {e}")

        actions_taken.append(f"Assigned to {decision['assigned_team']} team")

        if decision['priority'] in ['critical', 'high']:
            actions_taken.append(f"Sent high-priority alert to {decision['assigned_team']} team")
        else:
            actions_taken.append(f"Added to {decision['assigned_team']} queue")

        if decision['needs_human_review']:
            actions_taken.append("Flagged for human review (low confidence or critical priority)")

        return {
            'actions_taken': actions_taken,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }

    def _generate_response(self, ticket: Dict, context: Dict, decision: Dict) -> str:
        kb_articles = context['kb_articles']
        subject = ticket.get('subject', 'your issue')

        if kb_articles:
            article = kb_articles[0]
            response = f"Thank you for contacting support. Based on your issue regarding '{subject}', " \
                      f"we've categorized this as a {decision['category']} issue with {decision['priority']} priority. " \
                      f"\n\nYou might find this helpful: {article['title']} (Article {article['article_id']})" \
                      f"\n\nOur {decision['assigned_team']} team will review your ticket shortly."
        else:
            response = f"Thank you for contacting support. We've received your ticket regarding '{subject}'. " \
                      f"This has been categorized as a {decision['category']} issue with {decision['priority']} priority. " \
                      f"Our {decision['assigned_team']} team will get back to you soon."

        return response

    def _log_agent_action(self, ticket_id: str, decision: Dict, result: Dict):
        try:
            action_doc = {
                "action_id": str(uuid.uuid4()),
                "ticket_id": ticket_id,
                "agent_name": self.agent_name,
                "action_type": "triage",
                "details": {
                    "category": decision['category'],
                    "priority": decision['priority'],
                    "assigned_team": decision['assigned_team'],
                    "needs_review": decision['needs_human_review']
                },
                "confidence_score": decision['confidence'],
                "timestamp": datetime.now().isoformat()
            }

            self.es.index(
                index="agent_actions",
                body=action_doc
            )
        except Exception as e:
            print(f"[WARNING] Error logging action: {e}")

def main():
    print("Support Ticket Triage Agent\n")

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
                raise ValueError("ELASTIC_PASSWORD is required when not using API key")
            es = Elasticsearch(
                os.getenv('ELASTICSEARCH_URL'),
                basic_auth=(
                    os.getenv('ELASTIC_USERNAME', 'elastic'),
                    password
                ),
                verify_certs=True
            )
    elif os.getenv('ELASTIC_CLOUD_ID') and os.getenv('ELASTIC_API_KEY'):
        es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            api_key=os.getenv('ELASTIC_API_KEY')
        )
    else:
        raise ValueError("Missing Elasticsearch configuration")

    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch")

    print("[INFO] Connected to Elasticsearch\n")

    agent = TriageAgent(es)

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    response = es.search(
        index="support_tickets",
        body={
            "query": {"term": {"status": "open"}},
            "size": 50
        }
    )

    all_tickets = [hit["_source"] for hit in response["hits"]["hits"]]
    tickets = sorted(all_tickets, key=lambda t: priority_order.get(t.get("priority", "low"), 3))[:10]

    print(f"Found {len(all_tickets)} open tickets — processing top 10 by priority\n")
    print("Queue order:")
    for i, t in enumerate(tickets, 1):
        print(f"  {i:2}. [{t.get('priority','?').upper():8}] {t['ticket_id']} - {t['subject'][:50]}")
    print()

    results = []
    for ticket in tickets:
        start_time = datetime.now()
        result = agent.triage_ticket(ticket)
        end_time = datetime.now()

        result['processing_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
        results.append(result)

    print("\n" + "="*60)
    print("TRIAGE SUMMARY")
    print("="*60)

    priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for result in results:
        p = result['triage_decision']['priority']
        priority_counts[p] = priority_counts.get(p, 0) + 1
        print(f"\nTicket {result['ticket_id']}:")
        print(f"  Category: {result['triage_decision']['category']} (confidence: {result['triage_decision']['confidence']:.1%})")
        print(f"  Priority: {result['triage_decision']['priority']}")
        print(f"  Team: {result['triage_decision']['assigned_team']}")
        print(f"  Processing time: {result['processing_time_ms']}ms")
        if result['triage_decision']['needs_human_review']:
            print(f"  [REVIEW REQUIRED] Flagged for human review")

    avg_time = sum(r['processing_time_ms'] for r in results) / len(results)
    print(f"\n{'='*60}")
    print(f"Priority Breakdown: Critical={priority_counts['critical']} | High={priority_counts['high']} | Medium={priority_counts['medium']} | Low={priority_counts['low']}")
    print(f"Average processing time: {avg_time:.0f}ms")
    print(f"[SUCCESS] {len(results)} tickets triaged successfully!")

if __name__ == "__main__":
    main()
