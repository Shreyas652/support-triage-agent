"""
Data Generator for Support Ticket Triage Agent
Generates realistic synthetic support tickets and related data
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class SupportDataGenerator:
    """Generate synthetic support ticket data"""
    
    # Ticket templates by category
    TICKET_TEMPLATES = {
        "technical": [
            {
                "subject": "Cannot login to account",
                "description": "I'm trying to log into my account but keep getting an error message saying 'Invalid credentials' even though I'm sure my password is correct. This started happening after the recent update.",
                "tags": ["login", "authentication", "account-access"],
                "urgency_keywords": ["cannot", "error", "not working"]
            },
            {
                "subject": "Application crashes when uploading files",
                "description": "Every time I try to upload a file larger than 10MB, the application crashes completely. I've tried different browsers but the issue persists. This is blocking my work.",
                "tags": ["crash", "upload", "file-handling"],
                "urgency_keywords": ["crashes", "blocking", "completely"]
            },
            {
                "subject": "API integration not working",
                "description": "Our API integration stopped working this morning. We're getting 500 errors on all endpoints. This is affecting our production system.",
                "tags": ["api", "integration", "production"],
                "urgency_keywords": ["stopped working", "production", "affecting"]
            },
            {
                "subject": "Slow performance when loading dashboard",
                "description": "The dashboard is taking 30+ seconds to load. It used to be instant. This happens consistently across all pages.",
                "tags": ["performance", "dashboard", "slow"],
                "urgency_keywords": ["slow", "taking too long"]
            },
            {
                "subject": "Data sync issue between devices",
                "description": "My data isn't syncing between my desktop and mobile app. Changes I make on desktop don't appear on mobile after several hours.",
                "tags": ["sync", "mobile", "data"],
                "urgency_keywords": ["not syncing", "don't appear"]
            }
        ],
        "billing": [
            {
                "subject": "Charged twice for subscription",
                "description": "I was charged twice this month for my subscription. Can you please refund one of the charges? My card ending in 1234 was charged $99 twice on the same day.",
                "tags": ["billing", "duplicate-charge", "refund"],
                "urgency_keywords": ["charged twice", "refund"]
            },
            {
                "subject": "Unable to update payment method",
                "description": "I'm trying to update my credit card information but the form won't save. I get an error saying 'Payment method invalid' but the card works everywhere else.",
                "tags": ["payment", "credit-card", "update"],
                "urgency_keywords": ["unable", "won't save", "error"]
            },
            {
                "subject": "Need invoice for last month",
                "description": "Could you please send me an invoice for last month's payment? I need it for my expense report.",
                "tags": ["invoice", "receipt", "documentation"],
                "urgency_keywords": []
            },
            {
                "subject": "Subscription cancelled but still charged",
                "description": "I cancelled my subscription two weeks ago but was still charged today. Please cancel immediately and refund the charge.",
                "tags": ["cancellation", "refund", "billing"],
                "urgency_keywords": ["still charged", "immediately"]
            },
            {
                "subject": "Want to upgrade to Enterprise plan",
                "description": "We'd like to upgrade from Business to Enterprise. What's the process and can we get a quote for 50 users?",
                "tags": ["upgrade", "enterprise", "quote"],
                "urgency_keywords": []
            }
        ],
        "account": [
            {
                "subject": "Cannot reset password",
                "description": "I've tried to reset my password multiple times but never receive the reset email. I've checked spam and it's not there either.",
                "tags": ["password", "reset", "email"],
                "urgency_keywords": ["cannot", "never receive"]
            },
            {
                "subject": "Need to change account email",
                "description": "I no longer have access to the email associated with my account. How can I change it to my new email address?",
                "tags": ["email", "account-settings", "access"],
                "urgency_keywords": ["no longer have access"]
            },
            {
                "subject": "Account locked after too many login attempts",
                "description": "My account got locked because I entered the wrong password too many times. How can I unlock it?",
                "tags": ["locked", "account-security", "login"],
                "urgency_keywords": ["locked"]
            },
            {
                "subject": "Want to delete my account",
                "description": "I'd like to delete my account and all associated data. Please provide instructions on how to do this.",
                "tags": ["deletion", "privacy", "data"],
                "urgency_keywords": []
            },
            {
                "subject": "Need to add team members",
                "description": "How do I add new team members to our account? I can't find the option in settings.",
                "tags": ["team", "users", "settings"],
                "urgency_keywords": ["can't find"]
            }
        ],
        "feature": [
            {
                "subject": "Request: Dark mode support",
                "description": "It would be great if you could add a dark mode option. The current bright interface is hard on the eyes during late-night work sessions.",
                "tags": ["feature-request", "ui", "dark-mode"],
                "urgency_keywords": []
            },
            {
                "subject": "Feature request: Export data to CSV",
                "description": "Please add the ability to export our data to CSV format. This would help us with external reporting and analysis.",
                "tags": ["feature-request", "export", "csv"],
                "urgency_keywords": []
            },
            {
                "subject": "Suggestion: Mobile app notifications",
                "description": "The mobile app should send push notifications for important events. Currently, I have to open the app to check for updates.",
                "tags": ["feature-request", "mobile", "notifications"],
                "urgency_keywords": []
            },
            {
                "subject": "Need integration with Slack",
                "description": "Do you have plans to integrate with Slack? It would be very helpful to receive notifications in our team channel.",
                "tags": ["feature-request", "integration", "slack"],
                "urgency_keywords": []
            },
            {
                "subject": "Request: Bulk actions",
                "description": "It would save a lot of time if we could perform actions on multiple items at once instead of one by one.",
                "tags": ["feature-request", "bulk-actions", "efficiency"],
                "urgency_keywords": []
            }
        ]
    }
    
    # Customer plans and their characteristics
    CUSTOMER_PLANS = {
        "free": {"priority_multiplier": 0.5, "sla_hours": 72},
        "pro": {"priority_multiplier": 1.0, "sla_hours": 24},
        "business": {"priority_multiplier": 1.5, "sla_hours": 12},
        "enterprise": {"priority_multiplier": 2.0, "sla_hours": 4}
    }
    
    # Sentiment indicators
    SENTIMENT_PATTERNS = {
        "positive": ["thanks", "appreciate", "great", "love", "excellent", "helpful"],
        "neutral": ["need", "how", "can you", "please", "would like", "question"],
        "negative": ["frustrated", "angry", "disappointed", "terrible", "worst", "unacceptable", "immediately"]
    }
    
    def __init__(self):
        self.customers = []
        self.tickets = []
        self.kb_articles = []
        
    def generate_customers(self, count: int = 100) -> List[Dict]:
        """Generate synthetic customer data"""
        customers = []
        
        for i in range(count):
            customer_id = f"CUST-{str(i+1).zfill(4)}"
            plan = random.choice(list(self.CUSTOMER_PLANS.keys()))
            
            customer = {
                "customer_id": customer_id,
                "email": f"customer{i+1}@example.com",
                "name": f"Customer {i+1}",
                "plan": plan,
                "signup_date": (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                "total_tickets": random.randint(0, 20),
                "satisfaction_score": round(random.uniform(3.0, 5.0), 1)
            }
            customers.append(customer)
        
        self.customers = customers
        return customers
    
    def generate_tickets(self, count: int = 500) -> List[Dict]:
        """Generate synthetic support tickets"""
        tickets = []
        
        if not self.customers:
            self.generate_customers()
        
        for i in range(count):
            # Select random category and template
            category = random.choice(list(self.TICKET_TEMPLATES.keys()))
            template = random.choice(self.TICKET_TEMPLATES[category])
            
            # Select random customer
            customer = random.choice(self.customers)
            
            # Determine sentiment
            sentiment = self._determine_sentiment(template["description"])
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(
                template["urgency_keywords"],
                sentiment,
                customer["plan"]
            )
            
            # Determine status (mostly open, some resolved)
            status_weights = [0.6, 0.2, 0.15, 0.05]  # open, in_progress, resolved, closed
            status = random.choices(
                ["open", "in_progress", "resolved", "closed"],
                weights=status_weights
            )[0]
            
            # Create ticket
            created_at = datetime.now() - timedelta(
                hours=random.randint(0, 168)  # Last 7 days
            )
            
            ticket = {
                "ticket_id": f"TICK-{str(i+1).zfill(5)}",
                "subject": template["subject"],
                "description": template["description"],
                "customer_id": customer["customer_id"],
                "customer_email": customer["email"],
                "customer_plan": customer["plan"],
                "status": status,
                "category": category,
                "priority": self._calculate_priority(urgency_score),
                "assigned_team": self._determine_team(category),
                "assigned_to": f"agent_{random.randint(1, 5)}" if status != "open" else None,
                "sentiment": sentiment,
                "urgency_score": urgency_score,
                "created_at": created_at.isoformat(),
                "updated_at": (created_at + timedelta(hours=random.randint(0, 12))).isoformat(),
                "resolved_at": (created_at + timedelta(hours=random.randint(1, 48))).isoformat() if status in ["resolved", "closed"] else None,
                "tags": template["tags"],
                "resolution_time_minutes": random.randint(15, 240) if status in ["resolved", "closed"] else None
            }
            
            tickets.append(ticket)
        
        self.tickets = tickets
        return tickets
    
    def generate_kb_articles(self, count: int = 50) -> List[Dict]:
        """Generate knowledge base articles"""
        articles = []
        
        article_templates = [
            {"title": "How to reset your password", "category": "account", "tags": ["password", "reset", "login"]},
            {"title": "Troubleshooting login issues", "category": "technical", "tags": ["login", "authentication", "troubleshooting"]},
            {"title": "Understanding your billing cycle", "category": "billing", "tags": ["billing", "subscription", "payment"]},
            {"title": "How to update payment information", "category": "billing", "tags": ["payment", "credit-card", "update"]},
            {"title": "Adding team members to your account", "category": "account", "tags": ["team", "users", "collaboration"]},
            {"title": "Uploading large files", "category": "technical", "tags": ["upload", "files", "storage"]},
            {"title": "API authentication guide", "category": "technical", "tags": ["api", "authentication", "integration"]},
            {"title": "Cancelling your subscription", "category": "billing", "tags": ["cancellation", "subscription", "billing"]},
            {"title": "Exporting your data", "category": "technical", "tags": ["export", "data", "backup"]},
            {"title": "Account security best practices", "category": "account", "tags": ["security", "password", "2fa"]},
        ]
        
        for i, template in enumerate(article_templates):
            article = {
                "article_id": f"KB-{str(i+1).zfill(3)}",
                "title": template["title"],
                "content": f"This is a comprehensive guide about {template['title'].lower()}. Step-by-step instructions with screenshots and troubleshooting tips.",
                "category": template["category"],
                "tags": template["tags"],
                "view_count": random.randint(100, 5000),
                "helpful_count": random.randint(10, 500),
                "updated_at": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            }
            articles.append(article)
        
        self.kb_articles = articles
        return articles
    
    def _determine_sentiment(self, text: str) -> str:
        """Determine sentiment from text"""
        text_lower = text.lower()
        
        negative_count = sum(1 for word in self.SENTIMENT_PATTERNS["negative"] if word in text_lower)
        positive_count = sum(1 for word in self.SENTIMENT_PATTERNS["positive"] if word in text_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > 0:
            return "positive"
        else:
            return "neutral"
    
    def _calculate_urgency_score(self, keywords: List[str], sentiment: str, plan: str) -> int:
        """Calculate urgency score (0-100)"""
        base_score = len(keywords) * 15
        
        # Sentiment modifier
        if sentiment == "negative":
            base_score += 20
        elif sentiment == "positive":
            base_score -= 10
        
        # Plan modifier
        plan_multiplier = self.CUSTOMER_PLANS[plan]["priority_multiplier"]
        base_score = int(base_score * plan_multiplier)
        
        # Cap at 100
        return min(base_score, 100)
    
    def _calculate_priority(self, urgency_score: int) -> str:
        """Convert urgency score to priority level"""
        if urgency_score >= 75:
            return "critical"
        elif urgency_score >= 50:
            return "high"
        elif urgency_score >= 25:
            return "medium"
        else:
            return "low"
    
    def _determine_team(self, category: str) -> str:
        """Determine appropriate team based on category"""
        team_mapping = {
            "technical": "engineering",
            "billing": "billing",
            "account": "success",
            "feature": "product"
        }
        return team_mapping.get(category, "support")
    
    def save_to_files(self, output_dir: str = "data"):
        """Save generated data to JSON files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save customers
        with open(f"{output_dir}/customers.json", "w") as f:
            json.dump(self.customers, f, indent=2)
        
        # Save tickets
        with open(f"{output_dir}/tickets.json", "w") as f:
            json.dump(self.tickets, f, indent=2)
        
        # Save KB articles
        with open(f"{output_dir}/kb_articles.json", "w") as f:
            json.dump(self.kb_articles, f, indent=2)
        
        print(f"✅ Generated data saved to {output_dir}/")
        print(f"   - {len(self.customers)} customers")
        print(f"   - {len(self.tickets)} tickets")
        print(f"   - {len(self.kb_articles)} KB articles")


def main():
    """Generate and save all data"""
    print("🔧 Generating synthetic support data...")
    
    generator = SupportDataGenerator()
    
    # Generate data
    customers = generator.generate_customers(100)
    tickets = generator.generate_tickets(500)
    kb_articles = generator.generate_kb_articles(50)
    
    # Save to files
    generator.save_to_files()
    
    # Print summary statistics
    print("\n📊 Data Summary:")
    print(f"Customers by plan:")
    plan_counts = {}
    for c in customers:
        plan_counts[c["plan"]] = plan_counts.get(c["plan"], 0) + 1
    for plan, count in sorted(plan_counts.items()):
        print(f"  - {plan}: {count}")
    
    print(f"\nTickets by category:")
    category_counts = {}
    for t in tickets:
        category_counts[t["category"]] = category_counts.get(t["category"], 0) + 1
    for category, count in sorted(category_counts.items()):
        print(f"  - {category}: {count}")
    
    print(f"\nTickets by priority:")
    priority_counts = {}
    for t in tickets:
        priority_counts[t["priority"]] = priority_counts.get(t["priority"], 0) + 1
    for priority, count in sorted(priority_counts.items()):
        print(f"  - {priority}: {count}")


if __name__ == "__main__":
    main()
