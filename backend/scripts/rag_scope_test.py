import os
import sys
import time
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

BASE_URL = "http://localhost:8000"

import uuid

def get_auth_token():
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "Password123!"
    try:
        # Create user
        user_payload = {
            "first_name": "Test", "last_name": "User", "email": email, 
            "password": password, "phone_number": "000000", 
            "date_of_birth": "1990-01-01", "gender": "Male", "location": "Morocco"
        }
        r_create = requests.post(f"{BASE_URL}/users/", json=user_payload)
        r_create.raise_for_status()
        
        # Login
        r = requests.post(
            f"{BASE_URL}/auth/login", 
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        r.raise_for_status()
        return r.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating: {e}")
        sys.exit(1)

def run_test(name, history, question, expected_intent_logic):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "question": question,
        "history": history
    }
    
    try:
        r = requests.post(f"{BASE_URL}/rag/chat", json=payload, headers=headers)
        r.raise_for_status()
        ans = r.json()["answer"]
        print(f"User: {question}")
        print(f"Assistant: {ans}")
        
        # Verify deterministic rejection
        if expected_intent_logic == "OUT_OF_SCOPE":
            assert "I can't help with unrelated topics" in ans, "Failed OUT_OF_SCOPE check"
            print("=> PASSED (OUT_OF_SCOPE)")
        elif expected_intent_logic == "GREETING":
            assert "What can I help you with" in ans, "Failed GREETING check"
            print("=> PASSED (GREETING)")
        else:
            # IN_SCOPE (should not return deterministic early return)
            assert "I can't help with unrelated topics" not in ans, "Falsely flagged as OUT_OF_SCOPE"
            assert "Of course! I'm the VillaStay assistant" not in ans or len(question.split()) > 4, "Falsely flagged as GREETING only"
            print(f"=> PASSED ({expected_intent_logic})")
            
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)

def main():
    print("Testing Intent Router Scope Guardrails...\n")

    # 1. Direct programming request -> OUT_OF_SCOPE
    run_test(
        "Direct programming request",
        [],
        "Can you solve this LeetCode problem: Two Sum?",
        "OUT_OF_SCOPE"
    )
    
    # 2. Programming request after 'can you help me?' -> OUT_OF_SCOPE
    run_test(
        "Programming after greeting (context awareness)",
        [
            {"role": "user", "content": "can you help me?"},
            {"role": "assistant", "content": "Of course! What can I help you with?"}
        ],
        "Can you solve this LeetCode problem: Reverse a Linked List?",
        "OUT_OF_SCOPE"
    )
    
    # 3. Math request -> OUT_OF_SCOPE
    run_test(
        "Math request",
        [],
        "Solve 2+x=3.",
        "OUT_OF_SCOPE"
    )
    
    # 4. VillaStay cancellation question -> IN_SCOPE
    run_test(
        "Cancellation question",
        [],
        "Can you explain the cancellation policy?",
        "IN_SCOPE"
    )
    
    # 5. VillaStay booking question -> IN_SCOPE
    run_test(
        "Booking question",
        [],
        "What can you tell me about my booking?",
        "IN_SCOPE"
    )
    
    # 6. VillaStay document question -> DOCUMENT
    run_test(
        "Document question",
        [],
        "Can you help me understand my rental agreement?",
        "IN_SCOPE"
    )
    
    # 7. Greeting -> GREETING
    run_test(
        "Greeting",
        [],
        "hello, can you help me?",
        "GREETING"
    )
    
    # 8. Help with cancellation -> IN_SCOPE, not OUT_OF_SCOPE
    run_test(
        "Help with cancellation",
        [],
        "Can you help me cancel my reservation?",
        "IN_SCOPE"
    )
    
    print("\nALL SCOPE AND INTENT TESTS PASSED ✅")

if __name__ == "__main__":
    main()
