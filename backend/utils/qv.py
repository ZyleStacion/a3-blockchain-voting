import math

def calculate_cost(votes: int) -> int:
    """
    Quadratic Voting cost function.
    Cost = (votes^2)
    Example: 
        1 vote  -> 1 token
        2 votes -> 4 tokens
        3 votes -> 9 tokens
    """
    if votes < 0:
        raise ValueError("Votes must be non-negative")
    return votes * votes

def max_votes(available_tokens: int) -> int:
    """
    Given available tokens, calculate the maximum number of votes
    a user can purchase under quadratic pricing.
    """
    if available_tokens < 0: #simple exception handling
        raise ValueError("Tokens must be non-negative")
    return int(math.floor(math.sqrt(available_tokens)))

if __name__ == "__main__":
    # Demo
    for tokens in [1, 4, 9, 10]:
        v = max_votes(tokens)
        print(f"With {tokens} tokens, max votes = {v} (cost of {v} votes = {calculate_cost(v)})")
