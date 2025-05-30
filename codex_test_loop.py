# codex_test_loop.py
# Helper script for running tests until they pass.
# See README "Contributing" section for details.


import subprocess
import time
import os

def install_requirements():
    """Install required packages before running tests."""
    print("Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)


def run_tests():
    print("Running tests...")
    result = subprocess.run(["pytest"], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return "failed" in result.stdout.lower() or "error" in result.stdout.lower()

def stage_commit_push():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "fix: auto-test adjustment"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

def loop_test_until_pass():
    install_requirements()
    for i in range(10):
        print(f"\n⏱️ Iteration {i + 1}...")
        if run_tests():
            print("🔴 Test failed. Waiting for AI or manual fix...")
            time.sleep(60)  # Wait for AI agent or human to fix it
        else:
            print("✅ Tests passed! Pushing changes to GitHub...")
            stage_commit_push()
            break
    else:
        print("❌ Tests never passed after 10 attempts.")

if __name__ == "__main__":
    loop_test_until_pass()
