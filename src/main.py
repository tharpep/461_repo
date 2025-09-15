#!/usr/bin/env python3
"""Main entry point for the model scoring tool."""

import sys
import argparse
from typing import List, Optional

# Handle both relative and absolute imports for flexibility
try:
    from . import sub_scores, bus_factor
except ImportError:
    # Fallback for direct execution
    import sub_scores
    import bus_factor


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        description="Model scoring tool for evaluating Hugging Face models"
    )
    
    parser.add_argument(
        "model_url",
        help="Hugging Face model URL to evaluate"
    )
    
    parser.add_argument(
        "--license-only",
        action="store_true",
        help="Only compute license score"
    )
    
    parser.add_argument(
        "--bus-factor-only", 
        action="store_true",
        help="Only compute bus factor score"
    )
    
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as e:
        return e.code if e.code is not None else 1
    
    print(f"Evaluating model: {parsed_args.model_url}")
    print("=" * 50)
    
    try:
        if parsed_args.license_only:
            score, elapsed = sub_scores.license_sub_score(parsed_args.model_url)
            print(f"License Score: {score}")
            print(f"Computation time: {elapsed:.3f}s")
            
        elif parsed_args.bus_factor_only:
            score = bus_factor.bus_factor_score(parsed_args.model_url)
            print(f"Bus Factor Score: {score}")
            
        else:
            # Compute both scores
            license_score, license_elapsed = sub_scores.license_sub_score(parsed_args.model_url)
            bus_score = bus_factor.bus_factor_score(parsed_args.model_url)
            
            print(f"License Score: {license_score} (computed in {license_elapsed:.3f}s)")
            print(f"Bus Factor Score: {bus_score}")
        
        print("=" * 50)
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
