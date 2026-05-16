import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_articles(articles: list, category: str, reading_style: str = "short") -> dict:
    if not articles:
        return {"summaries": [], "brief": f"No articles found for {category}."}

    # Build article text for prompt
    article_text = ""
    for i, a in enumerate(articles, 1):
        title = a.get("title", "")
        desc = a.get("description", "")
        source = a.get("source", "")
        article_text += f"\nArticle {i}:\nTitle: {title}\nDescription: {desc}\nSource: {source}\n"

    length_instruction = "2-3 sentences" if reading_style == "short" else "4-5 sentences"

    prompt = f"""You are a professional news editor creating a daily brief for {category} news.

Here are {len(articles)} articles:
{article_text}

Your task:
1. Write a {length_instruction} summary for EACH article (numbered 1, 2, 3...)
2. Write 4-5 bullet point highlights as a consolidated brief

Use EXACTLY this format:

SUMMARIES:
1. [summary of article 1]
2. [summary of article 2]
3. [summary of article 3]

BRIEF:
- [highlight 1]
- [highlight 2]
- [highlight 3]
- [highlight 4]
"""

    try:
        print(f"\nCalling Groq for {category}...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a concise news editor. Always follow the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=600,
            timeout=30,
        )

        output = response.choices[0].message.content.strip()
        print(f"--- Groq output for {category} ---\n{output[:300]}\n---")

        summaries = []
        brief = ""

        if "SUMMARIES:" in output and "BRIEF:" in output:
            parts = output.split("BRIEF:")
            summary_block = parts[0].replace("SUMMARIES:", "").strip()
            brief = parts[1].strip()

            for line in summary_block.split("\n"):
                line = line.strip()
                if line and line[0].isdigit() and "." in line:
                    summary_text = line.split(".", 1)[-1].strip()
                    if summary_text:
                        summaries.append(summary_text)
        else:
            brief = output
            summaries = [a.get("description", "")[:300] for a in articles]

        return {"summaries": summaries, "brief": brief}

    except Exception as e:
        print(f"Groq error for {category}: {e}")
        summaries = [a.get("description", "")[:300] for a in articles]
        brief = "• " + "\n• ".join([a.get("title", "") for a in articles])
        return {"summaries": summaries, "brief": brief}