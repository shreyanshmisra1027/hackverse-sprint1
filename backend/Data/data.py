stock_data = {
    "NVIDIA": {"price": 118.50, "change_pct": 3.2, "volume": "very high"},
    "TESLA": {"price": 245.30, "change_pct": -1.5, "volume": "high"},
    "TATAMOTORS": {"price": 950.00, "change_pct": 4.5, "volume": "normal"}
}

news = {
    "NVIDIA": "NVIDIA beats earnings estimates on strong AI chip demand",
    "TESLA": "Tesla deliveries fall short of analyst expectations this quarter",
    "TATAMOTORS": "Tata Motors reports record EV sales, beats delivery targets"
}

def search(query: str):
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    snippets_path = os.path.join(script_dir, "snippets.txt")
    with open(snippets_path, "r") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")

    query_words = query.lower().split()

    best_match = None
    best_score = 0
    best_source = None

    for block in blocks:
        lines = block.strip().split("\n")
        label = lines[0]
        text = " ".join(lines[1:])

        score = sum(1 for word in query_words if word in text.lower())

        if score > best_score:
            best_match = text
            best_score = score
            best_source = label

    return best_match, best_source

if __name__ == "__main__":
    chunk, source = search("Tesla margins")
    print("CHUNK:", chunk)
    print("SOURCE:", source)