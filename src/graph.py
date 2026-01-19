from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated, Optional
import operator

from src.agents.stylist import StyleAnalyzer
from src.agents.researcher import Researcher
from src.agents.writer import Writer
from src.agents.publisher import Publisher
from src.agents.reviewer import Reviewer

# Define the State
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    style_persona: Optional[str]
    research_results: Optional[List[dict]]
    selected_topic: Optional[dict]
    draft: Optional[str]
    final_draft: Optional[str]
    image_options: Optional[List[dict]]
    selected_image: Optional[dict]
    scheduled_time: Optional[str]

# Initialize Agents
stylist = StyleAnalyzer()
researcher = Researcher()
writer = Writer()
publisher = Publisher()
from src.tools.unsplash_tool import UnsplashTool
from src.tools.serpapi_tool import SerpApiTool
unsplash = UnsplashTool()
serpapi = SerpApiTool()

# Define Nodes
def analyze_style_node(state: AgentState):
    print("--- Analyzing Style ---")
    persona = stylist.analyze_style()
    return {"style_persona": persona, "messages": ["Style analyzed"]}

def research_node(state: AgentState):
    print("--- Researching Topics ---")
    results = researcher.research()
    if not results:
        return {"research_results": [], "messages": ["No topics found"]}
    
    # For simplicity, pick the first topic. In a real app, user might select.
    # selected = results[0]
    return {"research_results": results, "messages": ["Research completed, waiting for topic selection"]}



from pathlib import Path

# ... (existing imports)

# ...

def write_node(state: AgentState):
    print("--- Writing Draft ---")
    topic = state.get("selected_topic")
    style = state.get("style_persona")
    
    if not topic or not style:
        return {"messages": ["Missing topic or style"]}
    
    # Load sample draft
    try:
        sample_draft_path = Path(__file__).parent.parent / "data" / "style_examples" / "sample5.txt"
        with open(sample_draft_path, "r") as f:
            sample_draft = f.read()
    except Exception as e:
        print(f"Error loading sample draft: {e}")
        # Fallback to empty string or handle appropriately
        sample_draft = ""

    draft = writer.write_draft(topic, style, sample_draft)
    print(f"DEBUG: Draft generated. Length: {len(draft) if draft else 'None'}")
    return {"draft": draft, "messages": ["Draft created"]}

def review_node(state: AgentState):
    print("--- Revisting draft ---")
    draft = state['draft']

    reviewer = Reviewer()
    final_draft = reviewer.review(draft)
    return {"final_draft": final_draft, "messages": ["Draft reviewed"]}





def image_finder_node(state: AgentState):
    print("--- Finding Images ---")
    topic = state.get("selected_topic", {})
    title = topic.get("video_title", "office productivity")
    draft = state.get("final_draft", "")
    
    print(f"DEBUG: Original title for image search: {title}")
    
    # Use LLM to generate a better search query
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_template("Convert the following video title into a simple, 1 or 2  word search query for a stock photo site (Unsplash).Try to capture the moat of the writing. Return ONLY the query. Title: {title}")
    chain = prompt | llm | StrOutputParser()
    
    try:
        search_query = chain.invoke({"title": title})
        print(f"DEBUG: Generated search query: {search_query}")
    except Exception as e:
        print(f"Error generating query: {e}")
        search_query = title

    # 1. Get Unsplash Images
    unsplash_images = unsplash.search_images(search_query) or []
    
    # 2. Get SerpApi Images
    serpapi_images = []
    try:
        # We need to map SerpApi results to our standard format
        raw_serp_results = serpapi.search(search_query)
        if raw_serp_results:
            for i in raw_serp_results:
                serpapi_images.append({
                    'thumb': i.get('thumbnail'), 
                    'author': i.get('source'), 
                    'url': i.get('original')
                })
    except Exception as e:
        print(f"Error fetching SerpApi images: {e}")

    # 3. Combine: Top 4 from Unsplash + Top 4 from SerpApi
    final_images = unsplash_images[:4] + serpapi_images[:4]
    
    print(f"DEBUG: Found {len(unsplash_images)} Unsplash and {len(serpapi_images)} SerpApi images.")
    
    if not final_images:
        # Ultimate fallback
        print("No images found from either source. Trying fallback 'business'.")
        final_images = unsplash.search_images("business") or []

    return {"image_options": final_images, "messages": [f"Found {len(final_images)} images"]}


def publish_node(state: AgentState):
    print("--- Publishing ---")
    draft = state.get("final_draft")
    selected_image = state.get("selected_image")
    scheduled_time = state.get("scheduled_time")
    
    if not draft:
        return {"messages": ["No draft to publish"]}
    
    image_url = selected_image["url"] if selected_image else None
    
    publisher.publish(draft, scheduled_time=scheduled_time, image_url=image_url)
    
    msg = "Published to LinkedIn" if not scheduled_time else f"Scheduled for {scheduled_time}"
    return {"messages": [msg]}

# Define the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("stylist", analyze_style_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", write_node)
workflow.add_node("publisher", publish_node)
workflow.add_node("review_node", review_node )
workflow.add_node("image_finder", image_finder_node)




# Add Edges
workflow.set_entry_point("stylist")
workflow.add_edge("stylist", "researcher")

def check_topics(state):
    if state.get("research_results"):
        return "writer"
    return END

workflow.add_conditional_edges(
    "researcher",
    check_topics,
    {
        "writer": "writer",
        END: END
    }
)

#workflow.add_edge("writer", "publisher")
workflow.add_edge("writer", "review_node")
workflow.add_edge("review_node", "image_finder")
workflow.add_edge("image_finder", "publisher")
workflow.add_edge("publisher", END)

from langgraph.checkpoint.memory import MemorySaver

# Compile the Graph with Interrupt and Checkpointer
# We interrupt BEFORE the publisher node to allow human review
checkpointer = MemorySaver()
# Adding interrupt_after to ensure we stop after review
app = workflow.compile(
    interrupt_before=["writer", "publisher"], 
    interrupt_after=["image_finder"],
    checkpointer=checkpointer
)





