# api_client.py
import requests
import json
import re
from typing import Tuple, Optional

def fetch_rank_data(username: str, hashtag: str, region: str) -> Tuple[Optional[str], int]:
    """
    Fetches rank data from the Valorant API.

    Args:
        username: The in-game name of the player.
        hashtag: The player's hashtag.
        region: The player's region.

    Returns:
        A tuple containing the rank (str) and RR (int).
        Returns (None, 0) if data cannot be parsed.
    """
    api_url = f"https://valorantrank.chat/{region}/{username}/{hashtag}"
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()  # Will raise HTTPError for bad responses (4xx or 5xx)

    rank_val, rr_val = None, 0
    
    # Try parsing as JSON first
    try:
        api_data = response.json()
        data_payload = api_data.get('data', api_data)
        if isinstance(data_payload, dict) and 'rank' in data_payload:
            rank_val = data_payload.get('rank', 'Unranked')
            rr_val = data_payload.get('rr', 0)
        return rank_val, rr_val
    except json.JSONDecodeError:
        # If JSON fails, use the updated, more robust text parsing
        rank_text = response.text.strip()
        match = re.match(r'^(.*\S)\s+(\d+)\s*RR$', rank_text.replace(':', '').strip())
        if match:
            # This updated logic correctly extracts the rank name
            rank_val = match.group(1).strip()
            rank_val = re.sub(r'^.*\[(.*)\]$', r'\1', rank_val).strip()
            rr_val = int(match.group(2))
        else:
            rank_val = rank_text  # Fallback to the full text if regex fails
        return rank_val, rr_val