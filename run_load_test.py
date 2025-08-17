#!/usr/bin/env python3
"""
Load Test Runner for Localization Manager Backend
"""

import subprocess
import sys
import time
import argparse


def run_load_test(users=10, spawn_rate=2, run_time=60, host="http://localhost:8000"):
    """Run the load test with specified parameters"""

    print(f"🚀 Starting load test with:")
    print(f"   Users: {users}")
    print(f"   Spawn Rate: {spawn_rate} users/second")
    print(f"   Duration: {run_time} seconds")
    print(f"   Target: {host}")
    print("-" * 50)

    # Build the locust command
    cmd = [
        "uv",
        "run",
        "locust",
        "--host",
        host,
        "--users",
        str(users),
        "--spawn-rate",
        str(spawn_rate),
        "--run-time",
        f"{run_time}s",
        "--headless",  # Run without web UI
        "--only-summary",  # Show only summary at the end
        "--locustfile",
        "locustfile.py",
    ]

    try:
        # Run the load test
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Load test completed successfully!")
        print("\n📊 Results:")
        print(result.stdout)

        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"❌ Load test failed with exit code {e.returncode}")
        print("Error output:")
        print(e.stderr)
        sys.exit(1)


def run_interactive_test(host="http://localhost:8000"):
    """Run interactive load test with web UI"""

    print(f"🌐 Starting interactive load test at {host}")
    print(
        "Open your browser to http://localhost:8089 to access the Locust web interface"
    )
    print("Press Ctrl+C to stop the test")

    cmd = ["uv", "run", "locust", "--host", host, "--locustfile", "locustfile.py"]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Load test stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Load test failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run load tests for Localization Manager Backend"
    )
    parser.add_argument(
        "--users", type=int, default=10, help="Number of users (default: 10)"
    )
    parser.add_argument(
        "--spawn-rate",
        type=int,
        default=2,
        help="Users spawned per second (default: 2)",
    )
    parser.add_argument(
        "--run-time",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)",
    )
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Target host (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive test with web UI"
    )

    args = parser.parse_args()

    if args.interactive:
        run_interactive_test(args.host)
    else:
        run_load_test(args.users, args.spawn_rate, args.run_time, args.host)


if __name__ == "__main__":
    main()
