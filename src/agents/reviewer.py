import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
from dotenv import load_dotenv

class Reviewer:
    def __init__(self ):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    def review(self,draft):

        prompt = ChatPromptTemplate.from_template("""
        
        You are an expert Social Media Editor. Your task is to rewrite the provided **Draft** to change its hashtag style from "thematic" (tags at the end) to "inline" (tags inside sentences).

**Follow these steps strictly:**

1.  **Inline Integration:** Rewrite every paragraph to include **2-3 relevant hashtags** directly inside the sentences. 
    * *Method:* Convert important nouns or verbs into hashtags (e.g., change "guidance" to "#guidance").
    * *Constraint:* Do not simply add tags; the text must flow naturally.

2.  **Paragraph Cleanup:** Remove any standalone hashtags that currently sit at the end of individual paragraphs. 
    * *Exception:* Do NOT touch the block of hashtags at the very bottom of the entire article (the footer tags).

3.  **Mandatory Sign-off:** Ensure the very last element of the text is the hashtag #StoriesWithJai. If it is missing, add it.

4.  **Output:** Return **only** the updated text. Do not add conversational filler.
5.  Dont touch the emojis.
6.  Dont touch the hashtags at the end.
7. call to action should be at the end, just before the footer hashtags. It should be a short call to action.

***

**Example of Desired Change:**

*Input Paragraph:* "I reflected on my reactions. It was a story I revisit when I feel stuck. #Reflection #Growth"

*Output Paragraph:* "I #reflected on my reactions. It was a #story I revisit when I feel #stuck."

***

**Draft to Edit:**
{draft}
        """)

        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({"draft": draft})


