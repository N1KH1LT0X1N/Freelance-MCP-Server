"""
Freelance MCP Server - Quick Demo Entry Point

The simplest way to test the Freelance MCP Server.

Usage:
    python main.py
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """Main entry point for quick demo"""
    print("="*70)
    print("  Freelance MCP Server - Quick Start Demo")
    print("="*70)
    print()
    print("This will run a quick demonstration of the Freelance MCP Server.")
    print()
    print("Options:")
    print("  1. Run comprehensive demo (all features)")
    print("  2. Run quick demo (simplified)")
    print("  3. Check environment setup")
    print("  4. Exit")
    print()

    try:
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            print("\n🚀 Starting comprehensive demo...\n")
            from freelance_client import main as client_main
            await client_main()

        elif choice == "2":
            print("\n🚀 Starting quick demo...\n")
            from freelance_client2 import main as client2_main
            await client2_main()

        elif choice == "3":
            print("\n🔍 Checking environment...\n")
            from freelance_client import check_environment
            check_environment()

        elif choice == "4":
            print("\n👋 Goodbye!\n")
            return

        else:
            print("\n❌ Invalid choice. Please run again and select 1-4.\n")

    except ImportError as e:
        print(f"\n❌ Error: Missing required module - {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        print()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if required files exist
    if not Path("freelance_server.py").exists():
        print("\n❌ Error: freelance_server.py not found!")
        print("Please make sure you're running this from the project directory.\n")
        sys.exit(1)

    if not Path("freelance_client.py").exists():
        print("\n❌ Error: freelance_client.py not found!")
        print("Please make sure all project files are present.\n")
        sys.exit(1)

    # Run main
    asyncio.run(main())
