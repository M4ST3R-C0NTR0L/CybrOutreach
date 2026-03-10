# 🧊 CybrOutreach

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/pip-installable-blue.svg" alt="Pip Installable">
  <img src="https://img.shields.io/badge/AI-powered-orange.svg" alt="AI Powered">
</p>

<p align="center">
  <b>AI-powered cold email generator with personalized outreach</b>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/M4ST3R-C0NTR0L/CybrOutreach/main/assets/demo.gif" alt="CybrOutreach Demo" width="700">
</p>

## ✨ Features

- **🤖 AI-Powered Personalization** - Generate unique, personalized emails using advanced AI models
- **📧 Multiple Templates** - Intro, Follow-up, Break-up, and Meeting Request templates
- **🎭 Four Tones** - Professional, Casual, Aggressive, and Friendly
- **📊 Proven Frameworks** - Built on AIDA, PAS, and BAB copywriting frameworks
- **📁 Batch Processing** - Generate emails for hundreds of leads from CSV files
- **🔧 Multiple AI Providers** - OpenRouter, OpenAI, and Anthropic support
- **🎨 Beautiful Output** - Rich terminal formatting with colors and styling
- **📋 Clipboard Support** - Copy emails directly to clipboard
- **💾 File Export** - Save emails to files for later use

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install CybrOutreach
```

### From Source

```bash
git clone https://github.com/M4ST3R-C0NTR0L/CybrOutreach.git
cd CybrOutreach
pip install -e .
```

## 🔑 Configuration

CybrOutreach requires an AI provider API key. Set one of these environment variables:

```bash
# Recommended - supports 100+ models
export OPENROUTER_API_KEY="your-key-here"

# Or use direct providers
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

You can also create a `.env` file in your working directory:

```env
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

## 📖 Usage

### Generate a Single Email

```bash
# Basic intro email
CybrOutreach generate --to "John Smith" --company "Acme Corp"

# Professional tone with context
CybrOutreach generate \
  --to "Jane Doe" \
  --company "TechStartup" \
  --tone professional \
  --template intro \
  --context "They are a Series A SaaS company focusing on AI"

# Casual follow-up
CybrOutreach generate \
  --to "Mike Johnson" \
  --company "GrowthCo" \
  --tone casual \
  --template follow-up

# Copy to clipboard
CybrOutreach generate --to "Sarah" --company "ScaleUp" --clipboard

# Save to file
CybrOutreach generate --to "Alex" --company "Startup" --output email.txt
```

### List Available Templates

```bash
CybrOutreach templates
```

### Preview a Template Structure

```bash
CybrOutreach preview intro
CybrOutreach preview follow-up
CybrOutreach preview break-up
CybrOutreach preview meeting-request
```

### Check Provider Status

```bash
CybrOutreach status
```

### Batch Processing from CSV

Create a `leads.csv` file:

```csv
name,company,context,title
John Smith,Acme Corp,AI startup focused on NLP,CEO
Jane Doe,Tech Inc,SaaS company 50 employees,CTO
Bob Wilson,StartupXYZ,Pre-seed fintech startup,Founder
```

Run batch generation:

```bash
# Basic batch
CybrOutreach batch --csv leads.csv

# With specific tone and template
CybrOutreach batch \
  --csv leads.csv \
  --tone professional \
  --template intro \
  --output ./emails

# With rate limiting (recommended)
CybrOutreach batch \
  --csv leads.csv \
  --delay 2.0 \
  --context-field context
```

## 🎭 Tones

| Tone | Description | Best For |
|------|-------------|----------|
| **Professional** | Formal, polished, business-focused | Enterprise sales, C-suite |
| **Casual** | Conversational, relaxed, approachable | Startups, creative industries |
| **Aggressive** | Direct, bold, high-energy | Time-sensitive offers, competitive markets |
| **Friendly** | Warm, personable, relationship-building | Long-term partnerships, warm leads |

## 📧 Templates

### Introduction (AIDA Framework)
Perfect for first contact. Grabs attention, builds interest, creates desire, and drives action.

### Follow-Up (PAS Framework)
For prospects who haven't responded. Highlights problem, agitates pain points, presents solution.

### Break-Up (BAB Framework)
Final email to unresponsive prospects. Shows before/after state with bridge to your solution.

### Meeting Request (AIDA Framework)
Specifically designed to book meetings/calls with clear value proposition.

## 🔧 Advanced Configuration

### OpenRouter Settings

```bash
# Set custom model
export OPENROUTER_MODEL="meta-llama/llama-3.1-70b-instruct"

# Optional: Set your site info
export OPENROUTER_SITE_URL="https://yourcompany.com"
export OPENROUTER_SITE_NAME="Your Company"
```

### Provider Priority

By default, CybrOutreach auto-detects available providers in this order:
1. OpenRouter (recommended - most models)
2. OpenAI
3. Anthropic

Force a specific provider:

```bash
CybrOutreach --provider openai generate --to "John" --company "Acme"
```

Or set via environment:

```bash
export CYBROUTREACH_PROVIDER="anthropic"
```

## 📋 CSV Format

Required columns:
- `name` - Recipient's full name
- `company` - Company name

Optional columns:
- `context` - Additional context for personalization
- `email` - Email address (preserved in output)
- `title` - Job title
- `linkedin` - LinkedIn URL
- `website` - Company website

## 🧪 Development

### Setup

```bash
git clone https://github.com/M4ST3R-C0NTR0L/CybrOutreach.git
cd CybrOutreach
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black CybrOutreach/ tests/
ruff check CybrOutreach/ tests/
mypy CybrOutreach/
```

## 📝 Example Output

```
🧊 CybrOutreach v1.0.0

┌─────────────────────────────────────────────────────────────┐
│ Email Details                                               │
├─────────────────────────────────────────────────────────────┤
│ To:        John Smith                                       │
│ Company:   Acme Corp                                        │
│ Tone:      professional                                     │
│ Template:  intro                                            │
│ Model:     anthropic/claude-3.5-sonnet                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Generated Email                                             │
├─────────────────────────────────────────────────────────────┤
│ Subject: Quick question about Acme Corp's growth strategy   │
│                                                             │
│ John,                                                       │
│                                                             │
│ I noticed Acme Corp just raised your Series B—congrats!     │
│ Scaling customer success teams is typically the biggest     │
│ challenge at this stage.                                    │
│                                                             │
│ We helped similar B2B SaaS companies reduce onboarding      │
│ time by 60% while handling 3x the customer volume.          │
│                                                             │
│ Worth a brief conversation about your Q4 goals?             │
│                                                             │
│ Best,                                                       │
│ [Your name]                                                 │
└─────────────────────────────────────────────────────────────┘

Tokens used: 312
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- Copywriting frameworks from legendary copywriters
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- AI powered by [OpenRouter](https://openrouter.ai/), [OpenAI](https://openai.com/), and [Anthropic](https://anthropic.com/)

---

<p align="center">
  Made with ❄️ by the CybrOutreach Team
</p>
