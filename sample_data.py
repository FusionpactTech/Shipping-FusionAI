#!/usr/bin/env python3
"""
Vessel Maintenance AI System - Sample Data Generator

This script generates realistic sample data for testing and demonstrating
the vessel maintenance AI system. It creates various types of maintenance
records, sensor alerts, and incident reports that showcase the system's
classification and analysis capabilities.

The script sends test documents to the running API server and displays
the AI analysis results, providing a comprehensive demonstration of
the system's features.

Usage:
    python sample_data.py

Requirements:
    - The main application server must be running on localhost:8000
    - The requests library must be installed

Author: Fusionpact Technologies Inc.
Date: 2025-07-18
Version: 1.0.0
License: MIT License

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License. See LICENSE file for details.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"
DEMO_DELAY = 2  # Seconds between requests for better demonstration

# Sample vessel maintenance records demonstrating different classification types
MAINTENANCE_RECORDS = [
    """
    Vessel ID: MV-ATLANTIC-001
    Date: 2024-01-15
    
    Main Engine Maintenance Report:
    During routine inspection of main engine, discovered oil leak from cylinder head gasket.
    Engine temperature readings showing 5-degree increase over normal operating range.
    Oil pressure maintaining within acceptable limits but showing gradual decline over past week.
    Recommended immediate replacement of gasket and full system pressure test.
    
    Crew: Chief Engineer Martinez, Assistant Engineer Thompson
    Equipment: Caterpillar 3516C Marine Engine
    """,
    
    """
    Vessel ID: MV-PACIFIC-STAR
    Date: 2024-01-20
    
    CRITICAL NAVIGATION SYSTEM FAILURE:
    GPS primary unit has completely failed during night watch. 
    Backup GPS showing intermittent signal loss.
    Radar system functioning but showing reduced range accuracy.
    Ship currently navigating using compass and paper charts.
    
    IMMEDIATE ASSISTANCE REQUIRED - Position uncertainty in heavy traffic area.
    
    Bridge Officer: Captain Rodriguez
    Location: 45°N 35°W (approximate)
    """,
    
    """
    Vessel ID: MV-CARGO-MASTER
    Date: 2024-01-25
    
    Environmental Incident Report:
    During fuel transfer operations in port, approximately 150 liters of marine diesel
    spilled into harbor waters due to hose connection failure. 
    
    Spill containment booms deployed immediately.
    Coast Guard and port authority notified as per MARPOL regulations.
    Environmental cleanup crew dispatched.
    
    This constitutes a breach of environmental compliance protocols.
    Full investigation and corrective measures required.
    
    Environmental Officer: Sarah Johnson
    Port: Rotterdam
    """,
    
    """
    Vessel ID: MV-OCEAN-BREEZE
    Date: 2024-01-30
    
    Routine Maintenance Schedule:
    Weekly inspection completed on all safety equipment.
    Life jackets - 48 units inspected, 3 require replacement
    Fire extinguishers - all pressure levels normal
    Emergency lighting - 2 units need battery replacement
    
    Scheduled for next port call maintenance:
    - Air filter replacement (due in 50 hours)
    - Oil change (due in 75 hours)
    - Pump bearing lubrication
    
    Maintenance Supervisor: Mike Chen
    """,
    
    """
    Vessel ID: MV-NORDIC-WIND
    Date: 2024-02-05
    
    Safety Violation Incident:
    Crew member found working on deck without proper personal protective equipment.
    No safety harness used while working near rail in rough sea conditions.
    
    Incident occurred during cargo securing operations.
    Immediate safety briefing conducted for all deck crew.
    Written warning issued to crew member.
    
    All safety protocols must be strictly enforced.
    
    Safety Officer: David Wilson
    """,
    
    """
    Vessel ID: MV-FUEL-EFFICIENT
    Date: 2024-02-10
    
    Fuel Efficiency Alert:
    Fuel consumption has increased by 15% over past voyage compared to normal operations.
    Current consumption: 45 tons/day (normal: 39 tons/day)
    
    Possible causes:
    - Hull fouling (last cleaning 8 months ago)
    - Engine performance degradation
    - Adverse weather conditions
    
    Recommend hull inspection and engine tuning during next dry dock.
    Consider speed optimization for remaining voyage.
    
    Chief Engineer: Anna Petrov
    """,
    
    """
    Vessel ID: MV-SENSOR-WATCH
    Date: 2024-02-15
    
    Sensor Anomaly Alert:
    Temperature sensors in engine room showing unusual readings:
    - Sensor A1: 95°C (normal: 75°C)
    - Sensor B2: Temperature fluctuating between 65-85°C
    - Cooling water pressure: 4.2 bar (normal: 5.5 bar)
    
    Manual temperature checks confirm elevated readings.
    Cooling system efficiency appears compromised.
    
    Recommend immediate cooling system inspection and pump check.
    
    Watch Engineer: Tom Anderson
    """,
    
    """
    Vessel ID: MV-STORM-RIDER
    Date: 2024-02-20
    
    Severe Weather Incident Report:
    Vessel encountered Force 9 gale conditions with 12-meter waves.
    During heavy rolling, cargo containers shifted causing:
    - Minor damage to container guides on deck
    - Loose lashing requiring immediate attention
    - Bridge window cracked from wave impact
    
    All crew accounted for and safe.
    Speed reduced to 8 knots for safety.
    ETA delayed by 6 hours.
    
    Master: Captain Lisa Chang
    Position: 52°N 15°W
    """,
    
    """
    Vessel ID: MV-MAINTENANCE-MASTER
    Date: 2024-02-25
    
    Preventive Maintenance Completion Report:
    Monthly maintenance schedule completed successfully:
    
    ✓ Engine oil analysis - results within normal parameters
    ✓ Fuel filters replaced - 3 primary, 2 secondary
    ✓ Steering gear lubrication completed
    ✓ Emergency generator tested - 30-minute full load test passed
    ✓ Fire suppression system inspection completed
    
    Next scheduled maintenance: March 25, 2024
    
    Chief Engineer: Roberto Silva
    """,
    
    """
    Vessel ID: MV-TECH-INNOVATION
    Date: 2024-03-01
    
    Equipment Malfunction Report:
    Autopilot system experiencing intermittent failures.
    System disconnects randomly every 2-3 hours requiring manual steering.
    Gyrocompass readings appear stable.
    
    Preliminary diagnosis suggests software corruption or sensor malfunction.
    Manual steering capabilities confirmed operational.
    
    Recommend technical support consultation at next port.
    
    Navigation Officer: Emma Thompson
    """
]

def print_banner():
    """Display the application banner and introduction."""
    print("\n" + "="*80)
    print("🚢 VESSEL MAINTENANCE AI SYSTEM - SAMPLE DATA DEMONSTRATION")
    print("="*80)
    print("\nThis demonstration will process various types of vessel maintenance")
    print("documents to showcase the AI system's classification capabilities.")
    print("\nDocument types included:")
    print("• Critical Equipment Failures")
    print("• Navigational Hazard Alerts") 
    print("• Environmental Compliance Breaches")
    print("• Routine Maintenance Records")
    print("• Safety Violation Reports")
    print("• Fuel Efficiency Alerts")
    print("• Sensor Anomaly Alerts")
    print("• Incident Reports")
    print("\n" + "-"*80)

def check_server_availability():
    """
    Check if the API server is running and accessible.
    
    Returns:
        bool: True if server is accessible, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and accessible")
            return True
        else:
            print(f"❌ API server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Unable to connect to API server: {e}")
        print("Please ensure the server is running on localhost:8000")
        return False

def process_document(text, vessel_id=None, document_type=None):
    """
    Process a single document through the API.
    
    Args:
        text (str): Document text to process
        vessel_id (str, optional): Vessel identifier
        document_type (str, optional): Type of document
    
    Returns:
        dict: API response or None if failed
    """
    try:
        payload = {
            "text": text,
            "vessel_id": vessel_id,
            "document_type": document_type
        }
        
        response = requests.post(
            f"{API_BASE_URL}/process/text", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error processing document: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def display_result(result, index):
    """
    Display the processing result in a formatted manner.
    
    Args:
        result (dict): Processing result from the API
        index (int): Document index for numbering
    """
    if not result:
        return
        
    print(f"\n📋 DOCUMENT {index + 1} ANALYSIS RESULTS:")
    print("-" * 50)
    
    # Basic information
    print(f"🏷️  Classification: {result.get('classification', 'Unknown')}")
    print(f"🚨 Priority: {result.get('priority', 'Unknown')}")
    print(f"📊 Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"📄 Document Type: {result.get('document_type', 'Unknown')}")
    
    # Summary and details
    print(f"\n📝 Summary:")
    print(f"   {result.get('summary', 'No summary available')}")
    
    # Risk assessment
    print(f"\n⚠️  Risk Assessment:")
    print(f"   {result.get('risk_assessment', 'No risk assessment available')}")
    
    # Keywords
    keywords = result.get('keywords', [])
    if keywords:
        print(f"\n🔑 Key Terms: {', '.join(keywords[:8])}{'...' if len(keywords) > 8 else ''}")
    
    # Entities
    entities = result.get('entities', {})
    if entities:
        print(f"\n🔍 Extracted Entities:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"   {entity_type.title()}: {', '.join(entity_list[:3])}{'...' if len(entity_list) > 3 else ''}")
    
    # Recommended actions
    recommendations = result.get('recommended_actions', [])
    if recommendations:
        print(f"\n💡 Recommended Actions:")
        for i, action in enumerate(recommendations[:5], 1):
            print(f"   {i}. {action}")
        if len(recommendations) > 5:
            print(f"   ... and {len(recommendations) - 5} more actions")
    
    print("\n" + "="*60)

def get_analytics():
    """
    Retrieve and display system analytics.
    
    Returns:
        dict: Analytics data or None if failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/analytics", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting analytics: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error getting analytics: {e}")
        return None

def display_analytics(analytics):
    """
    Display system analytics in a formatted manner.
    
    Args:
        analytics (dict): Analytics data from the API
    """
    if not analytics:
        return
        
    print("\n" + "="*80)
    print("📊 SYSTEM ANALYTICS SUMMARY")
    print("="*80)
    
    # Overall statistics
    print(f"📈 Total Documents Processed: {analytics.get('total_processed', 0)}")
    print(f"🚨 Critical Alerts: {analytics.get('critical_alerts', 0)}")
    
    # Classification breakdown
    classification_breakdown = analytics.get('classification_breakdown', {})
    if classification_breakdown:
        print(f"\n🏷️  Classification Breakdown:")
        for classification, count in classification_breakdown.items():
            print(f"   • {classification}: {count}")
    
    # Priority breakdown  
    priority_breakdown = analytics.get('priority_breakdown', {})
    if priority_breakdown:
        print(f"\n🚨 Priority Level Distribution:")
        for priority, count in priority_breakdown.items():
            print(f"   • {priority}: {count}")
    
    # Recent trends
    recent_trends = analytics.get('recent_trends', [])
    if recent_trends:
        print(f"\n📅 Recent Activity (Last 7 Days):")
        for trend in recent_trends[:7]:
            date = trend.get('date', 'Unknown')
            count = trend.get('count', 0)
            print(f"   • {date}: {count} documents")
    
    print("\n" + "="*80)

def main():
    """
    Main function to run the sample data demonstration.
    
    This function orchestrates the entire demonstration process including
    server checks, document processing, and analytics display.
    """
    # Display introduction
    print_banner()
    
    # Check if server is running
    if not check_server_availability():
        print("\n❌ Cannot proceed without server connection.")
        print("Please start the server with: python app.py")
        return
    
    # Process sample documents
    print(f"\n🔄 Processing {len(MAINTENANCE_RECORDS)} sample documents...")
    print("(Processing with 2-second delays for demonstration purposes)")
    
    successful_processes = 0
    
    for i, document in enumerate(MAINTENANCE_RECORDS):
        print(f"\n⏳ Processing document {i + 1}/{len(MAINTENANCE_RECORDS)}...")
        
        # Extract vessel ID from document if available
        vessel_id = None
        lines = document.strip().split('\n')
        for line in lines:
            if 'Vessel ID:' in line:
                vessel_id = line.split('Vessel ID:')[1].strip()
                break
        
        # Process the document
        result = process_document(
            text=document,
            vessel_id=vessel_id,
            document_type="Sample Data"
        )
        
        if result:
            display_result(result, i)
            successful_processes += 1
        else:
            print(f"❌ Failed to process document {i + 1}")
        
        # Add delay for demonstration purposes
        if i < len(MAINTENANCE_RECORDS) - 1:
            time.sleep(DEMO_DELAY)
    
    # Display summary
    print(f"\n✅ Successfully processed {successful_processes}/{len(MAINTENANCE_RECORDS)} documents")
    
    # Get and display analytics
    print("\n⏳ Generating analytics summary...")
    analytics = get_analytics()
    display_analytics(analytics)
    
    # Final message
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("\nThe Vessel Maintenance AI System has successfully processed various")
    print("types of maritime documents and provided intelligent classifications")
    print("and actionable recommendations.")
    print("\n💡 Next steps:")
    print("• Visit http://localhost:8000 for the web interface")
    print("• View analytics at http://localhost:8000/analytics")
    print("• Check system health at http://localhost:8000/health")
    print("• Review processing history at http://localhost:8000/history")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration interrupted by user.")
        print("Thank you for testing the Vessel Maintenance AI System!")
    except Exception as e:
        print(f"\n❌ Unexpected error during demonstration: {e}")
        print("Please check the server logs for more details.")