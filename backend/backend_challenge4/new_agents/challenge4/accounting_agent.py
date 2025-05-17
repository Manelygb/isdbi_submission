import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMChain
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "openai/gpt-4o-mini"

class AccountingAgent(BaseAgent):
    agent_name = "AccountingAgent"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.4)
        print(f"{self.agent_name} initialized.")

        # Prepare vector store path
        script_dir = os.path.dirname(__file__)
        self.vector_store_path = os.path.join(script_dir, "../../vector_storee/index")
        self.alternative_path = "vector_storee/index"

    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting accounting entries generation..."
        
        try:
            # Extract required information
            contract_draft = pco.get("contract_draft", {})
            selected_contract = pco.get("selected_contract_details", {})
            
            if not contract_draft or not selected_contract:
                raise ValueError("Missing contract draft or selected contract details in PCO")
            
            # Get contract content
            contract_content = contract_draft.get("content", "")
            if not contract_content:
                raise ValueError("Contract draft content is empty")
            
            # Get primary contract type
            primary_contract_type = selected_contract.get("primary_contract_type", "")
            if not primary_contract_type:
                raise ValueError("Primary contract type not specified in selected contract details")
            
            # Generate accounting entries
            accounting_entries = self._generate_accounting_entries(primary_contract_type, contract_content)
            
            # Update PCO with the accounting entries
            pco["accounting_entries_report"] = {
                "content": accounting_entries,
                "contract_type": primary_contract_type,
                "status": "completed"
            }
            
            pco["current_status"] = "pending_shariah_validation"
            pco["processing_log"][-1]["message"] = f"Accounting entries generation completed for {primary_contract_type} contract."
            
        except Exception as e:
            error_message = f"Error during accounting entries generation: {str(e)}"
            pco["accounting_entries_report"] = {
                "content": None,
                "status": "failed",
                "error": error_message
            }
            pco["current_status"] = "error_accounting_generation"
            pco["processing_log"][-1]["message"] = error_message
            print(f"Critical error in AccountingAgent: {e}")

    def _get_prompt_for_contract_type(self, contract_type: str) -> PromptTemplate:
        """Returns the appropriate prompt template for the given contract type."""
        contract_type = contract_type.lower()
        
        if "ijarah" in contract_type:
            return self._get_ijarah_prompt()
        elif "murabaha" in contract_type:
            return self._get_murabaha_prompt()
        elif "musharakah" in contract_type:
            return self._get_musharakah_prompt()
        elif "istisna" in contract_type:
            return self._get_istisnaa_prompt()
        elif "salam" in contract_type:
            return self._get_salam_prompt()
        else:
            # Default to a generic prompt if contract type is not recognized
            return self._get_generic_prompt()

    def _get_retriever(self):
        """Loads the FAISS vector store and returns a retriever."""
        try:
            # Try to load vector store from primary location
            try:
                embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
                vector_store = FAISS.load_local(
                    self.vector_store_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                return vector_store.as_retriever()
            except Exception as e:
                print(f"Unable to load from primary location, trying alternative: {e}")
                # Try alternative location
                embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
                vector_store = FAISS.load_local(
                    self.alternative_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                return vector_store.as_retriever()
        except Exception as e:
            print(f"Error loading vector store: {e}")
            # Return None if retriever can't be loaded
            return None

    def _generate_accounting_entries(self, contract_type: str, contract_content: str) -> str:
        """Generates accounting entries for the given contract type and content."""
        # Get appropriate prompt template for contract type
        prompt_template = self._get_prompt_for_contract_type(contract_type)
        
        # Try to get retriever for RAG
        retriever = self._get_retriever()
        
        # Format documents into context string if retriever is available
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        try:
            if retriever:
                # Create chain with RAG
                custom_qa_chain = (
                    {"context": retriever | format_docs, "query": RunnablePassthrough()} 
                    | LLMChain(
                        llm=self.llm,
                        prompt=prompt_template
                    )
                )
                result = custom_qa_chain.invoke(contract_content)
                return result["text"]
            else:
                # Fallback without RAG if retriever is not available
                result = LLMChain(
                    llm=self.llm,
                    prompt=prompt_template
                ).invoke({"query": contract_content, "context": "No additional context available."})
                return result["text"]
        except Exception as e:
            print(f"Error generating accounting entries: {e}")
            return f"Error generating accounting entries: {str(e)}"

    def _get_ijarah_prompt(self) -> PromptTemplate:
        """Returns the prompt template for Ijarah contracts."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 10 (Ijarah and Ijarah Muntahia Bittamleek) and Shari'ah Standard No. 9.

Use the following AAOIFI reference context to support your reasoning:
{context}

Your task is to generate a complete, multi-stage accounting treatment from the **lessee's perspective**, using the **Underlying Asset Cost Method** for an Ijarah Muntahia Bittamleek contract.

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

    def _get_murabaha_prompt(self) -> PromptTemplate:
        """Returns the prompt template for Murabaha contracts."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 28 (Murabaha and Deferred Payment Sales) and Shari'ah Standard No. 8.

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

    def _get_musharakah_prompt(self) -> PromptTemplate:
        """Returns the prompt template for Musharakah contracts."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert with deep expertise in AAOIFI Financial Accounting Standard No. 4 (Musharakah) and Shari'ah Standard No. 12.

Use the following official AAOIFI context to guide your response:
{context}

Your task is to produce a complete accounting treatment for the Musharakah arrangement described below, **from the Islamic bank's perspective**. Assume this is a **Diminishing Musharakah** unless otherwise stated.

If any rule, computation, or assumption is unclear, refer to the provided context and do not invent values or logic.

---

### A. Partnership Setup & Equity Breakdown

1. Identify the capital contribution of each party.
2. Determine equity ownership based on capital contributions.
3. Clarify the profit-sharing ratio (usually fixed in the contract).
4. Apply **capital ratio** for **loss-sharing**.
5. If it is a Diminishing Musharakah:
   - Define the **annual repurchase amount** from the client.
   - Show how the bank's equity % decreases year by year.
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

**2. Bank's Share of Profit or Loss (each year)**  
   - Dr. Cash/Receivable (if profit)  
   - Cr. Profit from Musharakah (IS)  
   - OR  
   - Dr. Loss from Musharakah (IS)  
   - Cr. Musharakah Financing (SFP)

**3. Client's Repurchase of Bank's Share (each year)**  
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

    def _get_istisnaa_prompt(self) -> PromptTemplate:
        """Returns the prompt template for Istisna'a contracts."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 10 (Istisna'a) and Shari'ah Standard No. 11.

Use the official AAOIFI reference context below to guide your answer:
{context}

Your task is to generate a full multi-phase accounting treatment **from the perspective of the Islamic bank**, using the **percentage-of-completion method**.

Only follow standards-based reasoning. Do not estimate if information is unclear — instead, explain that the assumption requires support.

---

### A. Initial Contract Details

1. Clearly identify:
   - The bank's role as **Seller (Al-Sani')** under the Istisna'a with the client.
   - The bank's role as **Buyer (Al-Mustasni')** under any Parallel Istisna'a contract.
2. Report:
   - Total contract value with the client
   - Construction cost under Parallel Istisna'a
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
   - Cr. Istisna'a Receivable

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

    def _get_salam_prompt(self) -> PromptTemplate:
        """Returns the prompt template for Salam contracts."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standard No. 7 (Salam) and Shari'ah Standard No. 10.

Use the official AAOIFI context below to guide your response:
{context}

You are to generate a complete accounting treatment for the scenario below **from the perspective of the Islamic bank**. If any part of the treatment is unclear, you MUST consult the context above. Avoid making assumptions not grounded in the standards.

---

### A. Contract Details & Profit

1. Identify:
   - The Salam capital (Ra's al-Mal) paid in advance by the bank.
   - The goods (Al-Muslam Fihi) and their delivery timeline.
   - Whether a Parallel Salam exists or the original seller will resell the goods.

2. Calculate:
   - The bank's profit in each case: **Resale price – Salam capital**
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

    def _get_generic_prompt(self) -> PromptTemplate:
        """Returns a generic prompt template for unrecognized contract types."""
        return PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are an Islamic finance accounting expert specialized in AAOIFI Financial Accounting Standards.

Use the following AAOIFI reference context to support your reasoning:
{context}

Your task is to generate a complete, multi-stage accounting treatment for the Islamic finance contract described in the scenario below. Based on the details in the scenario, determine the appropriate contract type and generate the corresponding accounting entries.

If any detail is ambiguous, you MUST rely on the context provided and never guess. Adhere strictly to AAOIFI treatments.

---

### A. Contract Identification and Analysis

1. Identify the type of Islamic contract being used.
2. Outline the key financial parameters of the contract.
3. Determine the appropriate accounting treatment according to AAOIFI standards.

---

### B. Journal Entries

Provide detailed Dr/Cr entries for each stage of the contract, including:

1. Initial recognition
2. Periodic entries (if applicable)
3. Completion/settlement entries

---

### C. Summary General Ledger Table

Provide a table summarizing the accounting movements over the contract term.

---

Present all outputs using markdown formatting. Do not invent values. If values are not provided, explain what should be done using AAOIFI logic.

**Scenario:**
{query}
"""
        )