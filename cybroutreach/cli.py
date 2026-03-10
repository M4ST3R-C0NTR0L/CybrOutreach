"""
CLI interface for CybrOutreach.

Provides commands for generating cold emails, batch processing, and template management.
"""

import os
import sys
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import pyperclip

from cybroutreach import __version__
from cybroutreach.templates import TemplateType, Tone, list_templates, TEMPLATES
from cybroutreach.providers import list_available_providers, get_provider
from cybroutreach.generator import (
    EmailGenerator, 
    GeneratedEmail,
    validate_csv_file
)

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="CybrOutreach")
@click.option(
    "--provider",
    type=click.Choice(["openrouter", "openai", "anthropic", "auto"]),
    default="auto",
    help="AI provider to use (default: auto-detect)",
)
@click.pass_context
def cli(ctx: click.Context, provider: str):
    """
    🧊 CybrOutreach - AI-powered cold email generator
    
    Generate personalized cold outreach emails using AI and proven copywriting frameworks.
    
    Examples:
        CybrOutreach generate --to "John Smith" --company "Acme Corp"
        CybrOutreach templates
        CybrOutreach batch --csv leads.csv --tone professional
    """
    ctx.ensure_object(dict)
    ctx.obj["provider"] = provider if provider != "auto" else None


@cli.command()
@click.option(
    "--to", "recipient",
    required=True,
    help="Recipient name (e.g., 'John Smith')"
)
@click.option(
    "--company",
    required=True,
    help="Company name (e.g., 'Acme Corp')"
)
@click.option(
    "--tone",
    type=click.Choice(["professional", "casual", "aggressive", "friendly"]),
    default="professional",
    help="Email tone (default: professional)"
)
@click.option(
    "--template",
    "template_type",
    type=click.Choice(["intro", "follow-up", "break-up", "meeting-request"]),
    default="intro",
    help="Template type (default: intro)"
)
@click.option(
    "--context",
    default="",
    help="Additional context about recipient/company"
)
@click.option(
    "--temperature",
    type=click.FloatRange(0.0, 1.0),
    default=0.7,
    help="AI creativity level 0.0-1.0 (default: 0.7)"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Save email to file"
)
@click.option(
    "--clipboard", "-c",
    is_flag=True,
    help="Copy email to clipboard"
)
@click.option(
    "--raw", "-r",
    is_flag=True,
    help="Output raw text without formatting"
)
@click.pass_context
def generate(
    ctx: click.Context,
    recipient: str,
    company: str,
    tone: str,
    template_type: str,
    context: str,
    temperature: float,
    output: Optional[str],
    clipboard: bool,
    raw: bool,
):
    """Generate a single cold email."""
    try:
        provider_name = ctx.obj.get("provider")
        generator = EmailGenerator(provider=get_provider(provider_name))
        
        tone_enum = Tone(tone)
        template_enum = TemplateType(template_type)
        
        if not raw:
            console.print(f"\n[bold cyan]🧊 CybrOutreach[/bold cyan] v{__version__}")
            console.print(f"[dim]Generating {tone} {template_type} email...[/dim]\n")
        
        email = generator.generate(
            recipient_name=recipient,
            company_name=company,
            tone=tone_enum,
            template_type=template_enum,
            context=context,
            temperature=temperature,
        )
        
        # Output
        if raw:
            click.echo(email.to_text())
        else:
            _display_email(email)
        
        # Save to file
        if output:
            _save_email(email, output)
            if not raw:
                console.print(f"\n[green]✓ Saved to {output}[/green]")
        
        # Copy to clipboard
        if clipboard:
            try:
                pyperclip.copy(email.to_text())
                if not raw:
                    console.print("[green]✓ Copied to clipboard[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not copy to clipboard: {e}[/yellow]")
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def templates():
    """List all available email templates."""
    table = Table(
        title="🧊 CybrOutreach Templates",
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Template", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Framework", style="magenta")
    table.add_column("Description")
    
    for template in list_templates():
        table.add_row(
            template["name"],
            template["type"],
            template["framework"],
            template["description"],
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Show tone options
    tone_table = Table(title="Available Tones", show_header=True)
    tone_table.add_column("Tone", style="bold")
    tone_table.add_column("Description")
    
    tones = [
        ("professional", "Formal, polished, business-focused"),
        ("casual", "Conversational, relaxed, approachable"),
        ("aggressive", "Direct, bold, high-energy call-to-action"),
        ("friendly", "Warm, personable, relationship-building"),
    ]
    
    for tone, desc in tones:
        tone_table.add_row(tone, desc)
    
    console.print(tone_table)
    console.print()


@cli.command()
@click.option(
    "--csv",
    "csv_file",
    required=True,
    type=click.Path(exists=True),
    help="CSV file with leads (name, company columns required)"
)
@click.option(
    "--tone",
    type=click.Choice(["professional", "casual", "aggressive", "friendly"]),
    default="professional",
    help="Email tone"
)
@click.option(
    "--template",
    "template_type",
    type=click.Choice(["intro", "follow-up", "break-up", "meeting-request"]),
    default="intro",
    help="Template type"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output directory for generated emails"
)
@click.option(
    "--delay",
    type=float,
    default=1.0,
    help="Seconds between API calls (default: 1.0)"
)
@click.option(
    "--context-field",
    help="CSV column name containing additional context"
)
@click.pass_context
def batch(
    ctx: click.Context,
    csv_file: str,
    tone: str,
    template_type: str,
    output: Optional[str],
    delay: float,
    context_field: Optional[str],
):
    """Generate emails for multiple leads from a CSV file."""
    try:
        provider_name = ctx.obj.get("provider")
        generator = EmailGenerator(provider=get_provider(provider_name))
        
        # Validate and load CSV
        console.print(f"[dim]Loading leads from {csv_file}...[/dim]")
        leads = validate_csv_file(csv_file)
        console.print(f"[green]✓ Loaded {len(leads)} leads[/green]\n")
        
        tone_enum = Tone(tone)
        template_enum = TemplateType(template_type)
        
        # Prepare output directory
        output_dir = Path(output) if output else Path("cybroutreach_output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate emails
        emails = []
        for email in generator.generate_batch(
            leads=leads,
            tone=tone_enum,
            template_type=template_enum,
            rate_limit_delay=delay,
            context_field=context_field,
        ):
            emails.append(email)
            
            # Save individual email
            safe_name = email.recipient_name.replace(" ", "_").lower()
            filename = output_dir / f"{safe_name}_{email.company_name.replace(' ', '_').lower()}.txt"
            _save_email(email, str(filename))
        
        # Summary
        console.print(f"\n[bold green]✓ Generated {len(emails)} emails[/bold green]")
        console.print(f"[dim]Saved to: {output_dir.absolute()}[/dim]")
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def status():
    """Check API provider status and configuration."""
    console.print(f"\n[bold cyan]🧊 CybrOutreach[/bold cyan] v{__version__}\n")
    
    # Provider status
    providers = list_available_providers()
    
    table = Table(title="AI Provider Status", show_header=True)
    table.add_column("Provider", style="bold")
    table.add_column("Status")
    table.add_column("Environment Variable")
    
    env_vars = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    
    for provider, available in providers.items():
        status = "[green]✓ Configured[/green]" if available else "[red]✗ Not configured[/red]"
        table.add_row(provider, status, env_vars[provider])
    
    console.print(table)
    console.print()
    
    # Show active provider
    try:
        active = get_provider()
        console.print(f"[dim]Active provider: {active.__class__.__name__}[/dim]")
    except ValueError as e:
        console.print(f"[yellow]⚠ {e}[/yellow]")
    
    console.print()


@cli.command()
@click.argument("template_type")
def preview(template_type: str):
    """Preview a template structure without generating."""
    try:
        template_enum = TemplateType(template_type)
        template = TEMPLATES[template_enum]
        
        console.print(f"\n[bold]{template.name}[/bold] ({template.framework} framework)\n")
        console.print(f"[dim]{template.description}[/dim]\n")
        
        syntax = Syntax(template.structure, "text", theme="monokai", padding=1)
        console.print(Panel(syntax, title="Template Structure"))
        
        console.print("\n[bold]Tone Guidelines:[/bold]")
        for tone, guideline in template.tone_guidelines.items():
            console.print(f"  [cyan]{tone.value}:[/cyan] {guideline}")
        
        console.print()
        
    except ValueError:
        console.print(f"[red]Invalid template type: {template_type}[/red]")
        console.print(f"[dim]Available: intro, follow-up, break-up, meeting-request[/dim]")
        sys.exit(1)


def _display_email(email: GeneratedEmail) -> None:
    """Display a generated email with nice formatting."""
    # Metadata
    meta_table = Table(show_header=False, box=None)
    meta_table.add_column(style="dim")
    meta_table.add_column()
    
    meta_table.add_row("To:", email.recipient_name)
    meta_table.add_row("Company:", email.company_name)
    meta_table.add_row("Tone:", email.tone)
    meta_table.add_row("Template:", email.template_type)
    meta_table.add_row("Model:", email.model_used)
    
    console.print(Panel(meta_table, title="Email Details", border_style="cyan"))
    
    # Email content
    content = f"[bold]Subject:[/bold] {email.subject}\n\n{email.body}"
    console.print(Panel(content, title="Generated Email", border_style="green"))
    
    if email.tokens_used:
        console.print(f"[dim]Tokens used: {email.tokens_used}[/dim]")


def _save_email(email: GeneratedEmail, filepath: str) -> None:
    """Save email to a file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# Email for {email.recipient_name} @ {email.company_name}\n")
        f.write(f"# Tone: {email.tone}\n")
        f.write(f"# Template: {email.template_type}\n")
        f.write(f"# Model: {email.model_used}\n")
        f.write(f"# Tokens: {email.tokens_used or 'N/A'}\n\n")
        f.write(email.to_text())


def main():
    """Entry point for the CLI."""
    # Load .env file if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    cli()


if __name__ == "__main__":
    main()
