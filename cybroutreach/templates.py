"""
Email templates with proven copywriting frameworks.

Includes templates for various outreach scenarios using frameworks like:
- AIDA (Attention, Interest, Desire, Action)
- PAS (Problem, Agitation, Solution)
- BAB (Before, After, Bridge)
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class Tone(Enum):
    """Email tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AGGRESSIVE = "aggressive"
    FRIENDLY = "friendly"


class TemplateType(Enum):
    """Template type options."""
    INTRO = "intro"
    FOLLOW_UP = "follow-up"
    BREAKUP = "break-up"
    MEETING_REQUEST = "meeting-request"


@dataclass
class EmailTemplate:
    """Email template definition."""
    name: str
    template_type: TemplateType
    framework: str
    description: str
    tone_guidelines: Dict[Tone, str]
    structure: str


TEMPLATES: Dict[TemplateType, EmailTemplate] = {
    TemplateType.INTRO: EmailTemplate(
        name="Introduction",
        template_type=TemplateType.INTRO,
        framework="AIDA",
        description="First contact email to introduce yourself and your offering",
        tone_guidelines={
            Tone.PROFESSIONAL: "Formal, polished, business-focused language",
            Tone.CASUAL: "Conversational, relaxed, approachable",
            Tone.AGGRESSIVE: "Direct, bold, high-energy call-to-action",
            Tone.FRIENDLY: "Warm, personable, relationship-building",
        },
        structure="""
Subject: [Compelling subject line]

[Attention - Hook: Compelling opening that grabs attention]

[Interest - Why: Establish relevance and value proposition]

[Desire - What: Specific benefits and outcomes]

[Action - CTA: Clear next step]

[Sign-off]
""",
    ),
    TemplateType.FOLLOW_UP: EmailTemplate(
        name="Follow-Up",
        template_type=TemplateType.FOLLOW_UP,
        framework="PAS",
        description="Follow-up email for prospects who haven't responded",
        tone_guidelines={
            Tone.PROFESSIONAL: "Respectful, persistent, value-add focus",
            Tone.CASUAL: "Light, breezy, no pressure",
            Tone.AGGRESSIVE: "Urgency-driven, FOMO-inducing",
            Tone.FRIENDLY: "Caring, helpful, genuinely interested",
        },
        structure="""
Subject: [Re: Previous / New angle]

[Problem - Acknowledge their challenge or previous silence]

[Agitation - Amplify the cost of not solving it]

[Solution - Your offering as the answer]

[Soft CTA - Easy next step]

[Sign-off]
""",
    ),
    TemplateType.BREAKUP: EmailTemplate(
        name="Break-Up",
        template_type=TemplateType.BREAKUP,
        framework="BAB",
        description="Final email to unresponsive prospects",
        tone_guidelines={
            Tone.PROFESSIONAL: "Graceful exit, door left open",
            Tone.CASUAL: "No hard feelings, keep it light",
            Tone.AGGRESSIVE: "Final opportunity, create urgency",
            Tone.FRIENDLY: "Genuine well-wishes, authentic",
        },
        structure="""
Subject: [Closing the loop / Permission to close your file]

[Before - Current state without your solution]

[After - Potential state with your solution]

[Bridge - Brief offer to connect one last time]

[Permission-based close]

[Sign-off]
""",
    ),
    TemplateType.MEETING_REQUEST: EmailTemplate(
        name="Meeting Request",
        template_type=TemplateType.MEETING_REQUEST,
        framework="AIDA",
        description="Email specifically requesting a meeting or call",
        tone_guidelines={
            Tone.PROFESSIONAL: "Respectful of time, clear agenda",
            Tone.CASUAL: "Coffee chat vibe, low commitment",
            Tone.AGGRESSIVE: "Specific time slots, assumptive close",
            Tone.FRIENDLY: "Mutual benefit, collaborative tone",
        },
        structure="""
Subject: [Meeting focus / Time investment]

[Attention - Hook relevant to their role/company]

[Interest - Why this meeting matters now]

[Desire - What they'll gain from 15-30 minutes]

[Action - Specific meeting request with options]

[Sign-off]
""",
    ),
}


def get_template(template_type: TemplateType) -> EmailTemplate:
    """Get a template by type."""
    return TEMPLATES[template_type]


def list_templates() -> List[Dict[str, Any]]:
    """List all available templates with their details."""
    return [
        {
            "name": template.name,
            "type": template.template_type.value,
            "framework": template.framework,
            "description": template.description,
        }
        for template in TEMPLATES.values()
    ]


def get_tone_guideline(template_type: TemplateType, tone: Tone) -> str:
    """Get tone guidelines for a specific template and tone."""
    template = TEMPLATES[template_type]
    return template.tone_guidelines.get(tone, template.tone_guidelines[Tone.PROFESSIONAL])


def get_prompt_template(
    template_type: TemplateType,
    tone: Tone,
    recipient_name: str,
    company_name: str,
    context: str = "",
) -> str:
    """
    Generate a system prompt for the AI to create an email.
    
    Args:
        template_type: Type of email template
        tone: Desired tone
        recipient_name: Name of the recipient
        company_name: Company name
        context: Additional context about the recipient/company
        
    Returns:
        Complete prompt for the AI
    """
    template = TEMPLATES[template_type]
    tone_guideline = get_tone_guideline(template_type, tone)
    
    prompt = f"""You are an expert cold email copywriter specializing in B2B outreach.

TASK: Write a personalized cold email using the {template.framework} framework.

RECIPIENT DETAILS:
- Name: {recipient_name}
- Company: {company_name}
{f'- Context: {context}' if context else ''}

TEMPLATE TYPE: {template.name}
TEMPLATE STRUCTURE:
{template.structure}

TONE: {tone.value}
TONE GUIDELINES: {tone_guideline}

REQUIREMENTS:
1. Use the {template.framework} framework structure
2. Maintain a {tone.value} tone throughout
3. Keep it concise (150-200 words)
4. Make it feel personal, not templated
5. Include a clear, low-friction call-to-action
6. No generic phrases like "I hope this email finds you well"
7. Focus on value for THEM, not features of your product
8. Use line breaks for readability

OUTPUT FORMAT:
Subject: [Compelling subject line - max 50 chars]

[Email body with proper formatting]

[Professional sign-off]

Write only the email content, no explanations or notes."""

    return prompt
