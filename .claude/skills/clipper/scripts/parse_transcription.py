#!/usr/bin/env python3
"""
Parse video transcription JSON and extract sentences with timestamps.

Input: JSON file with 'sentences' array containing:
  - text: sentence content
  - start: start timestamp (seconds)
  - end: end timestamp (seconds)
  - duration: duration (seconds)
  - words: array of word-level timestamps

Output: JSON array of simplified sentence objects with timestamps
"""

import json
import sys
from typing import List, Dict, Any


def parse_transcription(input_file: str) -> List[Dict[str, Any]]:
    """
    Parse transcription JSON and extract sentence data.

    Args:
        input_file: Path to transcription JSON file

    Returns:
        List of sentence dictionaries with text, start, end, and duration
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'sentences' not in data:
        raise ValueError("Transcription JSON must contain 'sentences' array")

    sentences = []
    for idx, sentence in enumerate(data['sentences']):
        # Validate required fields
        required_fields = ['text', 'start', 'end']
        for field in required_fields:
            if field not in sentence:
                raise ValueError(f"Sentence {idx} missing required field: {field}")

        # Extract relevant data
        sentences.append({
            'index': idx,
            'text': sentence['text'].strip(),
            'start': float(sentence['start']),
            'end': float(sentence['end']),
            'duration': float(sentence.get('duration', sentence['end'] - sentence['start'])),
        })

    return sentences


def main():
    if len(sys.argv) != 2:
        print("Usage: python parse_transcription.py <transcription.json>", file=sys.stderr)
        print("\nParses video transcription and outputs simplified JSON with sentences and timestamps.", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        sentences = parse_transcription(input_file)

        # Output as JSON
        output = {
            'total_sentences': len(sentences),
            'total_duration': sentences[-1]['end'] if sentences else 0,
            'sentences': sentences
        }

        print(json.dumps(output, indent=2))

        # Print stats to stderr
        print(f"\n✓ Parsed {len(sentences)} sentences", file=sys.stderr)
        if sentences:
            print(f"✓ Duration: {sentences[-1]['end']:.2f} seconds ({sentences[-1]['end']/60:.1f} minutes)", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
