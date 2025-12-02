import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.graph import app

def visualize():
    print("Generating graph visualization...")
    
    # Get the graph object
    graph = app.get_graph()
    
    # Print Mermaid syntax
    print("\n--- Mermaid Syntax ---")
    print(graph.draw_mermaid())
    print("----------------------\n")
    
    # Generate PNG
    try:
        png_data = graph.draw_mermaid_png()
        output_file = "workflow_graph.png"
        with open(output_file, "wb") as f:
            f.write(png_data)
        print(f"Graph visualization saved to: {output_file}")
    except Exception as e:
        print(f"Could not generate PNG: {e}")
        print("Ensure you have the necessary dependencies installed (e.g., grandalf or graphviz).")

if __name__ == "__main__":
    visualize()
