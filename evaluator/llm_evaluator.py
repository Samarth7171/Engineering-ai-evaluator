import os

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# 1. LOAD API KEY
# --------------------------------------------------

# Load variables stored inside the .env file
load_dotenv()

# Get our OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")

# Stop the program if the key cannot be found
if not api_key:
    raise ValueError("OPENROUTER_API_KEY was not found in .env")


# --------------------------------------------------
# 2. CONNECT TO OPENROUTER
# --------------------------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# --------------------------------------------------
# 3. ENGINEERING QUESTION
# --------------------------------------------------

engineering_question = """
Air has a density of 1.225 kg/m^3 and flows at 50 m/s.
Calculate the dynamic pressure.
"""


# --------------------------------------------------
# 4. AI-GENERATED / CANDIDATE SOLUTION
# --------------------------------------------------

candidate_solution = """
Dynamic pressure is calculated using:

q = rho * V^2

q = 1.225 * 50^2

q = 3062.5 Pa

Therefore, the dynamic pressure is 3062.5 Pa.
"""


# --------------------------------------------------
# 5. SYSTEM PROMPT
# --------------------------------------------------

system_prompt = """
You are an engineering solution evaluator.

Your job is to evaluate a proposed solution to an engineering problem.

Check the solution for:

- correctness of the approach
- equations and formulas
- mathematical reasoning
- numerical calculations
- units
- assumptions
- physical plausibility
- final answer
- clarity of explanation

Identify specific mistakes and explain why they are mistakes.

Do not only say that an answer is wrong.
Explain the engineering reasoning behind your evaluation.

After identifying the errors, provide a corrected solution.
"""


# --------------------------------------------------
# 6. USER PROMPT
# --------------------------------------------------

user_prompt = f"""
ENGINEERING QUESTION:

{engineering_question}

CANDIDATE SOLUTION:

{candidate_solution}

Evaluate this solution.
"""


# --------------------------------------------------
# 7. SEND REQUEST TO THE LLM
# --------------------------------------------------

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
)


# --------------------------------------------------
# 8. PRINT THE LLM'S EVALUATION
# --------------------------------------------------

print("\n========== ENGINEERING AI EVALUATION ==========\n")

print(response.choices[0].message.content)

print("\n================================================\n")