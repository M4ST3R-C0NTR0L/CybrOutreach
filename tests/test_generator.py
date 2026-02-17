"""Tests for generator module."""

import csv
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from icebreaker.generator import (
    EmailGenerator,
    GeneratedEmail,
    validate_csv_file,
)
from icebreaker.templates import TemplateType, Tone


class TestGeneratedEmail:
    """Test GeneratedEmail dataclass."""
    
    def test_creation(self):
        """Test creating a GeneratedEmail."""
        email = GeneratedEmail(
            subject="Test Subject",
            body="Test body content",
            recipient_name="John Doe",
            company_name="Acme Corp",
            tone="professional",
            template_type="intro",
            model_used="test-model",
            tokens_used=100
        )
        assert email.subject == "Test Subject"
        assert email.recipient_name == "John Doe"
    
    def test_to_text(self):
        """Test text conversion."""
        email = GeneratedEmail(
            subject="Subject",
            body="Body content",
            recipient_name="Test",
            company_name="Test Co",
            tone="professional",
            template_type="intro",
            model_used="model"
        )
        text = email.to_text()
        assert "Subject: Subject" in text
        assert "Body content" in text
    
    def test_to_html(self):
        """Test HTML conversion."""
        email = GeneratedEmail(
            subject="Subject",
            body="Line 1\nLine 2",
            recipient_name="Test",
            company_name="Test Co",
            tone="professional",
            template_type="intro",
            model_used="model"
        )
        html = email.to_html()
        assert "<h3>Subject: Subject</h3>" in html
        assert "<br>" in html


class TestEmailGenerator:
    """Test EmailGenerator class."""
    
    def test_init_with_provider(self):
        """Test initialization with explicit provider."""
        mock_provider = Mock()
        generator = EmailGenerator(provider=mock_provider)
        assert generator.provider == mock_provider
    
    def test_parse_email_content_with_subject(self):
        """Test parsing email with explicit subject line."""
        mock_provider = Mock()
        generator = EmailGenerator(provider=mock_provider)
        
        content = "Subject: Great Opportunity\n\nHello,\n\nThis is the body."
        subject, body = generator._parse_email_content(content)
        
        assert subject == "Great Opportunity"
        assert "Hello," in body
        assert "This is the body." in body
    
    def test_parse_email_without_subject(self):
        """Test parsing email without subject line."""
        mock_provider = Mock()
        generator = EmailGenerator(provider=mock_provider)
        
        content = "Just a body\nWith multiple lines"
        subject, body = generator._parse_email_content(content)
        
        assert subject == ""
        assert "Just a body" in body
    
    def test_parse_removes_markdown(self):
        """Test that markdown code blocks are removed."""
        mock_provider = Mock()
        generator = EmailGenerator(provider=mock_provider)
        
        content = "Subject: Test\n\n```\nSome code\n```\nBody text"
        subject, body = generator._parse_email_content(content)
        
        assert "```" not in body
        assert "Some code" in body


class TestValidateCSVFile:
    """Test CSV validation."""
    
    def test_valid_csv(self, tmp_path):
        """Test valid CSV file."""
        csv_file = tmp_path / "leads.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "company", "context"])
            writer.writerow(["John Doe", "Acme Corp", "AI company"])
            writer.writerow(["Jane Smith", "Tech Inc", "SaaS startup"])
        
        leads = validate_csv_file(str(csv_file))
        assert len(leads) == 2
        assert leads[0]["name"] == "John Doe"
        assert leads[0]["company"] == "Acme Corp"
    
    def test_missing_name_column(self, tmp_path):
        """Test CSV without name column."""
        csv_file = tmp_path / "leads.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["company", "email"])
            writer.writerow(["Acme Corp", "test@example.com"])
        
        with pytest.raises(ValueError) as exc_info:
            validate_csv_file(str(csv_file))
        assert "name" in str(exc_info.value).lower()
    
    def test_missing_company_column(self, tmp_path):
        """Test CSV without company column."""
        csv_file = tmp_path / "leads.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email"])
            writer.writerow(["John Doe", "test@example.com"])
        
        with pytest.raises(ValueError) as exc_info:
            validate_csv_file(str(csv_file))
        assert "company" in str(exc_info.value).lower()
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_csv_file("/nonexistent/path/leads.csv")
    
    def test_case_insensitive_columns(self, tmp_path):
        """Test that column matching is case-insensitive."""
        csv_file = tmp_path / "leads.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["NAME", "COMPANY", "Context"])
            writer.writerow(["John Doe", "Acme Corp", "Context here"])
        
        leads = validate_csv_file(str(csv_file))
        assert len(leads) == 1
        assert leads[0]["name"] == "John Doe"
