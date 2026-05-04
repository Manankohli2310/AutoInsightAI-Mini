import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AIEngine:
    def __init__(self, basic_info, stats_snapshot, v1_insights):
        """
        AI Engine 2.0:
        - Uses stats_snapshot to prevent hallucinations.
        - Translates mathematical anomalies into business stories.
        - Provides grounded context for textual data.
        """
        self.basic_info = basic_info
        self.snapshot = stats_snapshot
        self.v1_insights = v1_insights

    def get_smart_summary(self):
        """Generates a domain-aware summary grounded in actual data ranges."""
        columns = self.basic_info['column_list']
        # We give the AI a 'Mathematical Fingerprint' of the top metrics
        stats_context = {k: v for k, v in list(self.snapshot.items())[:5]}
        
        prompt = f"""
        You are a Senior Data Consultant. 
        Dataset Structure: {columns}
        Mathematical Summary: {stats_context}
        
        Task:
        1. Identify the most likely business domain (e.g., E-commerce, Finance, Healthcare).
        2. State 2 high-level strategic questions this specific data can answer.
        
        Constraints: 
        - Max 80 words. 
        - Use **bolding** for key business terms.
        - Do not guess; use the provided statistical ranges to inform your answer.
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
        )
        return response.choices[0].message.content

    def enhance_insights(self):
        """Translates raw V1 findings into professional business narratives."""
        insights_str = "\n".join(self.v1_insights)
        stats_context = {k: v for k, v in list(self.snapshot.items())[:5]}

        prompt = f"""
        You are a Business Intelligence expert. 
        Raw Statistical Findings: 
        {insights_str}
        
        Statistical Background:
        {stats_context}
        
        Task:
        Rewrite these findings into professional, actionable insights.
        
        Rules:
        - Format: '**Heading**: Description'.
        - Explain 'Why it matters' for business strategy.
        - Keep each insight to exactly 2 sentences (max 25 words).
        - Use the background stats to add weight (e.g., 'With an average of X...').
        - Return 5-7 high-quality insights.
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content