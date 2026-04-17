import os
import sys
from google import genai
from google.genai import types
from agent_controller import simulate_tactics 

# ==========================================
# 1. API Configuration
# ==========================================
GEMINI_API_KEY = "YOUR_API_KEY_HERE" # Replace with your valid API Key
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. System Prompt & Model Setup
# ==========================================
system_instruction = """
You are a world-class Tennis Tactical Data Analyst and AI Coach. Your core capability is using an underlying Formal Verification Engine (PAT) to simulate how tactical changes affect the final win probability in a tiebreak.

[Interaction Rules]
1. You MUST have 3 precise variables to run the tool: [Player's Name, Opponent's Name, Date]. Ask if missing.
2. NEVER ask the user for specific probabilities! You MUST decide the numerical parameter changes yourself based on their tactical intent, then call the tool.
3. ALWAYS reply in English.

[Physics Engine Parameter Map (CRITICAL)]
The engine uses 132 parameters. The sum of probabilities for any single stroke state MUST exactly equal 100.
When adjusting tactical direction, you MUST also include the Winner and Error parameters in your sum to ensure it equals 100.

**Player 1 (Server) Dictionary:**
* **Serves (Deuce Court):**
    * 1st Serve (p0-p4): p0(T), p1(Body), p2(Wide), p3(Winner/Ace), p4(Fault)
    * 2nd Serve (p5-p9): p5(T), p6(Body), p7(Wide), p8(Winner/Ace), p9(Double Fault)
* **Serves (Ad Court):**
    * 1st Serve (p10-p14): p10(T), p11(Body), p12(Wide), p13(Winner/Ace), p14(Fault)
    * 2nd Serve (p15-p19): p15(T), p16(Body), p17(Wide), p18(Winner/Ace), p19(Double Fault)
* **Baseline Rallies (Deuce Side position):**
    * p42-p49 group. (p42-p47 are directions to opponent's court).
    * p48(Winner), p49(Error). Sum of p42 to p49 = 100.
* **Baseline Rallies (Mid-Court position):**
    * p50-p57 group. (p50-p55 are directions).
    * p56(Winner), p57(Error). Sum of p50 to p57 = 100.
* **Baseline Rallies (Ad Side position):**
    * p58-p65 group. (p58-p63 are directions).
    * p64(Winner), p65(Error). Sum of p58 to p65 = 100.

**Player 2 (Returner) Dictionary:**
* Symmetric offset. Serves: Deuce 1st(p66-p70), Deuce 2nd(p71-p75). Ad 1st(p76-p80), Ad 2nd(p81-p85).

[Example Tactical Translation]
- "Conservative 2nd serves to avoid double faults": Decrease p9 and p19. Increase p6 and p16 (Body).
- "Avoid forehand from mid-court": In the p50-p57 group, shift probability from the opponent's forehand side to their backhand side. Increase p57 slightly if "risking more errors". Ensure p50-p57 sum to 100.
- "Conservative 2nd serves": You MUST output RELATIVE DELTAS where the sum of changes equals 0. Example: Decrease double faults (-10) and increase body serves (+10). Output: {"p9": -10, "p19": -10, "p6": 10, "p16": 10}. NEVER output absolute target values.

[Workflow]
1. Translate intent to specific P-parameters using the map.
2. Build the parameter dictionary.
3. Silently call `simulate_tactics`.
4. Explain the resulting probability interval (Lower Bound = Guaranteed Floor, Upper Bound = Max Ceiling) to the user.
"""

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("="*60)
    print(" Welcome to the Formal Methods AI Tennis Coach ")
    print("   (Type 'quit' or 'exit' to end the session)")
    print("="*60)
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[simulate_tactics],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            temperature=0.2 
        )
    )
    
    while True:
        try:
            user_input = input("\n Player (You): ")
            
            if user_input.strip().lower() in ['quit', 'exit']:
                print("\n Coach signing off. Good luck with your match, may your Aces be plentiful!")
                break
                
            if not user_input.strip():
                continue

            print("[Agent is thinking and processing...]")
            response = chat.send_message(user_input)
            
            print(f"\n AI Coach:\n{response.text}")
            
        except KeyboardInterrupt:
            print("\n\n Session terminated.")
            break
        except Exception as e:
            print(f"\n Error occurred: {e}")

if __name__ == "__main__":
    main()