import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AIEngine:
    def __init__(self, basic_info, v1_insights):
        self.basic_info = basic_info
        self.v1_insights = v1_insights

    def get_smart_summary(self):
        columns = self.basic_info['column_list']
        prompt = f"""
        You are a Data Expert. Dataset columns: {columns}.
        Briefly tell me:
        1. What is the domain of this data?
        2. Two key business questions this data answers.
        Keep it under 80 words and use **bolding** for key terms.
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
        )
        return response.choices[0].message.content

    def enhance_insights(self):
        insights_str = "\n".join(self.v1_insights)
        prompt = f"""
        Transform these raw findings into professional business insights:
        {insights_str}
        
        Rules:
        - Use '**Heading**: Description' format.
        - Each insight should explain 'Why it matters'.
        - Use professional, actionable language.
        - Return a clean list of 5-7 insights.
        - Keep is short not more than 2 sentences (20-25 words).
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content