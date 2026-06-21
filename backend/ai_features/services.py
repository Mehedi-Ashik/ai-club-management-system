"""
AI service layer — handles calls to the LLM API (Claude / OpenAI)
for event description generation and blog draft assistance.
"""

def generate_event_description(title: str, category: str, event_date: str) -> str:
    """Generate a polished event description using an LLM API."""
    raise NotImplementedError


def generate_blog_draft(topic: str) -> str:
    """Generate a blog post draft from a topic using an LLM API."""
    raise NotImplementedError
