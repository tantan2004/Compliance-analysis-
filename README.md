# 🛡 Compliance Analysis Tool

**Live Demo:** [compliance-analyzer.streamlit.app](https://compliance-analyzer.streamlit.app/)

The **Compliance Analysis Tool** is an AI-powered application that automatically checks policy documents for compliance violations. It identifies rule breaches, assesses threat levels, and generates contextual summaries using LLMs through a Retrieval-Augmented Generation (RAG) architecture built on LangChain.

---

##  Project Purpose

Organizations often struggle to manually audit lengthy policy documents against dynamic regulatory requirements. This tool automates that process by:

- Comparing uploaded policy files against a set of compliance rules (`rules.json`)
- Detecting potential **rule violations**
- Assigning **risk/threat levels**
- Generating **AI summaries** using LLMs

Built with a **LangChain RAG pipeline**, **Groq models**, **FAISS vector store**, and a user-friendly **Streamlit frontend**, the tool is ideal for compliance analysts, privacy officers, and developers.

---

##  Features

-  Rule-based violation detection
- ⚠Risk level classification (High, Medium, Low)
-  LLM-powered contextual understanding and summaries
-  Evaluation framework to assess model performance (`evaluation.py`)
-  Deployed and accessible online via Streamlit

---

##  Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python, LangChain
- **Model:** Groq-hosted LLMs
- **Vector Store:** FAISS
- **Document Retrieval:** RAG (Retrieval-Augmented Generation)

---

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tantan2004/Compliance-analyzer.git
   cd Compliance-analyzer
2.**Install dependencies**
pip install -r requirements.txt
Add your API key

3.**Create a .env file in the root directory**:
GROQ_API_KEY=your_groq_api_key
You may also need other environment variables depending on your embedding model or deployment.

4.**Run the app**
streamlit run app.py
