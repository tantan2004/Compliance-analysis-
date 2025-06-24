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

Prerequisites

Python 3.8 or higher
Groq API key

Steps

Clone the repository
bash
git clone https://github.com/tantan2004/Compliance-analyzer.git
cd Compliance-analyzer

Install dependencies
bash
pip install -r requirements.txt

Configure environment variables
Create a .env file in the root directory:
env
GROQ_API_KEY=your_groq_api_key_here

ℹ️ Note: You may need additional environment variables depending on your embedding model or deployment configuration.


Run the application
bash
streamlit run app.py


 Evaluation
To test model performance on predefined policy documents and expected rule violations:
bashpython evaluation.py
The evaluation script provides comprehensive metrics:

✅ Precision and recall of rule-based matching
📊 Risk level accuracy compared to ground truth
🧠 LLM summary evaluation 

📌 Usage Guide
Getting Started

Launch the application:
bashstreamlit run app.py

Upload your policy document:

Supported formats: .txt, .pdf, .docx
Maximum file size: 200MB


Configure rules (optional):

Use the default rules.json file, or
Upload your custom rules configuration


Review results:

View detected rule violations
Check AI-generated risk levels
Read compliance issue summaries


