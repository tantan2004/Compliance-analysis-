from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceBgeEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import json

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

class Analysis:
    def __init__(self, rule_file="rules.json"):
        self.llm = ChatGroq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True
        )
        self.vector_store = None
        with open(rule_file, "r", encoding="utf-8") as f:
            self.regex_rules = json.load(f)

    def load_documents(self, file_path):
        if file_path.endswith('.txt'):
            loader = TextLoader(file_path)
        elif file_path.endswith('.pdf'):
            loader = PyMuPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError("Unsupported file type")

        documents = loader.load()
        self.raw_text = "\n".join(doc.page_content for doc in documents)
        chunks = self.text_splitter.split_documents(documents)

        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        self.vector_store.save_local("faiss_index")

        self._setup_analysis_chain()
        print("Document processed and ready for questions")

    def _setup_analysis_chain(self):
        self.analysis_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=self.memory
        )

        tool_qa = Tool(
            name="ComplianceQA",
            func=self.analysis_chain.run,
            description="Use this tool to answer compliance questions from the uploaded document."
        )

        tool_rule = Tool(
            name="RuleScanner",
            func=lambda query: self.rule_based_scan(self.raw_text),
            description="Scans the document for rule violations using predefined regex rules."
        )

        tool_risk = Tool(
            name="RiskAssessor",
            func=lambda query: self.assess_risk_level(self.rule_based_scan(self.raw_text)),
            description="Assesses the overall compliance risk level."
        )

        self.agent = initialize_agent(
            tools=[tool_qa, tool_rule, tool_risk],
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

    def ask_query(self, query):
        return self.agent.run(query)

    def _extract_context(self, text, start, end, window=100):
        left = max(start - window, 0)
        right = min(end + window, len(text))
        return text[left:right]

    def rule_based_scan(self, text):
        flagged = []
        for label, pattern in self.regex_rules.items():
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                matched_text = match.group()
                context = self._extract_context(text, match.start(), match.end())
                prompt = f"In the following policy text, does this indicate a violation of '{label}'?\n\n\"{context}\""
                response = self.llm.invoke(prompt)
                flagged.append({
                    "rule": label,
                    "match": matched_text,
                    "context": context,
                    "llm_judgment": response
                })
        return flagged

    def assess_risk_level(self, violations):
        risk_score = 0
        for v in violations:
            rule = v["rule"].lower()
            if "breach" in rule or "encryption" in rule:
                risk_score += 3
            elif "consent" in rule or "data sharing" in rule:
                risk_score += 2
            else:
                risk_score += 1

        if risk_score >= 6:
            return "High"
        elif risk_score >= 3:
            return "Medium"
        else:
            return "Low"

    def analyze_file(self, file_path, query=None):
        self.load_documents(file_path)
        rule_violations = self.rule_based_scan(self.raw_text)
        risk_level = self.assess_risk_level(rule_violations)
        ai_summary = self.ask_query(query or "Summarize all compliance risks in the document.")
        return {
            "rule_based_violations": rule_violations,
            "ai_summary": ai_summary,
            "risk_level": risk_level
        }

def main():
    analysis = Analysis(rule_file="rules.json")

    file_path = input("Enter the path to the document file (default: example_policy.txt): ").strip()
    if not file_path:
        file_path = "example_policy.txt"

    query = input("Enter your compliance query (default: summarize risks): ").strip()
    if not query:
        query = "Summarize all compliance risks in the document."

    result = analysis.analyze_file(file_path, query)

    print("\n Rule-Based Violations:")
    for v in result["rule_based_violations"]:
        print(f"- Rule: {v['rule']}\n  Match: {v['match']}\n  LLM Verdict: {v['llm_judgment']}\n")

    print("AI Summary:\n", result["ai_summary"])
    print("Risk Level:", result["risk_level"])

if __name__ == "__main__":
    main()
