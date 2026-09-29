# Engineering AI Evaluator

> A hybrid AI evaluation system for analyzing AI-generated engineering solutions using LLM-based reasoning and deterministic Python verification.

**Status:** Work in Progress — MVP under active development

---

## Overview

Large Language Models can generate convincing engineering solutions, but a well-written answer is not necessarily an engineering-correct answer.

The **Engineering AI Evaluator** is being developed to evaluate AI-generated or candidate engineering solutions and provide structured feedback explaining:

- what is correct,
- what is incorrect,
- why an error occurred,
- and how the solution can be improved.

Instead of relying entirely on an LLM to judge another LLM, the project combines:

1. **LLM-based engineering reasoning evaluation**
2. **Deterministic Python verification**

This allows objective numerical checks to remain separate from more qualitative engineering reasoning.

---

## Current Architecture

```text
Engineering Problem
        │
        ▼
Candidate / AI Solution
        │
        ▼
┌──────────────────────────────┐
│        LLM Evaluation        │
│                              │
│ • Extract final answer       │
│ • Evaluate approach          │
│ • Inspect equations          │
│ • Analyze assumptions        │
│ • Check physical reasoning   │
│ • Identify errors            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Deterministic Verification   │
│                              │
│ • Numerical error            │
│ • Percentage error           │
│ • Tolerance verification     │
│ • Unit verification          │
└──────────────┬───────────────┘
               │
               ▼
      Structured Evaluation
               │
               ▼
      Corrected Solution