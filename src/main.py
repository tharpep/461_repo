#!/usr/bin/env python3
"""Simple model scoring tool - just enter model name and get complete NetScore."""

import sys

# Handle both relative and absolute imports for flexibility
try:
    from . import net_score_calculator
except ImportError:
    # Fallback for direct execution
    import net_score_calculator


def main() -> int:
    """Simple CLI: just provide model name and get complete NetScore."""
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <model_name>")
        print("Example: python main.py google/gemma-2b")
        return 1
    
    model_id = sys.argv[1]
    
    try:
        # Calculate complete NetScore with all metrics
        results = net_score_calculator.calculate_net_score(model_id)
        
        # Print formatted summary
        net_score_calculator.print_score_summary(results)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
