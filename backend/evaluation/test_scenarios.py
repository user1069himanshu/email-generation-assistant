"""
10 test scenarios for the Email Generation Assistant evaluation.

Each scenario contains:
  id             : unique integer
  intent         : core purpose of the email
  facts          : list of key facts the email must include
  tone           : desired tone
  reference_email: human-written ideal output (ground truth)
"""

SCENARIOS = [
    {
        "id": 1,
        "intent": "Follow up after a sales meeting",
        "facts": [
            "Meeting was on April 10",
            "Discussed pricing for 50 software licences",
            "Product name is DataFlow Pro",
            "Next step is to send a formal proposal by April 17",
        ],
        "tone": "formal",
        "reference_email": """Subject: Follow-Up — DataFlow Pro Proposal

Dear [Name],

Thank you for taking the time to meet with us on April 10th to discuss DataFlow Pro. \
It was a pleasure walking you through the platform and exploring how it could serve your team.

As discussed, I will have the formal proposal for 50 licences ready and sent to you by \
April 17th. The document will include detailed pricing, implementation timelines, and \
support options tailored to your requirements.

Please do not hesitate to reach out in the meantime if you have any questions.

Kind regards,
[Your Name]""",
    },
    {
        "id": 2,
        "intent": "Apologise to a client for a project delay",
        "facts": [
            "Original deadline was March 31",
            "New delivery date is April 21",
            "Delay caused by unexpected server migration issues",
            "Client name is Priya Sharma at NovaTech",
        ],
        "tone": "empathetic",
        "reference_email": """Subject: Sincere Apology — Project Delivery Update

Dear Priya,

I wanted to reach out personally to sincerely apologise for the delay in delivering \
your project. We had originally committed to a March 31st deadline, and I fully \
understand how disruptive a change like this can be.

The delay was caused by unexpected complications during a critical server migration — \
an issue we are working hard to ensure does not recur. We now have a clear path forward \
and are confident that your project will be delivered by April 21st.

Your trust means a great deal to us at NovaTech, and I appreciate your patience \
and understanding. Please feel free to call me directly if you would like to discuss \
this further.

Warm regards,
[Your Name]""",
    },
    {
        "id": 3,
        "intent": "Cold outreach to a potential business partner",
        "facts": [
            "Company name is GreenLeaf Logistics",
            "Proposing a co-marketing partnership",
            "Both companies target the same SME audience",
            "Requesting a 30-minute exploratory call",
        ],
        "tone": "casual",
        "reference_email": """Subject: Partnership Idea — GreenLeaf × [Your Company]

Hi [Name],

Hope you're having a great week! I've been following GreenLeaf Logistics for a while \
and I think there's a really interesting opportunity for us to collaborate.

We both serve the same SME audience, and I think a co-marketing partnership could be \
a win-win — combining our reach to help both our customer bases get more value. I'd love \
to explore what that could look like together.

Would you be up for a quick 30-minute call sometime this week or next? Happy to work \
around your schedule.

Cheers,
[Your Name]""",
    },
    {
        "id": 4,
        "intent": "Request information urgently before a board meeting",
        "facts": [
            "Board meeting is tomorrow at 10 AM",
            "Need Q1 financial summary from the finance team",
            "Report must include revenue, expenses, and net margin",
            "Send to board.prep@company.com by 6 PM today",
        ],
        "tone": "urgent",
        "reference_email": """Subject: URGENT: Q1 Financial Summary Needed by 6 PM Today

Hi Finance Team,

I need your immediate assistance ahead of tomorrow's board meeting at 10 AM.

Please prepare and send the Q1 financial summary — covering revenue, expenses, and \
net margin — to board.prep@company.com no later than 6 PM today. This information \
is critical for the board pack and cannot be delayed.

Thank you for your prompt attention to this.

[Your Name]""",
    },
    {
        "id": 5,
        "intent": "Thank you email after a job interview",
        "facts": [
            "Interview was for the Senior Product Manager role",
            "Interviewed with Rajiv Mehra and the product team",
            "Discussed the company's 2025 roadmap",
            "Expressed strong interest in the AI features initiative",
        ],
        "tone": "warm",
        "reference_email": """Subject: Thank You — Senior Product Manager Interview

Dear Rajiv,

Thank you so much for the opportunity to meet with you and the product team yesterday. \
I really enjoyed our conversation and came away even more excited about what you're \
building.

Hearing about the 2025 roadmap — and particularly the AI features initiative — was \
genuinely inspiring. I believe my background aligns well with the direction the team \
is heading, and I would be thrilled to contribute to that work as your Senior Product Manager.

Thank you again for your time and consideration. I look forward to hearing from you.

With warm regards,
[Your Name]""",
    },
    {
        "id": 6,
        "intent": "Announce a new company-wide remote work policy",
        "facts": [
            "New policy effective from May 1",
            "Employees can work remotely up to 3 days per week",
            "In-office days are Tuesday and Thursday",
            "Policy document available on the intranet under HR > Policies",
        ],
        "tone": "neutral",
        "reference_email": """Subject: Updated Remote Work Policy — Effective May 1

Dear All,

I am writing to share an update to our company-wide remote work policy, which will \
take effect from 1 May.

Going forward, employees may work remotely for up to three days per week. \
All team members are expected to be in the office on Tuesdays and Thursdays.

The full policy document is available on the intranet under HR > Policies. \
Please take a moment to review it and reach out to the HR team if you have any questions.

Best regards,
[Your Name]""",
    },
    {
        "id": 7,
        "intent": "Request a meeting with a senior executive",
        "facts": [
            "Executive is the CTO, Dr. Anita Roy",
            "Topic is discussing AI adoption strategy",
            "Requesting a 20-minute slot in the next two weeks",
            "Available Monday to Wednesday mornings",
        ],
        "tone": "formal",
        "reference_email": """Subject: Meeting Request — AI Adoption Strategy

Dear Dr. Roy,

I hope this message finds you well. I am writing to kindly request a brief 20-minute \
meeting at your convenience to discuss our AI adoption strategy and explore how we \
might accelerate progress in this area.

I am available any morning from Monday to Wednesday over the next two weeks and am \
happy to work entirely around your schedule.

Thank you for your time and consideration. I look forward to the opportunity to connect.

Yours sincerely,
[Your Name]""",
    },
    {
        "id": 8,
        "intent": "Send a project status update to stakeholders",
        "facts": [
            "Project name: Phoenix Platform Relaunch",
            "Currently 80% complete",
            "On track to meet the June 15 launch date",
            "Remaining work: QA testing and final UAT sign-off",
        ],
        "tone": "professional",
        "reference_email": """Subject: Project Update — Phoenix Platform Relaunch (Week 15)

Dear Stakeholders,

I am pleased to share the latest update on the Phoenix Platform Relaunch.

The project is progressing well and is currently 80% complete. We remain on track \
to meet our target launch date of June 15th. The remaining work includes final QA \
testing and UAT sign-off, both of which are underway and on schedule.

I will continue to provide weekly updates and will flag immediately if any issues arise.

Thank you for your continued support.

Best regards,
[Your Name]""",
    },
    {
        "id": 9,
        "intent": "Negotiate a better rate with a vendor",
        "facts": [
            "Vendor is CloudHost Solutions",
            "Current annual contract is $48,000",
            "Requesting a 15% discount to $40,800",
            "Have been a customer for 4 years",
        ],
        "tone": "formal",
        "reference_email": """Subject: Contract Renewal Discussion — Rate Review Request

Dear CloudHost Solutions Team,

As we approach our annual contract renewal, I would like to take this opportunity \
to discuss our pricing arrangement.

We have been a loyal customer of CloudHost Solutions for four years and have greatly \
valued the reliability and quality of your service. Our current annual contract stands \
at $48,000. In light of our long-standing relationship, I would like to respectfully \
request a 15% reduction, bringing the revised figure to $40,800 for the upcoming term.

I believe this adjustment reflects a partnership that is mutually beneficial and that \
we can build on for years to come. I welcome the opportunity to discuss this further \
at your convenience.

Yours sincerely,
[Your Name]""",
    },
    {
        "id": 10,
        "intent": "Onboard a new team member and make them feel welcome",
        "facts": [
            "New hire name is James Okonkwo",
            "Joining as a Data Scientist on April 28",
            "Will be part of the Analytics Guild team",
            "Buddy assigned is Meera Nair",
        ],
        "tone": "warm",
        "reference_email": """Subject: Welcome to the Team, James! 🎉

Hi James,

We are so excited to welcome you to the Analytics Guild as our newest Data Scientist — \
your start date of April 28th can't come soon enough!

To help you settle in, we've paired you with Meera Nair as your buddy. Meera is \
brilliant and knows the ropes inside out — she'll be your go-to person for any \
questions during your first few weeks.

We have a lot of great things planned and can't wait for you to be part of it. \
If there's anything you need before your first day, please don't hesitate to reach out.

See you on the 28th!

Warm regards,
[Your Name]""",
    },
]
