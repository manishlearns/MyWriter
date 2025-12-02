import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class StyleAnalyzer:
    def __init__(self, data_dir="data/style_examples"):
        self.data_dir = data_dir
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def load_articles(self):
        articles = []
        if not os.path.exists(self.data_dir):
            return articles
            
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt") or filename.endswith(".md"):
                with open(os.path.join(self.data_dir, filename), "r") as f:
                    articles.append(f.read())
        return articles

    def analyze_style(self):
        articles = self.load_articles()
        if not articles:
            return "No articles found to analyze. Using default professional style."

        # Concatenate a few articles (limit to avoid token limits if necessary)
        context = "\n\n---\n\n".join(articles[:5]) 

        prompt = ChatPromptTemplate.from_template("""
        You are an expert literary analyst. Analyze the following articles written by the same author.
        Identify the unique writing style, tone, voice, and structural patterns.The author's name is Jai thomas. He likes using hashtags throughout his articles and ocassional emojis.
        
        Focus on:
        1. **Tone**: Is it formal, casual, witty, serious, etc.?
        2. **Perspective**: First-person, third-person?
        3. **Structure**: Short paragraphs, bullet points, storytelling approach?
        4. **Vocabulary**: Simple, technical, flowery?
        5. **Hooks**: How do they start their posts?
        6. **specifics**: Are hashtags used , are Emojis used?
        Provide a concise "System Persona" description that I can give to an AI to make it write exactly like this author.
        
        Articles:
        {articles}
        """)

        # Mock if no API key or dummy key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "dummy":
             return "Professional, first-person, uses short sentences and bullet points. Optimistic tone."

        chain = prompt | self.llm | StrOutputParser()
        style_description = chain.invoke({"articles": context})
        print('Style Description: ', style_description)
        return style_description

if __name__ == "__main__":
    # Test the analyzer
    analyzer = StyleAnalyzer()
    print(analyzer.analyze_style())
