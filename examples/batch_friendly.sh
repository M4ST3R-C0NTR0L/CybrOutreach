#!/bin/bash
# Example: Generate intro emails for warm leads

icebreaker batch \
  --csv leads.csv \
  --tone friendly \
  --template intro \
  --delay 1.5 \
  --output ./emails/intro
