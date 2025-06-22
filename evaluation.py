import os
import json
from analyzer import Analysis
from nltk.translate.bleu_score import sentence_bleu
from bert_score import score as bert_score

# Synthetic test cases for evaluation
test_cases = [
    {
        "text": "The company shares user data without explicit consent and does not use encryption.",
        "expected_rules": ["consent", "encryption"],
        "expected_risk": "High",
        "query": "Summarize all compliance risks",
        "expected_summary_keywords": ["consent", "encryption"]
    },
    {
        "text": "User information is collected but not shared. Encryption is applied.",
        "expected_rules": [],
        "expected_risk": "Low",
        "query": "Summarize all compliance risks",
        "expected_summary_keywords": []
    }
]

def evaluate_rule_based(analysis, text, expected_rules):
    analysis.raw_text = text  # Ensure text is available for rule_based_scan
    violations = analysis.rule_based_scan(text)
    matched_rules = [v["rule"].lower() for v in violations]

    true_positives = len(set(matched_rules) & set(expected_rules))
    precision = true_positives / len(matched_rules) if matched_rules else 1.0
    recall = true_positives / len(expected_rules) if expected_rules else 1.0
    return precision, recall, violations

def evaluate_risk_level(analysis, violations, expected):
    risk = analysis.assess_risk_level(violations)
    return risk == expected, risk

def evaluate_summary_keywords(summary, expected_keywords):
    summary = summary.lower()
    matched = [kw for kw in expected_keywords if kw in summary]
    return len(matched) / len(expected_keywords) if expected_keywords else 1.0

def evaluate_bleu(prediction, reference_keywords):
    if not reference_keywords:
        return 1.0
    return sentence_bleu([reference_keywords], prediction.lower().split())

def evaluate_bert(prediction, reference_keywords):
    reference = " ".join(reference_keywords) if reference_keywords else "ok"
    P, R, F1 = bert_score([prediction], [reference], lang="en", verbose=False)
    return F1[0].item()

def evaluate_llm_judgment(llm, summary, expected_keywords):
    prompt = f"""
You are a compliance expert.

The system generated this summary of risks:
\"\"\"{summary}\"\"\"

We expect it to mention or imply these risk types: {', '.join(expected_keywords)}.

Rate the summary on a scale of 1 to 5 for:
1. Correctness
2. Completeness
3. Clarity

Respond as: {{\"correctness\": X, \"completeness\": Y, \"clarity\": Z}}
"""
    try:
        response = llm.invoke(prompt)
        content = response if isinstance(response, str) else response.content
        result = json.loads(content.strip().replace("\n", ""))
        return result
    except Exception as e:
        print(f"LLM scoring error: {e}")
        return {"correctness": 0, "completeness": 0, "clarity": 0}

def main():
    analysis = Analysis(rule_file="rules.json")
    results = []

    for idx, case in enumerate(test_cases):
        print(f"\n[Test Case {idx+1}]")
        raw_text = case["text"]
        expected_rules = case["expected_rules"]
        expected_risk = case["expected_risk"]
        query = case["query"]
        expected_keywords = case["expected_summary_keywords"]

        # Evaluate rule-based
        p, r, violations = evaluate_rule_based(analysis, raw_text, expected_rules)
        print(f"Precision: {p:.2f}, Recall: {r:.2f}")

        # Evaluate risk level
        risk_correct, risk = evaluate_risk_level(analysis, violations, expected_risk)
        print(f"Expected Risk: {expected_risk}, Got: {risk}, Match: {risk_correct}")

        # Evaluate QA summary
        summary = analysis.ask_query(query)
        keyword_match_score = evaluate_summary_keywords(summary, expected_keywords)
        bleu = evaluate_bleu(summary, expected_keywords)
        bert = evaluate_bert(summary, expected_keywords)
        llm_scores = evaluate_llm_judgment(analysis.llm, summary, expected_keywords)

        print(f"Keyword Match Score: {keyword_match_score:.2f}")
        print(f"BLEU Score: {bleu:.2f}")
        print(f"BERTScore F1: {bert:.2f}")
        print(f"LLM Scores: {llm_scores}")

        results.append({
            "precision": p,
            "recall": r,
            "risk_level_match": risk_correct,
            "keyword_match": keyword_match_score,
            "bleu": bleu,
            "bert": bert,
            "llm_scores": llm_scores
        })

    print("\n===== Final Evaluation Summary =====")
    for i, res in enumerate(results):
        print(f"Test {i+1}:", res)

if __name__ == "__main__":
    main()
