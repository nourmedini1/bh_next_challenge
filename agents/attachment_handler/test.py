#!/usr/bin/env python3
# filepath: attachment_client.py
import os
import sys
import uuid
import json
import base64
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
    DataPart,
)

class AttachmentSecurityClient:
    """A2A client for sending files to the Attachment Handler for security scanning"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.httpx_client = None
        self.a2a_client = None
        
    async def initialize(self):
        """Initialize the A2A client"""
        self.httpx_client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for file processing
        
        try:
            # Get the agent card
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url,
            )
            agent_card = await resolver.get_agent_card()
            
            # Initialize A2A client
            self.a2a_client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=agent_card
            )
            
            print(f"✅ Connected to Attachment Handler agent at {self.base_url}")
            print(f"🤖 Agent: {agent_card.name}")
            print(f"📝 Description: {agent_card.description}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")
            return False
    
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Send a file to the agent for security scanning"""
        if not self.a2a_client:
            raise RuntimeError("Client not initialized. Call initialize() first.")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = len(file_content)
            
            # Try to determine MIME type
            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            
            # Base64 encode file content
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            
            # Create A2A message with file attachment
            message_payload = Message(
                role=Role.user,
                messageId=str(uuid.uuid4()),
                parts=[DataPart(
                    data={
                        "content": {
                            "file_data": {
                                "name" : file_name,
                                "size": file_size,
                                "declared_type": "text/plain",
                                "content": encoded_content
                            },
                            "type": "application/json"
                        }
                    }
                )],
            )
            
            request = SendMessageRequest(
                id=str(uuid.uuid4()),
                params=MessageSendParams(
                    message=message_payload,
                ),
            )
            
            # Send to agent
            print(f"\n🔍 Scanning file: {file_name} ({file_size:,} bytes, {mime_type})")
            print("⏳ Sending to Attachment Handler agent...")
            
            # Track timing
            start_time = datetime.now()
            response = await self.a2a_client.send_message(request)
            print(json.dumps(response.model_dump(), indent=2))
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # Parse response
            response_json = response.model_dump()
            
            # Try to find JSON content in the response parts
            result = None
            for part in response_json.get("result", {}).get("parts", []):
                if part.get("type") == "application/json" and "content" in part:
                    try:
                        result = json.loads(part["content"])
                        break
                    except:
                        pass
                elif "text" in part:
                    # Try to parse the text as JSON
                    try:
                        result = json.loads(part["text"])
                        break
                    except:
                        # If not JSON, keep as raw text
                        result = {"raw_response": part["text"]}
            
            if not result:
                result = {"error": "Could not parse agent response"}
            
            # Add timing information
            result["scan_time_seconds"] = elapsed
            
            return result
            
        except Exception as e:
            print(f"❌ Error scanning file: {e}")
            return {"error": str(e), "success": False}
    
    async def cleanup(self):
        """Clean up client resources"""
        if self.httpx_client:
            await self.httpx_client.aclose()
            self.httpx_client = None

def print_scan_results(results: Dict[str, Any], detailed: bool = False):
    """Pretty print the scan results"""
    print("\n" + "="*60)
    print("📊 ATTACHMENT SECURITY SCAN RESULTS")
    print("="*60)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Print high-level summary for each file
    for file_result in results.get("response_data", []):
        file_info = file_result.get("file", {})
        agent_result = file_result.get("agent_result", {})
        
        print(f"\n📄 File: {file_info.get('name', 'Unknown')}")
        print(f"   Size: {file_info.get('size', 0):,} bytes")
        print(f"   Type: {file_info.get('declared_type', 'Unknown')}")
        
        # Check if any security issues were found
        detections = []
        is_malicious = False
        
        # Check for embedded code detections
        if "detections" in agent_result:
            detections = agent_result.get("detections", [])
            is_malicious = agent_result.get("is_malicious", False)
            score = agent_result.get("score", 0)
            
            # Print summary status
            if is_malicious:
                print(f"\n🚨 SECURITY THREAT DETECTED - Score: {score:.2f}")
            else:
                print(f"\n✅ No serious threats detected - Score: {score:.2f}")
            
            # Print detection count by severity
            severities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for detection in detections:
                severity = detection.get("severity", "medium")
                severities[severity] = severities.get(severity, 0) + 1
                
            for severity, count in severities.items():
                if count > 0:
                    severity_marker = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🔵"
                    }.get(severity, "⚪")
                    print(f"   {severity_marker} {severity.upper()}: {count} detections")
        
        # Gateway validation issues
        if "valid" in agent_result and not agent_result.get("valid", True):
            print(f"\n🚫 Gateway validation failed: {agent_result.get('reason', 'Unknown')}")
            
        # Print detailed detections if requested
        if detailed and detections:
            print("\n📋 Detailed Detections:")
            for i, detection in enumerate(detections, 1):
                det_type = detection.get("type", "unknown")
                severity = detection.get("severity", "unknown").upper()
                details = detection.get("details", "No details")
                
                print(f"  {i}. [{severity}] {det_type}: {details}")
                
                # Show the matched content if available
                if "match" in detection:
                    match = detection["match"]
                    if len(match) > 60:
                        match = match[:57] + "..."
                    print(f"     Match: {match}")
                    
    # Print scan time
    scan_time = results.get("scan_time_seconds", 0)
    print(f"\n⏱️ Scan completed in {scan_time:.2f} seconds")
    print("="*60)

async def main():
    parser = argparse.ArgumentParser(description="Attachment Security Scanner Client")
    parser.add_argument("file", help="File to scan")
    parser.add_argument("--url", default="http://localhost:3001", help="Agent URL")
    parser.add_argument("--detailed", action="store_true", help="Show detailed results")
    
    args = parser.parse_args()
    
    client = AttachmentSecurityClient(base_url=args.url)
    
    try:
        if not await client.initialize():
            return 1
            
        results = await client.scan_file(args.file)
        print_scan_results(results, detailed=args.detailed)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    finally:
        await client.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))