import random
import json
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class SupportDataGenerator:
    
    TICKET_TEMPLATES = {
: [
            {
: "Cannot login to account",
: "I'm trying to log into my account but keep getting an error message saying 'Invalid credentials' even though I'm sure my password is correct. This started happening after the recent update.",
: ["login", "authentication", "account-access"],
: ["cannot", "error", "not working"]
            },
            {
: "Application crashes when uploading files",
: "Every time I try to upload a file larger than 10MB, the application crashes completely. I've tried different browsers but the issue persists. This is blocking my work.",
: ["crash", "upload", "file-handling"],
: ["crashes", "blocking", "completely"]
            },
            {
: "API integration not working",
: "Our API integration stopped working this morning. We're getting 500 errors on all endpoints. This is affecting our production system.",
: ["api", "integration", "production"],
: ["stopped working", "production", "affecting"]
            },
            {
: "Slow performance when loading dashboard",
: "The dashboard is taking 30+ seconds to load. It used to be instant. This happens consistently across all pages.",
: ["performance", "dashboard", "slow"],
: ["slow", "taking too long"]
            },
            {
: "Data sync issue between devices",
: "My data isn't syncing between my desktop and mobile app. Changes I make on desktop don't appear on mobile after several hours.",
: ["sync", "mobile", "data"],
: ["not syncing", "don't appear"]
            }
        ],
: [
            {
: "Charged twice for subscription",
: "I was charged twice this month for my subscription. Can you please refund one of the charges? My card ending in 1234 was charged $99 twice on the same day.",
: ["billing", "duplicate-charge", "refund"],
: ["charged twice", "refund"]
            },
            {
: "Unable to update payment method",
: "I'm trying to update my credit card information but the form won't save. I get an error saying 'Payment method invalid' but the card works everywhere else.",
: ["payment", "credit-card", "update"],
: ["unable", "won't save", "error"]
            },
            {
: "Need invoice for last month",
: "Could you please send me an invoice for last month's payment? I need it for my expense report.",
: ["invoice", "receipt", "documentation"],
: []
            },
            {
: "Subscription cancelled but still charged",
: "I cancelled my subscription two weeks ago but was still charged today. Please cancel immediately and refund the charge.",
: ["cancellation", "refund", "billing"],
: ["still charged", "immediately"]
            },
            {
: "Want to upgrade to Enterprise plan",
: "We'd like to upgrade from Business to Enterprise. What's the process and can we get a quote for 50 users?",
: ["upgrade", "enterprise", "quote"],
: []
            }
        ],
: [
            {
: "Cannot reset password",
: "I've tried to reset my password multiple times but never receive the reset email. I've checked spam and it's not there either.",
: ["password", "reset", "email"],
: ["cannot", "never receive"]
            },
            {
: "Need to change account email",
: "I no longer have access to the email associated with my account. How can I change it to my new email address?",
: ["email", "account-settings", "access"],
: ["no longer have access"]
            },
            {
: "Account locked after too many login attempts",
: "My account got locked because I entered the wrong password too many times. How can I unlock it?",
: ["locked", "account-security", "login"],
: ["locked"]
            },
            {
: "Want to delete my account",
: "I'd like to delete my account and all associated data. Please provide instructions on how to do this.",
: ["deletion", "privacy", "data"],
: []
            },
            {
: "Need to add team members",
: "How do I add new team members to our account? I can't find the option in settings.",
: ["team", "users", "settings"],
: ["can't find"]
            }
        ],
: [
            {
: "Request: Dark mode support",
: "It would be great if you could add a dark mode option. The current bright interface is hard on the eyes during late-night work sessions.",
: ["feature-request", "ui", "dark-mode"],
: []
            },
            {
: "Feature request: Export data to CSV",
: "Please add the ability to export our data to CSV format. This would help us with external reporting and analysis.",
: ["feature-request", "export", "csv"],
: []
            },
            {
: "Suggestion: Mobile app notifications",
: "The mobile app should send push notifications for important events. Currently, I have to open the app to check for updates.",
: ["feature-request", "mobile", "notifications"],
: []
            },
            {
: "Need integration with Slack",
: "Do you have plans to integrate with Slack? It would be very helpful to receive notifications in our team channel.",
: ["feature-request", "integration", "slack"],
: []
            },
            {
: "Request: Bulk actions",
: "It would save a lot of time if we could perform actions on multiple items at once instead of one by one.",
: ["feature-request", "bulk-actions", "efficiency"],
: []
            }
        ]
    }
    
    CUSTOMER_PLANS = {
: {"priority_multiplier": 0.5, "sla_hours": 72},
: {"priority_multiplier": 1.0, "sla_hours": 24},
: {"priority_multiplier": 1.5, "sla_hours": 12},
: {"priority_multiplier": 2.0, "sla_hours": 4}
    }
    
    SENTIMENT_PATTERNS = {
: ["thanks", "appreciate", "great", "love", "excellent", "helpful"],
: ["need", "how", "can you", "please", "would like", "question"],
: ["frustrated", "angry", "disappointed", "terrible", "worst", "unacceptable", "immediately"]
    }
    
    def __init__(self):
        self.customers = []
        self.tickets = []
        self.kb_articles = []
        
    def generate_customers(self, count: int = 100) -> List[Dict]:
        
        customers = []
        
        for i in range(count):
            customer_id = f"CUST-{str(i+1).zfill(4)}"
            plan = random.choice(list(self.CUSTOMER_PLANS.keys()))
            
            customer = {
: customer_id,
: f"customer{i+1}@example.com",
: f"Customer {i+1}",
: plan,
: (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
: random.randint(0, 20),
: round(random.uniform(3.0, 5.0), 1)
            }
            customers.append(customer)
        
        self.customers = customers
        return customers
    
    def generate_tickets(self, count: int = 500) -> List[Dict]:
        
        tickets = []
        
        if not self.customers:
            self.generate_customers()
        
        for i in range(count):
                                                 
            category = random.choice(list(self.TICKET_TEMPLATES.keys()))
            template = random.choice(self.TICKET_TEMPLATES[category])
            
            customer = random.choice(self.customers)
            
            sentiment = self._determine_sentiment(template["description"])
            
            urgency_score = self._calculate_urgency_score(
                template["urgency_keywords"],
                sentiment,
                customer["plan"]
            )
            
            status_weights = [0.6, 0.2, 0.15, 0.05]                                       
            status = random.choices(
                ["open", "in_progress", "resolved", "closed"],
                weights=status_weights
            )[0]
            
            created_at = datetime.now() - timedelta(
                hours=random.randint(0, 2160)                
            )
            
            ticket = {
: f"TICK-{str(i+1).zfill(5)}",
: template["subject"],
: template["description"],
: customer["customer_id"],
: customer["email"],
: customer["plan"],
: status,
: category,
: self._calculate_priority(urgency_score),
: self._determine_team(category),
: f"agent_{random.randint(1, 5)}" if status != "open" else None,
: sentiment,
: urgency_score,
: created_at.isoformat(),
: (created_at + timedelta(hours=random.randint(0, 12))).isoformat(),
: (created_at + timedelta(hours=random.randint(1, 48))).isoformat() if status in ["resolved", "closed"] else None,
: template["tags"],
: random.randint(15, 240) if status in ["resolved", "closed"] else None
            }
            
            tickets.append(ticket)
        
        self.tickets = tickets
        return tickets
    
    def generate_kb_articles(self, count: int = 50) -> List[Dict]:
        
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
: f"KB-{str(i+1).zfill(3)}",
: template["title"],
: f"This is a comprehensive guide about {template['title'].lower()}. Step-by-step instructions with screenshots and troubleshooting tips.",
: template["category"],
: template["tags"],
: random.randint(100, 5000),
: random.randint(10, 500),
: (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            }
            articles.append(article)
        
        self.kb_articles = articles
        return articles
    
    def _determine_sentiment(self, text: str) -> str:
        
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
        
        base_score = len(keywords) * 15
        
        if sentiment == "negative":
            base_score += 20
        elif sentiment == "positive":
            base_score -= 10
        
        plan_multiplier = self.CUSTOMER_PLANS[plan]["priority_multiplier"]
        base_score = int(base_score * plan_multiplier)
        
        return min(base_score, 100)
    
    def _calculate_priority(self, urgency_score: int) -> str:
        
        if urgency_score >= 75:
            return "critical"
        elif urgency_score >= 50:
            return "high"
        elif urgency_score >= 25:
            return "medium"
        else:
            return "low"
    
    def _determine_team(self, category: str) -> str:
        
        team_mapping = {
: "engineering",
: "billing",
: "success",
: "product"
        }
        return team_mapping.get(category, "support")
    
    def save_to_files(self, output_dir: str = "data"):
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f"{output_dir}/customers.json", "w") as f:
            json.dump(self.customers, f, indent=2)
        
        with open(f"{output_dir}/tickets.json", "w") as f:
            json.dump(self.tickets, f, indent=2)
        
        with open(f"{output_dir}/kb_articles.json", "w") as f:
            json.dump(self.kb_articles, f, indent=2)
        
        print(f"✅ Generated data saved to {output_dir}/")
        print(f"   - {len(self.customers)} customers")
        print(f"   - {len(self.tickets)} tickets")
        print(f"   - {len(self.kb_articles)} KB articles")

def main():
    
    print("🔧 Generating synthetic support data...")
    
    generator = SupportDataGenerator()
    
    customers = generator.generate_customers(100)
    tickets = generator.generate_tickets(500)
    kb_articles = generator.generate_kb_articles(50)
    
    generator.save_to_files()
    
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
