#!/bin/bash
# Example: Generate aggressive follow-ups for cold leads

icebreaker batch \
  --csv leads.csv \
  --tone aggressive \
  --template follow-up \
  --delay 2.0 \
  --output ./emails/followup
