import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

#  or use a generic placeholder like "[INSERT PERSONAL STORY HERE]" if unsure

class Writer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # Higher temp for creativity

    def write_draft(self, topic_data, style_description, sample_draft):
        prompt = ChatPromptTemplate.from_template("""
        You are a ghostwriter for a LinkedIn influencer. Your goal is to write a viral LinkedIn article based on a specific topic, adopting a specific persona.
        
        # The Persona (Style Guide)
        {style_description}
        
        # The Topic (Source Material)
        Title: {title}
        Summary: {summary}
        Key Points: {key_points}
        Transcript Snippet: {transcript_snippet}
        
        # Instructions
        1. Write a LinkedIn article (post) about this topic.
        2. STRICTLY follow the persona described above. Use the same tone, sentence structure, and vocabulary.
        3. Incorporate the key points from the source material.
        4. Add a personal touch or story (invent a plausible one if needed).
        5. Use appropriate hashtags and emoji's.
        6. Format with short paragraphs and clear hooks, optimized for LinkedIn readability.
        7. '#StoriesWithJai' has to be present at the end. Also hashtags should be used throughout the article.
        8. use HASHTAGS heavily throughout the article not just at the end.(important)


        # Draft
        

        Below is a sample draft:
        {sample_draft}
        """)
        

        chain = prompt | self.llm | StrOutputParser()
        
        draft = chain.invoke({
            "style_description": style_description,
            "title": topic_data["video_title"],
            "summary": topic_data["summary"],
            "key_points": "\n".join(topic_data["key_points"]),
            "transcript_snippet": topic_data["transcript_snippet"],
            "sample_draft": sample_draft
        })
        
        return draft

if __name__ == "__main__":
    # Test the writer
    writer = Writer()
    sample_topic = {
        "video_title": "The Future of AI",
        "summary": "AI is changing everything.",
        "key_points": ["AI is fast", "AI is smart", "Humans need to adapt"],
        "transcript_snippet": "..."
    }
    sample_style = "Professional, concise, uses bullet points. Starts with a question."
    with open(Path(__file__).parent.parent.parent / "data" / "style_examples" / "sample4.txt", "r") as f:
        sample_draft = f.read()

    #print(sample_draft)
    print(writer.write_draft(sample_topic, sample_style, sample_draft))
