#!/usr/bin/env python3
"""Main entry point for the model scoring tool."""

import sys
import argparse
from typing import List, Optional

# Handle both relative and absolute imports for flexibility
try:
    from . import (
        license_sub_score, 
        bus_factor, 
        ramp_up_sub_score,
        performance_claims_sub_score,
        dataset_quality_sub_score,
        hugging_face_api
    )
except ImportError:
    # Fallback for direct execution
    import license_sub_score
    import bus_factor
    import ramp_up_sub_score
    import performance_claims_sub_score
    import dataset_quality_sub_score
    import hugging_face_api


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
        description="Model scoring tool for evaluating Hugging Face models",
        epilog="""
Examples:
  %(prog)s "google/gemma-2b"                    # Basic scores (license, bus-factor)
  %(prog)s "google/gemma-2b" --all-scores       # All available scores
  %(prog)s "google/gemma-2b" --license-only     # Only license score
  %(prog)s "google/gemma-2b" --ramp-up-only     # Only ramp-up time score
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "model_url",
        help="Hugging Face model URL to evaluate"
    )
    
    # Individual scoring options
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
    
    parser.add_argument(
        "--ramp-up-only",
        action="store_true",
        help="Only compute ramp-up time score"
    )
    
    parser.add_argument(
        "--performance-claims-only",
        action="store_true",
        help="Only compute performance claims score"
    )
    
    parser.add_argument(
        "--dataset-quality-only",
        action="store_true",
        help="Only compute dataset quality score"
    )
    
    # Comprehensive scoring options
    parser.add_argument(
        "--all-scores",
        action="store_true",
        help="Compute all available scores"
    )
    
    parser.add_argument(
        "--basic-scores",
        action="store_true",
        help="Compute basic scores (license, bus-factor) - default behavior"
    )
    
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as e:
        return int(e.code) if e.code is not None else 1
    
    print(f"Evaluating model: {parsed_args.model_url}")
    print("=" * 50)
    
    try:
        # Individual scoring options
        if parsed_args.license_only:
            score, elapsed = license_sub_score.license_sub_score(parsed_args.model_url)
            print(f"License Score: {score}")
            print(f"Computation time: {elapsed:.3f}s")
            
        elif parsed_args.bus_factor_only:
            score = bus_factor.bus_factor_score(parsed_args.model_url)
            print(f"Bus Factor Score: {score}")
            
        elif parsed_args.ramp_up_only:
            score, elapsed = ramp_up_sub_score.ramp_up_time_score(parsed_args.model_url)
            print(f"Ramp-up Time Score: {score}")
            print(f"Computation time: {elapsed:.3f}s")
            
        elif parsed_args.performance_claims_only:
            score, elapsed = performance_claims_sub_score.performance_claims_sub_score(parsed_args.model_url)
            print(f"Performance Claims Score: {score}")
            print(f"Computation time: {elapsed:.3f}s")
            
        elif parsed_args.dataset_quality_only:
            score, elapsed = dataset_quality_sub_score.dataset_quality_sub_score(parsed_args.model_url)
            print(f"Dataset Quality Score: {score}")
            print(f"Computation time: {elapsed:.3f}s")
            
        elif parsed_args.all_scores:
            # Compute all available scores
            print("Computing all available scores...")
            print("-" * 30)
            
            # License score
            license_score, license_elapsed = license_sub_score.license_sub_score(parsed_args.model_url)
            print(f"License Score: {license_score} (computed in {license_elapsed:.3f}s)")
            
            # Bus factor score
            bus_score = bus_factor.bus_factor_score(parsed_args.model_url)
            print(f"Bus Factor Score: {bus_score}")
            
            # Ramp-up time score
            ramp_score, ramp_elapsed = ramp_up_sub_score.ramp_up_time_score(parsed_args.model_url)
            print(f"Ramp-up Time Score: {ramp_score} (computed in {ramp_elapsed:.3f}s)")
            
            # Performance claims score
            perf_score, perf_elapsed = performance_claims_sub_score.performance_claims_sub_score(parsed_args.model_url)
            print(f"Performance Claims Score: {perf_score} (computed in {perf_elapsed:.3f}s)")
            
            # Dataset quality score
            dataset_score, dataset_elapsed = dataset_quality_sub_score.dataset_quality_sub_score(parsed_args.model_url)
            print(f"Dataset Quality Score: {dataset_score} (computed in {dataset_elapsed:.3f}s)")
            
        else:
            # Default behavior: compute basic scores (license and bus-factor)
            license_score, license_elapsed = license_sub_score.license_sub_score(parsed_args.model_url)
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
