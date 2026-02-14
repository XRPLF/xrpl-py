#!/usr/bin/env python3
"""
Setup script for confidential MPT support.

This script builds the C extension for confidential MPT operations.
Run this only if you need to use confidential MPT features.

Usage:
    python -m xrpl.core.confidential.setup
    
Or:
    python xrpl/core/confidential/setup.py
"""

import os
import sys
import subprocess


def main():
    """Build the mpt-crypto C extension."""
    print("=" * 80)
    print("Setting up Confidential MPT Support")
    print("=" * 80)
    print()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_script = os.path.join(script_dir, "build_mpt_crypto.py")
    
    # Check if build script exists
    if not os.path.exists(build_script):
        print(f"ERROR: Build script not found: {build_script}")
        sys.exit(1)
    
    print(f"Building C extension from: {build_script}")
    print()
    
    # Run the build script
    try:
        result = subprocess.run(
            [sys.executable, build_script],
            cwd=script_dir,
            check=True,
            capture_output=False,
        )
        
        print()
        print("=" * 80)
        print("✓ Confidential MPT setup completed successfully!")
        print("=" * 80)
        print()
        print("You can now use confidential MPT features:")
        print("  from xrpl.core.confidential import MPTCrypto")
        print()
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 80)
        print("✗ Confidential MPT setup failed!")
        print("=" * 80)
        print()
        print("Please check the error messages above.")
        print()
        print("Common issues:")
        print("  - Missing pre-compiled libraries for your platform")
        print("  - Missing C compiler or build tools")
        print("  - Missing cffi package (install with: pip install cffi)")
        print()
        return 1
    
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

