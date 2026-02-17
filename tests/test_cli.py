"""Tests for CLI module."""

import os
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

import pytest

from icebreaker.cli import cli, main


class TestCLICommands:
    """Test CLI commands."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_version(self):
        """Test version flag."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'icebreaker' in result.output.lower()
    
    def test_help(self):
        """Test help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'IceBreaker' in result.output


class TestTemplatesCommand:
    """Test templates command."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_templates_list(self):
        """Test templates list command."""
        result = self.runner.invoke(cli, ['templates'])
        assert result.exit_code == 0
        assert 'Introduction' in result.output
        assert 'Follow-Up' in result.output


class TestStatusCommand:
    """Test status command."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_status_shows_providers(self):
        """Test that status shows provider information."""
        result = self.runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert 'openrouter' in result.output.lower()
        assert 'openai' in result.output.lower()


class TestPreviewCommand:
    """Test preview command."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_preview_valid_template(self):
        """Test preview with valid template."""
        result = self.runner.invoke(cli, ['preview', 'intro'])
        assert result.exit_code == 0
        assert 'Introduction' in result.output
        assert 'AIDA' in result.output
    
    def test_preview_invalid_template(self):
        """Test preview with invalid template."""
        result = self.runner.invoke(cli, ['preview', 'invalid'])
        assert result.exit_code != 0


class TestGenerateCommand:
    """Test generate command."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    @patch('icebreaker.cli.get_provider')
    @patch('icebreaker.cli.EmailGenerator')
    def test_generate_basic(self, mock_generator_class, mock_get_provider):
        """Test basic generate command."""
        mock_provider = Mock()
        mock_get_provider.return_value = mock_provider
        
        mock_email = Mock()
        mock_email.to_text.return_value = "Subject: Test\n\nBody"
        mock_email.recipient_name = "John"
        mock_email.company_name = "Acme"
        mock_email.tone = "professional"
        mock_email.template_type = "intro"
        mock_email.model_used = "test-model"
        mock_email.tokens_used = 100
        mock_email.subject = "Test Subject"
        mock_email.body = "Body content"
        
        mock_generator = Mock()
        mock_generator.generate.return_value = mock_email
        mock_generator_class.return_value = mock_generator
        
        result = self.runner.invoke(cli, [
            'generate',
            '--to', 'John Smith',
            '--company', 'Acme Corp',
            '--raw'
        ])
        
        assert result.exit_code == 0
        mock_generator.generate.assert_called_once()
    
    def test_generate_missing_required(self):
        """Test generate without required arguments."""
        result = self.runner.invoke(cli, ['generate'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'Usage:' in result.output


class TestBatchCommand:
    """Test batch command."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_batch_missing_file(self):
        """Test batch with non-existent file."""
        result = self.runner.invoke(cli, [
            'batch',
            '--csv', '/nonexistent/file.csv'
        ])
        assert result.exit_code != 0


class TestMain:
    """Test main entry point."""
    
    @patch('icebreaker.cli.cli')
    def test_main_calls_cli(self, mock_cli):
        """Test that main calls the CLI."""
        main()
        mock_cli.assert_called_once()
