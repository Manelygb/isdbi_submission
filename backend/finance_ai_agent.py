# finance_ai_agent.py

import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI  


# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = ""
# Initialize the model
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.4
)

# === Prompt: Classifier ===
classifier_prompt = PromptTemplate(
    input_variables=["scenario"],
    template="""
You are an Islamic finance accounting expert.

Your task is to classify the type of Islamic finance contract described in the scenario below, using AAOIFI standards.

Respond with two lines in this exact format:
Classification=<Ijarah / Murabaha / Musharakah / Salam / Istisna / Unknown>
Justification=<brief explanation for the classification, based on scenario content>

Use the following descriptions and keyword cues:

---

Ijarah (FAS 32, SS 9): Lease contract where the lessee gets the **usufruct** of an asset. May include **transfer of ownership** at the end via **gift** or **sale** (Ijarah Muntahia Bittamleek).
- Keywords: rental, right of use, lease, transfer of ownership, Ijarah MBT, residual value, right-of-use, deferred Ijarah cost, lessee, lessor

Murabaha (FAS 28, SS 8): **Cost-plus** sale where the seller discloses profit. Payment is usually **deferred**.
- Keywords: purchase cost, markup, selling price, deferred payment, Hamish Jiddiyyah, Arboun, Murabaha receivable

Musharakah (FAS 4, SS 12): Profit-sharing partnership where one party provides **capital** and the other **manages**. Loss borne only by capital provider.
- Keywords: profit-sharing, capital provider, investment partner, loss borne by funder

Salam (FAS 7, SS 10): Buyer pays **full price in advance**, and goods are delivered later. Often used for agriculture or commodities.
- Keywords: advance payment, future delivery, quantity and quality specified, Salam capital

Istisna (FAS 10, SS 11): Contract to **manufacture or build** something to order. Payment and delivery can be deferred.
- Keywords: custom construction, manufacturing, infrastructure, delivery schedule, progress billing, parallel Istisna

---

If the type is unclear, return:
Classification=Unknown
Justification=Scenario lacks sufficient or conclusive contract features.

Scenario:
{scenario}
"""  # [Put your full classifier prompt here]
)
classifier_chain = LLMChain(llm=llm, prompt=classifier_prompt)

# === Prompt Templates for Each Contract ===
ijarah_prompt = PromptTemplate(input_variables=["scenario"], template="""
You are an Islamic finance accounting expert with deep knowledge of AAOIFI Financial Accounting Standard No. 10 (Ijarah and Ijarah Muntahia Bittamleek).

Given the scenario below, apply the Underlying Asset Cost Method and follow the correct AAOIFI-compliant accounting treatment at the commencement of the lease for the lessee. Assume ownership transfer at the end is highly likely unless stated otherwise.

Perform the following steps:

A. Calculations:
1. Determine the total cost of the underlying asset, including all directly attributable costs such as freight, installation, or import duties.
2. Calculate the Right-of-Use (ROU) Asset:
   - If transfer of ownership is highly likely, subtract the purchase-option price from the asset cost.
   - If not, use the full cost without subtracting the purchase price.
3. Calculate total lease rental payments due over the lease term.
4. Compute the Deferred Ijarah Cost: total rentals minus ROU asset.
5. Determine the Amortisable Amount:
   - Compute the Terminal Value Difference = Residual Value – Purchase Option Price.
   - Subtract it from the ROU asset.

B. Initial Journal Entry:
Provide the journal entry at lease commencement using proper Dr/Cr format, aligned with AAOIFI FAS 10.

C. Amortisation Schedules:
Calculate straight-line annual amortisation for:
- The Right-of-Use asset
- The Deferred Ijarah Cost

Scenario:
{scenario}
""")
murabaha_prompt = PromptTemplate(input_variables=["scenario"], template="""
You are an Islamic finance accounting expert.

Apply AAOIFI Financial Accounting Standard 28 (Murabaha and Deferred Payment Sales) and Shari’ah Standard No. 8 to the scenario below. Your task is to generate the correct accounting treatment **in the books of the seller (Islamic bank)** at the time of Murabaha contract execution.

Follow these steps:
1. Calculate the total acquisition cost (purchase price + any directly related expenses, such as transport, taxes, or agency fees).
2. State the Murabaha contract price (the sale price including markup).
3. Compute the profit margin.
4. Calculate the monthly installment amount (if relevant).
5. Provide the **initial journal entry** in Dr/Cr format:
   - Murabaha Receivable (gross sale price)
   - Inventory (asset cost)
   - Deferred Profit (difference to be amortized)
6. Ensure deferred profit is correctly identified and placed as a contra-asset to the receivable.
7. Do not include explanations—only the values and entries.

Scenario:
{scenario}
""")
musharakah_prompt = PromptTemplate(input_variables=["scenario"], template="""
You are an Islamic finance accounting expert.

Based on the Musharakah scenario below, apply AAOIFI FAS 4 and Shari’ah Standard No. 12 to generate the correct financial and accounting treatment from the perspective of the Islamic bank.

Follow these steps:

1. Identify the capital contributions of each party and deduce the ownership percentages.
2. Use the profit-sharing ratio provided in the scenario.
3. If the loss-sharing ratio is not mentioned, assume it follows the capital contribution proportions (as per Shari’ah).
4. For each year in the scenario:
   - Determine the net profit or loss.
   - Allocate the bank’s share based on the agreed profit ratio or capital ratio (as applicable).
5. Calculae the total benifit of the the bank through all the years of the contract (+ benifits and - losses).
6. If the bank’s share is transferred to the partner at the end (Diminishing Musharakah), compute:
   - The final sale amount
   - The total net gain/loss for the bank = (bank’s profit/loss share + sale price – initial capital)

Output:
- A table showing the bank’s annual share in profits or losses
- The bank’s cumulative net result
- The bank’s total gain or loss at the end of the Musharakah
- Journal entries:
   - At commencement (initial investment)
   - At liquidation or transfer of ownership

Only include calculations and journal entries. Avoid explanations.

Scenario:
{scenario}
""")

salam_prompt = PromptTemplate(input_variables=["scenario"], template="""
You are an Islamic finance accounting expert.

Using AAOIFI FAS 7 and Shari’ah Standard No. 10, analyze the Salam contract scenario below and generate the appropriate accounting treatment from the perspective of the Islamic bank.

Follow these steps:

1. Identify the amount of Salam capital (Ra's al-Mal) actually paid by the bank, the goods purchased (Al-Muslam Fihi), and the agreed delivery schedule.
2. If a Parallel Salam contract exists:
   - State the resale price and delivery timing.
   - Ensure the two Salam contracts are legally independent (no conditional linkage).
3. If the seller is authorized to resell the goods on behalf of the bank, calculate the final resale proceeds and profit.
4. Calculate the bank’s profit as: **Resale Price – Salam Capital Paid**.
   Do not consider the seller’s cost or margin — only use the bank’s actual payment.
5. Provide the following journal entries:
   - At Salam contract initiation
   - At execution of Parallel Salam (if applicable)
   - At delivery/fulfillment and revenue realization
6. If delivery fails, list the appropriate accounting treatments per standard (extension, receivable recognition, impairment).

Return only structured calculations and journal entries. Do not include any commentary or discussion.

Scenario:
{scenario}
""")
istisnaa_prompt = PromptTemplate(input_variables=["scenario"], template="""
You are an Islamic finance accounting expert.

Using AAOIFI Financial Accounting Standard No. 10 and Shari’ah Standard No. 11, analyze the Istisna’a scenario below and provide the correct accounting treatment from the Islamic bank’s perspective.

Perform the following:

1. Identify the roles: is the Islamic bank acting as the seller (Al-Sani’) or buyer (Al-Mustasni’)? Is there a Parallel Istisna’a with a subcontractor?
2. State:
   - Total contract value (to the client)
   - Construction cost (under parallel Istisna’a, if any)
   - Delivery terms and payment schedule
   - Whether the asset is sold or retained for Ijarah
3. Compute the bank’s profit as:
   - Total Istisna’a sale price – total construction cost
4. Revenue Recognition:
   - Apply the **percentage-of-completion method** if costs and completion can be reliably estimated
   - Otherwise, use the **completed contract method**
5. Journal Entries:
   - Construction phase (WIP/cost entries)
   - Revenue recognition and billing
   - Asset capitalization or derecognition (based on sale or lease)
   - Payment receipts or receivables from the client

6. If delivery is delayed or the subcontractor defaults, briefly indicate the accounting treatment (e.g., recognition of loss or receivable provisioning).

Only provide numeric breakdowns and journal entries. Do not include explanations or commentary.

Scenario:
{scenario}
""")

def get_prompt_for_contract_type(contract_type):
    if contract_type == "Ijarah":
        return ijarah_prompt
    elif contract_type == "Murabaha":
        return murabaha_prompt
    elif contract_type == "Musharakah":
        return musharakah_prompt
    elif contract_type == "Salam":
        return salam_prompt
    elif contract_type == "Istisna":
        return istisnaa_prompt
    else:
        raise ValueError(f"No prompt found for contract type: {contract_type}")

def parse_classifier_output(output):
    classification = None
    justification = None
    for line in output.strip().split('\n'):
        if line.lower().startswith("classification="):
            classification = line.split("=", 1)[1].strip()
        elif line.lower().startswith("justification="):
            justification = line.split("=", 1)[1].strip()
    return classification, justification

def process_finance_scenario(scenario_text: str):
    raw_output = classifier_chain.run(scenario=scenario_text)
    classification, justification = parse_classifier_output(raw_output)

    if classification == "Unknown":
        return {
            "classification": classification,
            "justification": justification,
            "journal_entry": "Contract type could not be identified."
        }

    selected_prompt = get_prompt_for_contract_type(classification)
    generator_chain = LLMChain(llm=llm, prompt=selected_prompt)
    journal_entry = generator_chain.run(scenario=scenario_text)

    return {
        "classification": classification,
        "justification": justification,
        "journal_entry": journal_entry
    }
