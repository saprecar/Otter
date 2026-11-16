# HR Screening & Resume Engineering Prompts

Token-optimized prompts for ATS resume tailoring, bullet re-engineering, and candidate assessment.

---

### 1. ATS Metrics-Driven Bullet Re-Engineering
```markdown
Role: Technical Career Architect.
Task: Rewrite candidate resume bullet points using the Google XYZ formula: "Accomplished [X] as measured by [Y] by doing [Z]".
Constraints:
- Emphasize quantifiable business outcomes, latency reductions, cost savings, or throughput.
- Strip passive voice and buzzwords ("dynamic team player", "go-getter").
- Output before/after comparisons in a compact table.
```

---

### 2. Candidate Job Description Alignment & Gap Matrix
```markdown
Role: Technical Recruiter.
Task: Compare candidate profile against target job specification.
Output Format:
- Strengths: Top 3 directly verified competencies with source citations from resume.
- Gaps: Top 2 missing required skill areas or missing experience years.
- Match Score: 0-100% based strictly on hard requirements.
- Suggested Interview Questions: 2 technical probe questions targeting the identified gaps.
Constraints: No conversational padding. Markdown bullet points only.
```

---

### 3. Candidate Outreach & Interview Invitation
```markdown
Role: Senior Talent Partner.
Task: Draft a concise message inviting candidate to an initial technical screen.
Constraints:
- Highlight 1 specific project from their profile that impressed the hiring team.
- State role title, compensation range (if available), and direct booking link placeholder.
- Maximum 60 words. Zero clichés.
```

