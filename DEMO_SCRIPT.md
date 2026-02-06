# 🎬 Demo Video Script - Intelligent Support Ticket Triage Agent

**Total Duration**: 3:00 minutes

---

## INTRO SCREEN (0:00-0:05)
**Visual**: Title card with logo animation
**Text on screen**:
```
Intelligent Support Ticket Triage Agent
Elasticsearch Agent Builder Hackathon 2026
```

**Voiceover**: "This is the Intelligent Support Ticket Triage Agent—an AI-powered solution that transforms support operations."

---

## SCENE 1: THE PROBLEM (0:05-0:35)

### Screen Recording (0:05-0:20)
**Visual**: Show inbox with 500 unprocessed tickets, scrolling

**Voiceover**: "Every day, support teams face hundreds of tickets. Each one needs manual review—reading the content, categorizing it as technical, billing, account, or feature request, setting priority from critical to low, and routing to the right team."

**Show**: Someone manually clicking through tickets, taking notes

### Metrics Overlay (0:20-0:35)
**Visual**: Statistics appearing on screen
```
Manual Triage Process:
• 500 tickets per day
• 2-3 minutes per ticket
• 16-25 hours of human time daily
• 15% error rate
• 4-6 hour response delay
```

**Voiceover**: "This takes two to three minutes per ticket—that's 16 to 25 hours of human time daily. With a 15% error rate and four to six hour response delays, both teams and customers suffer."

---

## SCENE 2: THE SOLUTION IN ACTION (0:35-2:00)

### Agent Demo - Ticket 1 (0:35-1:05)
**Visual**: Terminal showing live agent execution

**Show new ticket arriving**:
```
Subject: Cannot access billing section after update
Description: I'm unable to access my billing information since this morning's update. 
Getting an error message. I need to update my payment method urgently.
Customer: Enterprise plan (CUST-0042)
```

**Voiceover**: "Watch the agent in action. A new ticket arrives—a customer can't access their billing section after an update."

**Show agent processing steps with timestamps**:

**Step 1 - Content Analysis (0:40)**
```
📝 Analyzing content...
   Sentiment: negative
   Urgency keywords: 3 found ("unable", "error", "urgently")
   Customer tier: Enterprise
```

**Step 2 - Search Tool (0:45)**
```
🔍 Search Tool - Finding context...
   ✓ Found 5 similar resolved tickets
   ✓ Found 3 relevant KB articles
   ✓ Customer history: 2 previous tickets (both resolved)
```

**Step 3 - ES|QL Tool (0:50)**
```
📊 ES|QL Tool - Analyzing patterns...
   Priority score calculation:
     Base urgency: +45
     Negative sentiment: +20
     Enterprise customer: ×2.0
   = Priority Score: 90/100
   
   Category: billing (95% confidence)
   Team workload: Billing team has 12 open tickets
```

**Step 4 - Decision (0:55)**
```
🧠 Agent Decision:
   Category: billing
   Priority: CRITICAL
   Team: Billing Team
   Confidence: 95%
```

**Step 5 - Workflow (1:00)**
```
⚙️ Executing workflows...
   ✓ Updated ticket fields
   ✓ Assigned to Billing Team
   ✓ Sent high-priority Slack alert
   ✓ Logged to audit trail
   
Processing time: 1.2 seconds
```

**Voiceover**: "The agent analyzes sentiment and urgency, searches for similar past tickets and KB articles, uses ES|QL to calculate a priority score, makes an intelligent decision with 95% confidence, and executes automated workflows—all in 1.2 seconds."

### Agent Demo - Ticket 2 (1:05-1:30)
**Visual**: Show second example with different outcome

**Show ticket**:
```
Subject: Feature request - Dark mode support
Description: It would be great if you could add a dark mode option.
Customer: Free plan (CUST-0078)
```

**Show rapid processing**:
```
📝 Analysis: Positive sentiment, no urgency
🔍 Search: Found 12 similar feature requests
📊 ES|QL: Priority score: 15 (Free tier, low urgency)
🧠 Decision: Category=feature, Priority=low, Team=Product
⚙️ Workflow: Added to product backlog queue

Processing time: 0.9 seconds
```

**Voiceover**: "Watch how the agent adapts. For a feature request from a free-tier customer, it correctly identifies low priority and routes to the product team. Same multi-step process, different outcome based on context."

### Multi-Step Intelligence Highlight (1:30-2:00)
**Visual**: Split screen showing both tickets side by side with decision tree

**Diagram overlay**:
```
Ticket A (Enterprise + Urgent) → Critical → Billing → Alert
Ticket B (Free + Feature)      → Low      → Product → Queue
```

**Voiceover**: "This is multi-step intelligence in action. The agent doesn't just pattern match—it searches for context, analyzes patterns with ES|QL, and adapts its decisions. Enterprise customers with urgent issues get immediate attention. Feature requests get properly queued. All automatically."

---

## SCENE 3: BEFORE/AFTER COMPARISON (2:00-2:30)

### Split Screen Comparison (2:00-2:15)
**Visual**: Side-by-side comparison

**Left side - BEFORE (Manual)**:
```
Manual Triage
⏱️ Time per ticket: 2-3 minutes
📊 Accuracy: 85%
⚠️ Error rate: 15%
🕐 Response time: 4-6 hours
💰 Daily cost: 25 hours of labor
```

**Right side - AFTER (Agent)**:
```
Agent Triage
⏱️ Time per ticket: 1-2 seconds
📊 Accuracy: 95%
✓ Error rate: 5%
⚡ Response time: < 15 minutes
💰 Daily cost: < 1 hour oversight
```

**Voiceover**: "The impact is dramatic. Processing time drops from minutes to seconds. Accuracy improves from 85% to 95%. Response time drops from hours to minutes."

### Impact Metrics (2:15-2:30)
**Visual**: Animated metrics dashboard

```
📊 IMPACT SUMMARY

Time Savings:
  99.1% faster processing
  20.7 hours saved daily
  5,163 hours saved annually

Cost Savings:
  $180,712 per year

Quality Improvements:
  67% fewer errors
  95% response time reduction
  100% audit trail coverage
```

**Voiceover**: "That's a 99% reduction in processing time, saving over five thousand hours per year. That's $180,000 in cost savings, with better accuracy and complete audit trails for every decision."

---

## SCENE 4: ARCHITECTURE & TOOLS (2:30-2:55)

### Architecture Diagram (2:30-2:45)
**Visual**: Clean architecture diagram with highlights

```
Multi-Step Agent Architecture

Input → [1] Analyze → [2] Search → [3] ES|QL → [4] Decide → [5] Workflow → Output
         Content      Tool        Tool        Reasoning   Tool
         
Agent Builder Tools:
🔍 Search  - Find similar tickets, KB articles, customer history
📊 ES|QL   - Calculate priority, analyze patterns, check workload
⚙️ Workflow - Update, assign, notify, log
```

**Voiceover**: "The agent uses all three Agent Builder tools. The Search tool finds relevant context from five hundred tickets and fifty KB articles. ES|QL analyzes patterns and calculates dynamic priority scores. Workflows execute automated actions end-to-end."

### Code Snippet (2:45-2:55)
**Visual**: Brief code highlight showing multi-step logic

```python
def triage_ticket(ticket):
    # Step 1: Analyze content
    analysis = analyze_content(ticket)
    
    # Step 2: Search for context (Search Tool)
    context = search_similar_tickets(ticket)
    context['kb'] = search_kb_articles(ticket)
    context['customer'] = get_customer_history(ticket)
    
    # Step 3: Analyze patterns (ES|QL Tool)
    priority = calculate_priority_esql(analysis, context)
    category = determine_category(context)
    
    # Step 4: Make decision
    decision = make_routing_decision(category, priority)
    
    # Step 5: Execute workflow (Workflow Tool)
    return execute_actions(ticket, decision)
```

**Voiceover**: "Every decision is explainable, logged, and can be reviewed. Low-confidence cases are flagged for human validation, ensuring we maintain high quality while automating the routine work."

---

## OUTRO (2:55-3:00)

### Call to Action Screen
**Visual**: GitHub and social links

```
🏆 Intelligent Support Ticket Triage Agent

Built with Elasticsearch Agent Builder
⭐ Star on GitHub: github.com/yourusername/triage-agent
🔗 Try it: [Demo Link]
🐦 Follow: @yourusername

#ElasticsearchHackathon #AgentBuilder
```

**Voiceover**: "Built for the Elasticsearch Agent Builder Hackathon. Check out the code on GitHub."

**Fade out with logo**

---

## 🎥 FILMING TIPS

### Recording Setup
- Use OBS Studio or similar screen recorder (1080p, 60fps)
- Enable system audio and microphone
- Test audio levels before recording

### Screen Recording Checklist
- [ ] Close unnecessary applications
- [ ] Clear terminal history
- [ ] Increase terminal font size (16-18pt)
- [ ] Use a clean, professional theme
- [ ] Prepare test data in advance
- [ ] Practice the flow 2-3 times

### Editing
- Use DaVinci Resolve (free) or similar
- Add background music (low volume, copyright-free)
- Add text overlays for key metrics
- Include smooth transitions between scenes
- Add your logo/watermark
- Export as MP4, H.264 codec, 1080p

### Music Suggestions (Copyright-Free)
- YouTube Audio Library: "Tech" category
- Epidemic Sound: "Upbeat Corporate"
- Keep volume at 10-15% to not overpower voice

### Voiceover Tips
- Speak clearly and at moderate pace
- Use an external mic if possible
- Record in a quiet room
- Edit out "umms" and long pauses
- Add subtle fade-in/fade-out

---

## 📤 UPLOAD CHECKLIST

- [ ] Video length < 3 minutes
- [ ] Uploaded to YouTube (Public or Unlisted)
- [ ] Title includes "Elasticsearch Agent Builder Hackathon"
- [ ] Description includes:
  - Project name
  - GitHub link
  - Hackathon mention
  - Tags: #Elasticsearch #AgentBuilder #Hackathon2026
- [ ] Thumbnail created (1280x720px)
- [ ] Captions/subtitles added (accessibility)

---

**Good luck with your submission! 🚀**
