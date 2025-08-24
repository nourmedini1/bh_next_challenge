"""
Test script for the Insurance Management API.
This script demonstrates how to interact with the API programmatically.
"""

import requests
import json
from typing import Optional


class InsuranceAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, email: str, password: str) -> bool:
        """Login and store JWT token."""
        url = f"{self.base_url}/api/v1/auth/login-json"
        data = {"email": email, "password": password}
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                print(f"✅ Login successful! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self) -> dict:
        """Get headers with authorization token."""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_user_profile(self):
        """Get current user profile."""
        url = f"{self.base_url}/api/v1/auth/me"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                profile = response.json()
                print(f"✅ User Profile: {json.dumps(profile, indent=2, default=str)}")
                return profile
            else:
                print(f"❌ Failed to get profile: {response.json()}")
        except Exception as e:
            print(f"❌ Profile error: {e}")
    
    def get_contracts(self, page: int = 1, size: int = 10):
        """Get user contracts."""
        url = f"{self.base_url}/api/v1/contracts?page={page}&size={size}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                contracts = response.json()
                print(f"✅ Contracts ({contracts['total']} total):")
                for contract in contracts['items']:
                    print(f"  - {contract['num_contrat']}: {contract['lib_produit']}")
                return contracts
            else:
                print(f"❌ Failed to get contracts: {response.json()}")
        except Exception as e:
            print(f"❌ Contracts error: {e}")
    
    def get_claims(self, page: int = 1, size: int = 10):
        """Get user claims."""
        url = f"{self.base_url}/api/v1/claims?page={page}&size={size}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                claims = response.json()
                print(f"✅ Claims ({claims['total']} total):")
                for claim in claims['items']:
                    print(f"  - {claim['num_sinistre']}: {claim['lib_type_sinistre']}")
                return claims
            else:
                print(f"❌ Failed to get claims: {response.json()}")
        except Exception as e:
            print(f"❌ Claims error: {e}")
    
    def test_health(self):
        """Test health endpoint."""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ Health check: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False


def main():
    """Run API tests."""
    print("🧪 Testing Insurance Management API\n")
    
    # Initialize client
    client = InsuranceAPIClient()
    
    # Test health endpoint
    if not client.test_health():
        print("❌ Server appears to be down. Make sure the API is running on http://localhost:8000")
        return
    
    print()
    
    # Test login
    email = input("Enter email (or press Enter for test@example.com): ").strip()
    if not email:
        email = "test@example.com"
    
    password = input("Enter password (or press Enter for testpassword): ").strip()
    if not password:
        password = "testpassword"
    
    if not client.login(email, password):
        print("❌ Cannot proceed without authentication")
        return
    
    print()
    
    # Test user profile
    client.get_user_profile()
    print()
    
    # Test contracts
    client.get_contracts()
    print()
    
    # Test claims
    client.get_claims()
    print()
    
    print("✅ API testing complete!")


if __name__ == "__main__":
    main()
