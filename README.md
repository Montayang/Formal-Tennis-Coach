# Formal-Tennis-Coach: Tactical Reasoning via LLM & PAT Engine

An automated tactical reasoning system that integrates the semantic understanding of **Large Language Models (LLMs)** with the rigorous mathematical verification of the **PAT (Process Analysis Toolkit)** formal verification engine.

---

## 🎾 Overview

This project provides a "Formal Methods AI Tennis Coach" that simulates and verifies tennis tactics in a tiebreak game. By modeling tennis as a **Markov Decision Process (MDP)** with 132 granular parameters, the system can answer "What-if" tactical questions with mathematical certainty.

### Key Features
- **Natural Language Interface**: Communicate tactical intents (e.g., "Aggressive wide serves") in plain English.
- **Agentic Parameter Mapping**: Automatically translates vague tactical descriptions into precise zero-sum probability adjustments across 132 MDP parameters.
- **Cross-System RPA Bridge**: A robust automation layer that bridges Linux (WSL) and Windows to control the legacy PAT GUI engine.
- **Robustness Guarantees**: Provides win probability intervals (Lower Bound vs. Upper Bound) to analyze the "worst-case scenario" (robustness) against an optimal opponent.

---

## 🏗️ Architecture

<img width="2257" height="1231" alt="pic1" src="https://github.com/user-attachments/assets/2a4bc96a-06d8-4532-9a0a-76c32e483aef" />

The system follows a 4-layer pipeline:
1. **User Query**: Input tactical intentions.
2. **LLM Brain (Gemini 3.1 Pro)**: Reasons and generates parameter deltas.
3. **Python Controller**: Orchestrates data injection and invokes the RPA bridge.
4. **Verification Core (PAT Engine)**: Executes the MDP verification and returns win probability bounds.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Both on Linux/WSL and Windows Host)
- **PAT (Process Analysis Toolkit) 3.5.1** installed on Windows.
- **Google GenAI API Key** (for Gemini 3.1 Pro/2.5 Flash).

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/Montayang/Formal-Tennis-Coach.git](https://github.com/Montayang/Formal-Tennis-Coach.git)
   cd Formal-Tennis-Coach
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
### Data Preparation
Ensure the historical database tennisabstract-v2-combined.csv is placed in the root directory. (Note: This file is usually ignored by Git due to size; please download it separately.)

## 🖥️ Usage
Run the main agent interface:  python llm_agent.py

### Example Queries
"I am Novak Djokovic. I'm playing Daniil Medvedev on 2021-02-21. What if I aggressively target the wide side on my deuce court first serve?"

## 📊 Technical Details
Model: Probabilistic CSP (PCSP#)

State Space: 7-point Tiebreak game.

Non-determinism: Handled via PAT's MDP verification to find absolute win rate boundaries.
