"""
This module contains logic for matching a given string to Overwatch character quotes.
"""

from typing import List, Tuple
from random import shuffle
import re

from models import Quote, Match
from align import align_quote


def _normalize_and_tokenize(s: str) -> List[str]:
    """
    Lowercase the string, remove punctuation (except apostrophes), and split into word tokens.
    """

    s = s.lower()
    s = re.sub(r"[^a-z0-9']+", " ", s)
    tokens = s.split()
    return tokens


def find_quote_matches(input_string: str, quotes: List[Quote]) -> List[Match]:
    """
    Find the largest contiguous coverage of input_string by segments of quotes (from `quotes`),
    using as few matched segments as possible. Matches may be any contiguous sequence of whole words
    from a quote. Case and punctuation are ignored for matching; returned segments are normalized
    (lowercase, no punctuation).

    I literally don't know how this works, is was written completely by LLM (vibe-coding).
    """

    # Select only quotes in English
    quotes = [
        q
        for q in quotes
        for black_word in [
            "French",
            "Spanish",
            "German",
            "Russian",
            "Chinese",
            "Dutch",
            "Swedish",
            "Egyptian",
            "Arabic",
            "Japanese",
            "Samoan",
            "Korean",
        ]
        if black_word not in q.audio_url
    ]

    shuffle(quotes)

    # 1) Normalize and tokenize the input string
    input_tokens = _normalize_and_tokenize(input_string)
    n = len(input_tokens)

    # 2) For each quote, tokenize its text
    quote_tokens_list: List[List[str]] = []
    for q in quotes:
        qtoks = _normalize_and_tokenize(q.text)
        quote_tokens_list.append(qtoks)

    # 3) Precompute, for each position i in input_tokens, all possible matches:
    #    a match is (length_in_words, quote_index)
    matches_at: List[List[Tuple[int, int]]] = [[] for _ in range(n)]

    for i in range(n):
        w_in = input_tokens[i]

        for q_idx, qtoks in enumerate(quote_tokens_list):
            m = len(qtoks)
            # Find every start position k in the quote where qtoks[k] == w_in
            start_positions = [k for k, w in enumerate(qtoks) if w == w_in]
            best_len = 0
            # For each start, see how many words match in sequence
            for k in start_positions:
                length = 0
                while (
                    i + length < n
                    and k + length < m
                    and input_tokens[i + length] == qtoks[k + length]
                ):
                    length += 1
                if length > best_len:
                    best_len = length
            if best_len > 0:
                # Record the single best (longest) match for this quote at position i
                matches_at[i].append((best_len, q_idx))

    # 4) Build a DP array for contiguous matching:
    #    dp_contig[k] = (reach_index, segment_count, list_of_Match_objects)
    #    where 'reach_index' is the furthest index we can match if we start exactly at k
    #    and proceed by chaining matches without gaps; 'segment_count' is the minimum number
    #    of segments to get that reach. If no match starts at k, we cannot match k, so reach_index = k.
    dp_contig: List[Tuple[int, int, List[Match]]] = [(i, 0, []) for i in range(n + 1)]
    dp_contig[n] = (
        n,
        0,
        [],
    )  # Base case: at position n, we have matched nothing and we're "at" n

    for k in range(n - 1, -1, -1):
        shuffle(matches_at[k])  # Shuffle to ensure randomness in matches

        # If no match starts at k, we can't cover k, so our reach is k itself (zero coverage from k).
        if not matches_at[k]:
            dp_contig[k] = (k, 0, [])
            continue

        # Otherwise, try each match (length, q_idx) at k
        best_reach = k
        best_segs = 0
        best_matches_list: List[Match] = []

        for length, q_idx in matches_at[k]:
            next_k = k + length
            next_reach, next_segs, next_matches = dp_contig[next_k]
            total_reach = next_reach
            total_segs = 1 + next_segs

            # Decide if this is better: prefer larger total_reach; if tie, fewer segments
            if (total_reach > best_reach) or (
                total_reach == best_reach
                and (
                    best_matches_list
                    and total_segs < best_segs
                    or not best_matches_list
                )
            ):
                segment_str = " ".join(input_tokens[k : k + length])
                new_match = Match(quotes[q_idx], segment_str)
                best_reach = total_reach
                best_segs = total_segs
                best_matches_list = [new_match] + next_matches

        dp_contig[k] = (best_reach, best_segs, best_matches_list)

    # 5) Among all starting positions i, pick the one with the largest contiguous coverage (reach - i),
    #    breaking ties by fewer segments. If coverage is zero, skip.
    best_cov = 0
    best_segs_overall = 0
    best_match_list_overall: List[Match] = []

    for i in range(n):
        reach_i, segs_i, matches_i = dp_contig[i]
        coverage_i = reach_i - i
        if coverage_i == 0:
            continue
        if (coverage_i > best_cov) or (
            coverage_i == best_cov
            and (not best_match_list_overall or segs_i < best_segs_overall)
        ):
            best_cov = coverage_i
            best_segs_overall = segs_i
            best_match_list_overall = matches_i

    # Calculate the audio segments for the best matches
    for match in best_match_list_overall:
        match.audio_segment = align_quote(match.quote, match.quote_segment)

    return best_match_list_overall
