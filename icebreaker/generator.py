"""
Email generation logic for IceBreaker.

Handles the orchestration of template selection, AI prompting, and output formatting.
"""

import re
import time
from typing import Optional, List, Dict, Any, Iterator
from dataclasses import dataclass
from pathlib import Path
import csv

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from icebreaker.templates import (
    TemplateType, 
    Tone, 
    get_prompt_template,
    list_templates as list_available_templates
)
from icebreaker.providers import get_provider, GenerationResult, AIProvider


console = Console()


@dataclass
class GeneratedEmail:
    """Generated email result."""
    subject: str
    body: str
    recipient_name: str
    company_name: str
    tone: str
    template_type: str
    model_used: str
    tokens_used: Optional[int] = None
    
    def to_text(self) -> str:
        """Convert to plain text format."""
        return f"Subject: {self.subject}\n\n{self.body}"
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        body_html = self.body.replace("\n", "<br>")
        return f"<h3>Subject: {self.subject}</h3><p>{body_html}</p>"


class EmailGenerator:
    """Main email generator class."""
    
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_provider()
    
    def generate(
        self,
        recipient_name: str,
        company_name: str,
        tone: Tone = Tone.PROFESSIONAL,
        template_type: TemplateType = TemplateType.INTRO,
        context: str = "",
        temperature: float = 0.7,
    ) -> GeneratedEmail:
        """
        Generate a personalized cold email.
        
        Args:
            recipient_name: Name of the recipient
            company_name: Company name
            tone: Desired tone of the email
            template_type: Type of email template
            context: Additional context about recipient/company
            temperature: AI creativity level (0.0-1.0)
            
        Returns:
            GeneratedEmail object with subject and body
        """
        prompt = get_prompt_template(
            template_type=template_type,
            tone=tone,
            recipient_name=recipient_name,
            company_name=company_name,
            context=context,
        )
        
        result = self.provider.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=1500
        )
        
        subject, body = self._parse_email_content(result.content)
        
        return GeneratedEmail(
            subject=subject,
            body=body,
            recipient_name=recipient_name,
            company_name=company_name,
            tone=tone.value,
            template_type=template_type.value,
            model_used=result.model,
            tokens_used=result.tokens_used,
        )
    
    def generate_batch(
        self,
        leads: List[Dict[str, str]],
        tone: Tone = Tone.PROFESSIONAL,
        template_type: TemplateType = TemplateType.INTRO,
        rate_limit_delay: float = 1.0,
        context_field: Optional[str] = None,
    ) -> Iterator[GeneratedEmail]:
        """
        Generate emails for multiple leads with rate limiting.
        
        Args:
            leads: List of dicts with 'name', 'company', and optional 'context'
            tone: Desired tone
            template_type: Type of template
            rate_limit_delay: Seconds to wait between requests
            context_field: Field name in leads dict containing context
            
        Yields:
            GeneratedEmail objects
        """
        total = len(leads)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Generating {total} emails...", total=total)
            
            for i, lead in enumerate(leads):
                name = lead.get("name", "").strip()
                company = lead.get("company", "").strip()
                
                if not name or not company:
                    console.print(
                        f"[yellow]⚠ Skipping lead {i+1}: missing name or company[/yellow]"
                    )
                    progress.advance(task)
                    continue
                
                context = ""
                if context_field and context_field in lead:
                    context = lead[context_field]
                elif "context" in lead:
                    context = lead["context"]
                
                try:
                    email = self.generate(
                        recipient_name=name,
                        company_name=company,
                        tone=tone,
                        template_type=template_type,
                        context=context,
                    )
                    yield email
                    
                    # Rate limiting
                    if i < total - 1 and rate_limit_delay > 0:
                        time.sleep(rate_limit_delay)
                        
                except Exception as e:
                    console.print(
                        f"[red]✗ Failed to generate for {name} @ {company}: {e}[/red]"
                    )
                
                progress.advance(task)
    
    def _parse_email_content(self, content: str) -> tuple:
        """Parse AI response into subject and body."""
        lines = content.strip().split("\n")
        
        subject = ""
        body_lines = []
        
        # Extract subject
        found_subject = False
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_lines = lines[i+1:]
                found_subject = True
                break
        
        if not found_subject:
            body_lines = lines
        
        # Clean up body
        body = "\n".join(line.strip() for line in body_lines if line.strip())
        
        # Remove markdown code blocks if present
        body = re.sub(r'```\w*\n?', '', body)
        body = body.strip()
        
        return subject, body


def validate_csv_file(file_path: str) -> List[Dict[str, str]]:
    """
    Validate and read a CSV file for batch processing.
    
    Expected columns: name, company (required)
    Optional columns: context, email, title, etc.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of lead dictionaries
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    leads = []
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns
        fieldnames = reader.fieldnames or []
        fieldnames_lower = [f.lower() for f in fieldnames]
        
        if 'name' not in fieldnames_lower:
            raise ValueError(
                f"CSV must have a 'name' column. Found: {fieldnames}"
            )
        if 'company' not in fieldnames_lower:
            raise ValueError(
                f"CSV must have a 'company' column. Found: {fieldnames}"
            )
        
        # Create normalized field mapping
        field_map = {f.lower(): f for f in fieldnames}
        
        for row in reader:
            lead = {
                "name": row.get(field_map.get("name", "name"), "").strip(),
                "company": row.get(field_map.get("company", "company"), "").strip(),
            }
            
            # Add optional fields
            for field in ["context", "email", "title", "linkedin", "website"]:
                if field in fieldnames_lower:
                    lead[field] = row.get(field_map.get(field, field), "").strip()
            
            leads.append(lead)
    
    return leads


def list_templates() -> List[Dict[str, Any]]:
    """List all available templates."""
    return list_available_templates()
