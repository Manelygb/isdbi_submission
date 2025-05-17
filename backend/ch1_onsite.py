# finance_ai_agent.py

import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI

# Set your OpenAI API key
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the model

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.4
)

# === Prompt: Classifier ===
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain.prompts import PromptTemplate

from langchain.prompts import PromptTemplate

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
"""
)

classifier_chain = LLMChain(llm=llm, prompt=classifier_prompt)

# === Prompt Templates for Each Contract ===

ijarah_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 10 (Ijarah and Ijarah Muntahia Bittamleek) and Shari’ah Standard No. 9.

Use the following AAOIFI reference context to support your reasoning:
{context}

Your task is to generate a complete, multi-stage accounting treatment from the **lessee’s perspective**, using the **Underlying Asset Cost Method** for an Ijarah Muntahia Bittamleek contract.

If any detail is ambiguous, you MUST rely on the context provided and never guess. Adhere strictly to AAOIFI treatments.

---

### A. Cost & Profit Computations

1. Compute the **total cost of the leased asset**, including all attributable costs (purchase, import, freight, etc.).
2. If ownership transfer is highly probable (e.g., via a purchase option), deduct the **purchase-option price** from the total cost to calculate the **Right-of-Use (ROU) Asset**.
3. Calculate the **total lease payments** over the full contract term.
4. Compute the **Deferred Ijarah Cost** = Total Lease Payments – ROU Asset.
5. Determine the **Terminal Value Difference** = Residual Value – Purchase Option.
6. Derive the **Amortizable Amount** = ROU Asset – Terminal Value Difference.

---

### B. Journal Entries

Provide detailed Dr/Cr entries for each stage:

**1. At Lease Commencement:**
- Dr. Right-of-Use Asset (ROU)
- Dr. Deferred Ijarah Cost (Expense – SFP)
- Cr. Ijarah Liability

**2. Annual Accrual of Rental & Income Recognition:**
- For each year:
   - Dr. Accrued Rent Receivable / Bank
   - Cr. Ijarah Income (P&L)

**3. (Optional) Ownership Transfer at End of Lease:**
- If ownership is transferred:
   - Dr. Ijarah Liability
   - Cr. Cash / Bank / Other Assets (at purchase price)

---

### C. Summary General Ledger Table

Use the following table format to summarize movements over the lease term:

| Account                        | Year 1 | Year 2 | Total |
|-------------------------------|--------|--------|-------|
| Right-of-Use Asset (ROU)      |   ...  |   –    |  ...  |
| Deferred Ijarah Cost          |   ...  |   –    |  ...  |
| Ijarah Liability              |   ...  |   ...  |  ...  |
| Ijarah Income (P&L)           |   ...  |   ...  |  ...  |
| Accrued Rent Receivable / Bank|   ...  |   ...  |  ...  |

---

Present all outputs using markdown formatting. Do not invent values. If values are not provided, explain what should be done using AAOIFI logic.

**Scenario:**
{query}
"""
)

murabaha_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 28 (Murabaha and Deferred Payment Sales) and Shari’ah Standard No. 8.

Use the following AAOIFI reference context to guide your response:
{context}

Your task is to generate a complete multi-stage accounting treatment for the scenario below, **from the perspective of the Islamic bank (as seller)** in a deferred-payment Murabaha.

If any treatment or value is uncertain, refer strictly to the context and avoid speculation.

---

### A. Financial Breakdown

1. Compute the **Total Acquisition Cost**: purchase price + related charges (e.g., notary, transport, taxes).
2. State the **Murabaha Sale Price** (agreed with the customer).
3. Calculate the **Profit Margin** = Sale Price − Acquisition Cost.
4. Calculate:
   - Monthly Installment = Sale Price ÷ Contract Term
   - Monthly Profit Portion = Profit Margin ÷ Contract Term

---

### B. Journal Entries

Use proper Dr/Cr format and label each entry clearly.

**1. Purchase of Asset:**
- Dr. Murabaha Inventory (SFP)
- Cr. Cash / Supplier Payable (SFP)

**2. Sale under Murabaha (Deferred Payment):**
- Dr. Murabaha Receivable [total sale price] (SFP)
- Cr. Murabaha Revenue (IS)
- Dr. Cost of Goods Sold (IS)
- Cr. Murabaha Inventory (SFP)
- Cr. Deferred Profit (SFP)

**3. Monthly Profit Recognition:**
- Dr. Deferred Profit (SFP)
- Cr. Murabaha Income (IS)

**4. Monthly Installment Receipt:**
- Dr. Cash / Bank (SFP)
- Cr. Murabaha Receivable (SFP)

---

### C. Summary General Ledger Table

| Account                                | Month 1 | Months 2–n | Total       |
|----------------------------------------|---------|------------|-------------|
| Murabaha Inventory / Asset (SFP)       | Dr      | –          | Cost only   |
| Murabaha Receivable (SFP)              | Dr      | Cr monthly | Net 0       |
| Deferred Profit (SFP)                  | Cr      | Dr monthly | Net 0       |
| Murabaha Income (IS)                   | Cr      | Cr monthly | Total Profit|
| Cash / Bank (SFP)                      | Dr      | Dr monthly | Total Paid  |

---

Only include markdown-formatted output. Clearly separate IS vs. SFP accounts.

**Scenario:**  
{query}
"""
)

musharakah_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are an Islamic finance accounting expert with deep expertise in AAOIFI Financial Accounting Standard No. 4 (Musharakah) and Shari’ah Standard No. 12.

Use the following official AAOIFI context to guide your response:
{context}

Your task is to produce a complete accounting treatment for the Musharakah arrangement described below, **from the Islamic bank’s perspective**. Assume this is a **Diminishing Musharakah** unless otherwise stated.

If any rule, computation, or assumption is unclear, refer to the provided context and do not invent values or logic.

---

### A. Partnership Setup & Equity Breakdown

1. Identify the capital contribution of each party.
2. Determine equity ownership based on capital contributions.
3. Clarify the profit-sharing ratio (usually fixed in the contract).
4. Apply **capital ratio** for **loss-sharing**.
5. If it is a Diminishing Musharakah:
   - Define the **annual repurchase amount** from the client.
   - Show how the bank’s equity % decreases year by year.
   - Tabulate the equity share of the bank for each year.

---

### B. Profit & Loss Allocation (Year-by-Year)

For each year:
1. Use the provided **net profit or loss**.
2. Allocate profits using the **fixed contractual profit ratio** (e.g., 50/50).
3. Allocate losses using the **capital ratio**.
4. Build a table like:

| Year | Net Result | Bank Share (%) | Bank Share Amount |
|------|------------|----------------|-------------------|
|      |            |                |                   |

Also calculate:
- Total profit received
- Total losses borne
- Net margin = Profit – Loss

---

### C. Capital Repurchase by Client

1. If applicable, calculate:
   - Annual repurchase amount (DA)
   - Total capital recovered = Annual × Years
2. Create yearly entries that reflect:
   - Decrease in Musharakah Financing (SFP)
   - Increase in Musharakah Receivable

---

### D. Journal Entries

Prepare entries for:

**1. Capital Contribution by Bank (if in tranches)**  
   - Dr. Musharakah Financing  
   - Cr. Cash/Bank

**2. Bank’s Share of Profit or Loss (each year)**  
   - Dr. Cash/Receivable (if profit)  
   - Cr. Profit from Musharakah (IS)  
   - OR  
   - Dr. Loss from Musharakah (IS)  
   - Cr. Musharakah Financing (SFP)

**3. Client’s Repurchase of Bank’s Share (each year)**  
   - Dr. Musharakah Receivable  
   - Cr. Musharakah Financing

---

### E. Ledger Summary Table

| Account                                | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|----------------------------------------|--------|--------|--------|--------|--------|-------|
| Musharakah Financing (SFP)             |        |        |        |        |        |       |
| Musharakah Receivable (SFP)            |        |        |        |        |        |       |
| Profit from Musharakah Financing (IS)  |        |        |        |        |        |       |
| Loss from Musharakah Financing (IS)    |        |        |        |        |        |       |

---

Only return markdown-formatted output.

**Scenario:**  
{query}
"""
)


istisnaa_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 10 (Istisna’a) and Shari’ah Standard No. 11.

Use the official AAOIFI reference context below to guide your answer:
{context}

Your task is to generate a full multi-phase accounting treatment **from the perspective of the Islamic bank**, using the **percentage-of-completion method**.

Only follow standards-based reasoning. Do not estimate if information is unclear — instead, explain that the assumption requires support.

---

### A. Initial Contract Details

1. Clearly identify:
   - The bank’s role as **Seller (Al-Sani’)** under the Istisna’a with the client.
   - The bank’s role as **Buyer (Al-Mustasni’)** under any Parallel Istisna’a contract.
2. Report:
   - Total contract value with the client
   - Construction cost under Parallel Istisna’a
   - Timeline of construction and delivery
   - Payment schedule from client (post-delivery or otherwise)

---

### B. Step-by-Step Revenue Recognition (Quarterly)

Follow the **percentage-of-completion method** using cost-based progress recognition:

1. For each quarter (Q1 to Q4), provide:

   - Cumulative construction cost incurred
   - % Completion = Cumulative Cost ÷ Total Estimated Cost
   - Cumulative revenue = % × Sale Price
   - Cumulative profit = % × Total Profit
   - Incremental revenue = Cumulative revenue – Prior cumulative
   - Incremental cost = Cost this period
   - Incremental profit = Profit this period

---

### C. Journal Entries (By Quarter)

For each quarter (Q1–Q4), provide entries for:

1. Cost incurred (Dr. WIP, Cr. Payables)
2. Revenue and profit recognition (Dr. Receivable, Cr. Revenue + Profit)
3. Do **not** recognize cash inflow from the client during construction

Use **Dr/Cr format** and label clearly by quarter.

---

### D. Payment Collection (Post-Delivery)

Assume delivery is completed at Q4. Then:

1. Record four client payments (P1–P4), **starting after delivery**.
2. For each:
   - Dr. Cash / Bank
   - Cr. Istisna’a Receivable

Do **not** offset construction cost or profit here.

---

### E. Ledger Table (Q1 to Q4 + P1 to P4)

| Period  | WIP (Dr) | Receivable (Dr) | Revenue (Cr) | Cost of Sales (Dr) | Profit (Cr) | Payables (Cr) | Cash Received (Dr) |
|---------|----------|------------------|---------------|--------------------|--------------|----------------|---------------------|
| Q1      |          |                  |               |                    |              |                |                     |
| Q2      |          |                  |               |                    |              |                |                     |
| Q3      |          |                  |               |                    |              |                |                     |
| Q4      |          |                  |               |                    |              |                |                     |
| P1      | –        | –                | –             | –                  | –            | –              |                     |
| P2      | –        | –                | –             | –                  | –            | –              |                     |
| P3      | –        | –                | –             | –                  | –            | –              |                     |
| P4      | –        | –                | –             | –                  | –            | –              |                     |
| **Total**|          |                  |               |                    |              |                |                     |

---

All outputs must be clearly structured using **markdown formatting**.

**Scenario:**  
{query}
"""
)


salam_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 7 (Salam) and Shari’ah Standard No. 10.

Use the official AAOIFI context below to guide your response:
{context}

You are to generate a complete accounting treatment for the scenario below **from the perspective of the Islamic bank**. If any part of the treatment is unclear, you MUST consult the context above. Avoid making assumptions not grounded in the standards.

---

### A. Contract Details & Profit

1. Identify:
   - The Salam capital (Ra’s al-Mal) paid in advance by the bank.
   - The goods (Al-Muslam Fihi) and their delivery timeline.
   - Whether a Parallel Salam exists or the original seller will resell the goods.

2. Calculate:
   - The bank’s profit in each case: **Resale price – Salam capital**
   - (Optionally) the farmer's margin for reference only.

---

### B. Journal Entries – Both Resale Options

Prepare entries for both possible resale structures:

#### **1. Bank-Managed Parallel Salam**

- **a)** Initial Salam Contract:
   - Recognize the advance payment to the seller.
- **b)** Parallel Salam Execution:
   - Recognize receivable from final buyer + delivery obligation.
- **c)** Receipt of Goods:
   - Transfer value from Salam Financing to Inventory.
- **d)** Delivery to Final Buyer:
   - Recognize gain, derecognize inventory.

#### **2. Farmer-Managed Resale (Authorized by Bank)**

- **a)** Initial Salam Contract:
   - Same as above.
- **b)** Goods Receipt:
   - Inventory treatment, depending on ownership risk.
- **c)** Sale by Farmer:
   - Recognize cash inflow and gain in bank records.

---

### C. Summary Ledger Tables (Two Versions)

Provide one table for each structure:

#### Ledger 1: Bank-Managed Resale

| Stage/Event               | Dr Accounts        | Cr Accounts            | Amount |
|---------------------------|--------------------|------------------------|--------|
| Salam signing             | Salam Financing    | Cash / Bank Payable    |        |
| Parallel Salam contract   | Receivable         | Parallel Salam Liab.   |        |
| Goods from seller         | Salam Inventory    | Salam Financing        |        |
| Delivery to buyer         | Liab. settled      | Inventory + Gain       |        |

#### Ledger 2: Farmer-Managed Resale

| Stage/Event               | Dr Accounts        | Cr Accounts            | Amount |
|---------------------------|--------------------|------------------------|--------|
| Salam signing             | Salam Financing    | Cash / Bank Payable    |        |
| Goods from seller         | Salam Inventory    | Salam Financing        |        |
| Sale by farmer            | Cash / Receivable  | Inventory + Gain       |        |

---

Present all outputs using **markdown formatting** for clear display.

**Scenario:**  
{query}
"""
)


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
    for line in output['text'].strip().split('\n'):
        if line.lower().startswith("classification="):
            classification = line.split("=", 1)[1].strip()
        elif line.lower().startswith("justification="):
            justification = line.split("=", 1)[1].strip()
    return classification, justification

import os
import zipfile
import gdown
from dotenv import load_dotenv

# LangChain components
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

def download_faiss_index():
    file_id = "1AgwRNfoszgiuEremX2166oyBwHvVj2VH"
    output_zip = "index.zip"
    extract_to = "vector_storee"

    if not os.path.exists(os.path.join(extract_to, "index", "index.faiss")):
        print("Downloading FAISS index from Google Drive…")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_zip, quiet=False)

        print("Extracting index.zip…")
        with zipfile.ZipFile(output_zip, "r") as z:
            z.extractall(extract_to)
        os.remove(output_zip)
        print("Done.")

def load_retriever():
    # 1) ensure the local FAISS index is present
    download_faiss_index()

    # 2) load embeddings & vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = FAISS.load_local(
        "vector_storee/index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    # 3) return a Retriever you can plug into RetrievalQA
    return vector_store.as_retriever()

# build the global retriever once
retriever = load_retriever()
def process_finance_scenario(scenario_text: str):
    # — 1) Classify the scenario —
    raw_output = classifier_chain.invoke({"scenario": scenario_text})
    classification, justification = parse_classifier_output(raw_output)
    print(f"🔹 Classification: {classification}")

    if classification == "Unknown":
        return {
            "classification": classification,
            "justification": justification,
            "journal_entry": "Contract type could not be identified."
        }

    # — 2) Get the appropriate prompt template —
    selected_prompt = get_prompt_for_contract_type(classification)
    
    # — 3) Create a custom chain that bypasses validation issues —
    from langchain.chains import LLMChain
    from langchain_core.runnables import RunnablePassthrough
    
    # Format documents into context string
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create the final chain
    custom_qa_chain = (
        {"context": retriever | format_docs, "query": RunnablePassthrough()} 
        | LLMChain(
            llm=ChatOpenAI(model_name="gpt-4-turbo", temperature=0.4),
            prompt=selected_prompt
        )
    )

    # — 4) Execute the chain —
    try:
        result = custom_qa_chain.invoke(scenario_text)
        journal_entry = result["text"]
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        journal_entry = f"Error generating journal entry: {str(e)}"

    return {
        "classification": classification,
        "justification": justification,
        "journal_entry": journal_entry
    }

