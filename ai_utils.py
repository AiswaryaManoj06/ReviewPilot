import json
import os
import google.generativeai as genai


def configure_ai():
    """Configure the Gemini AI client."""
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in your .env file."
        )
    genai.configure(api_key=api_key)


REVIEW_PROMPT_TEMPLATE = """You are an expert senior software engineer performing a thorough code review.
Analyze the following {input_type} and provide a comprehensive review.

Focus on these areas:
1. **Bugs & Logic Errors**: Identify potential bugs, null pointer issues, off-by-one errors, race conditions, incorrect logic.
2. **Security Vulnerabilities**: SQL injection, XSS, CSRF, hardcoded secrets, insecure configurations, input validation issues.
3. **Performance Issues**: N+1 queries, unnecessary computations, memory leaks, inefficient algorithms, missing caching opportunities.
4. **Code Quality & Maintainability**: Code smells, DRY violations, unclear naming, missing error handling, excessive complexity.
5. **Best Practices**: Design patterns, SOLID principles, proper typing, documentation gaps.

import json

CODE TO REVIEW:
```
{code}
```

You MUST respond with valid JSON only (no markdown, no code fences). Use this exact schema:
{{
  "overallRisk": "low" | "medium" | "high" | "critical",
  "riskScore": <number 0-100>,
  "summary": "<2-3 sentence overview of the code quality>",
  "statistics": {{
    "bugs": <count>,
    "security": <count>,
    "performance": <count>,
    "style": <count>,
    "total": <count>
  }},
  "issues": [
    {{
      "id": "<unique-id like BUG-001>",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "category": "bug" | "security" | "performance" | "style" | "maintainability",
      "title": "<short descriptive title>",
      "description": "<detailed explanation of the issue>",
      "codeSnippet": "<the problematic code snippet, 1-5 lines>",
      "suggestion": "<specific code fix or improvement>",
{code}
    }}
  ],
  "recommendations": [
    "<general improvement suggestion>"
  ],
  "positives": [
    "<something done well in the code>"
  ]
}}

Rules:
- Be specific and actionable. Don't be vague.
- Include code snippets in suggestions showing the fix.
- Rate severity accurately - don't over-inflate.
- If the code is good, say so. Don't invent issues.
- Always include at least 1 positive observation.
- Return between 0 and 15 issues depending on actual problems found.
- Ensure the JSON is valid and parseable.
"""


def analyze_code(code, input_type='code snippet', language=None, pr_info=None):
    """
    Analyze code using Google Gemini AI and return structured review results.

    Args:
        code: The code or diff text to analyze
        input_type: 'code snippet' or 'pull request diff'
        language: Programming language (optional)
        pr_info: PR metadata dict (optional)

    Returns:
        dict with structured review results
    """
    configure_ai()

    # Build context section
    context_parts = []
    if language:
        context_parts.append(f"Programming Language: {language}")
    if pr_info:
        context_parts.append(f"PR Title: {pr_info.get('title', 'N/A')}")
        context_parts.append(f"Author: {pr_info.get('author', 'N/A')}")
        context_parts.append(
            f"Changes: +{pr_info.get('additions', 0)} "
            f"-{pr_info.get('deletions', 0)} "
            f"across {pr_info.get('changed_files', 0)} files"
        )

    context_section = ""
    if context_parts:
        context_section = "CONTEXT:\n" + "\n".join(context_parts)

    prompt = REVIEW_PROMPT_TEMPLATE.format(
        input_type=input_type,
        code=code,
        context_section=context_section
    )

    # Use Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=4096,
            )
        )

        response_text = response.text.strip()

        # Clean up response - remove markdown code fences if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith('```')]
            response_text = '\n'.join(lines)

        review = json.loads(response_text)

        # Validate and ensure required fields
        review.setdefault('overallRisk', 'medium')
        review.setdefault('riskScore', 50)
        review.setdefault('summary', 'Review completed.')
        review.setdefault('statistics', {
            'bugs': 0, 'security': 0,
            'performance': 0, 'style': 0, 'total': 0
        })
        review.setdefault('issues', [])
        review.setdefault('recommendations', [])
        review.setdefault('positives', ['Code was submitted for review.'])

        # Ensure each issue has all required fields
        for issue in review['issues']:
            issue.setdefault('id', 'ISSUE-000')
            issue.setdefault('severity', 'info')
            issue.setdefault('category', 'style')
            issue.setdefault('title', 'Untitled Issue')
            issue.setdefault('description', '')
            issue.setdefault('codeSnippet', '')
            issue.setdefault('suggestion', '')
            issue.setdefault('explanation', '')

        return review

    except json.JSONDecodeError as e:
        return {
            'overallRisk': 'medium',
            'riskScore': 50,
            'summary': (
                'The AI analysis completed but returned an unexpected format. '
                'The results below are a best-effort interpretation.'
            ),
            'statistics': {
                'bugs': 0, 'security': 0,
                'performance': 0, 'style': 0, 'total': 0
            },
            'issues': [],
            'recommendations': [
                'Try submitting the code again for a fresh analysis.'
            ],
            'positives': ['Code was submitted for review.'],
            'error': f'JSON parse error: {str(e)}',
            'raw_response': response_text[:1000] if 'response_text' in dir() else ''
        }
    except Exception as e:
        raise RuntimeError(f"AI analysis failed: {str(e)}")
