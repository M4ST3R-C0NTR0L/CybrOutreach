"""Tests for templates module."""

import pytest

from icebreaker.templates import (
    TemplateType,
    Tone,
    get_template,
    list_templates,
    get_tone_guideline,
    get_prompt_template,
    TEMPLATES,
)


class TestTemplateType:
    """Test TemplateType enum."""
    
    def test_template_values(self):
        """Test template type values."""
        assert TemplateType.INTRO.value == "intro"
        assert TemplateType.FOLLOW_UP.value == "follow-up"
        assert TemplateType.BREAKUP.value == "break-up"
        assert TemplateType.MEETING_REQUEST.value == "meeting-request"


class TestTone:
    """Test Tone enum."""
    
    def test_tone_values(self):
        """Test tone enum values."""
        assert Tone.PROFESSIONAL.value == "professional"
        assert Tone.CASUAL.value == "casual"
        assert Tone.AGGRESSIVE.value == "aggressive"
        assert Tone.FRIENDLY.value == "friendly"


class TestGetTemplate:
    """Test get_template function."""
    
    def test_get_intro_template(self):
        """Test getting intro template."""
        template = get_template(TemplateType.INTRO)
        assert template.name == "Introduction"
        assert template.framework == "AIDA"
    
    def test_get_follow_up_template(self):
        """Test getting follow-up template."""
        template = get_template(TemplateType.FOLLOW_UP)
        assert template.name == "Follow-Up"
        assert template.framework == "PAS"
    
    def test_get_breakup_template(self):
        """Test getting break-up template."""
        template = get_template(TemplateType.BREAKUP)
        assert template.name == "Break-Up"
        assert template.framework == "BAB"
    
    def test_get_meeting_request_template(self):
        """Test getting meeting request template."""
        template = get_template(TemplateType.MEETING_REQUEST)
        assert template.name == "Meeting Request"
        assert template.framework == "AIDA"


class TestListTemplates:
    """Test list_templates function."""
    
    def test_returns_list(self):
        """Test that list_templates returns a list."""
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) == 4
    
    def test_template_structure(self):
        """Test that templates have required fields."""
        templates = list_templates()
        for template in templates:
            assert "name" in template
            assert "type" in template
            assert "framework" in template
            assert "description" in template


class TestGetToneGuideline:
    """Test get_tone_guideline function."""
    
    def test_returns_string(self):
        """Test that guideline is returned as string."""
        guideline = get_tone_guideline(TemplateType.INTRO, Tone.PROFESSIONAL)
        assert isinstance(guideline, str)
        assert len(guideline) > 0
    
    def test_different_tones_different_guidelines(self):
        """Test that different tones have different guidelines."""
        prof = get_tone_guideline(TemplateType.INTRO, Tone.PROFESSIONAL)
        casual = get_tone_guideline(TemplateType.INTRO, Tone.CASUAL)
        assert prof != casual


class TestGetPromptTemplate:
    """Test get_prompt_template function."""
    
    def test_prompt_contains_recipient_info(self):
        """Test that prompt includes recipient information."""
        prompt = get_prompt_template(
            TemplateType.INTRO,
            Tone.PROFESSIONAL,
            "John Doe",
            "Acme Corp",
        )
        assert "John Doe" in prompt
        assert "Acme Corp" in prompt
    
    def test_prompt_contains_context(self):
        """Test that prompt includes context when provided."""
        context = "They are a SaaS company focused on AI"
        prompt = get_prompt_template(
            TemplateType.INTRO,
            Tone.PROFESSIONAL,
            "John Doe",
            "Acme Corp",
            context,
        )
        assert context in prompt
    
    def test_prompt_contains_framework(self):
        """Test that prompt mentions the framework."""
        prompt = get_prompt_template(
            TemplateType.INTRO,
            Tone.PROFESSIONAL,
            "John",
            "Company",
        )
        assert "AIDA" in prompt
    
    def test_prompt_all_tones(self):
        """Test prompt generation for all tones."""
        for tone in Tone:
            prompt = get_prompt_template(
                TemplateType.INTRO,
                tone,
                "Test",
                "Company",
            )
            assert tone.value in prompt


class TestTemplateStructures:
    """Test template structures."""
    
    def test_all_templates_have_required_components(self):
        """Test that all templates have required components."""
        for template_type, template in TEMPLATES.items():
            assert template.name
            assert template.framework
            assert template.description
            assert template.structure
            assert len(template.tone_guidelines) == 4
            for tone in Tone:
                assert tone in template.tone_guidelines
