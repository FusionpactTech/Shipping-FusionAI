#!/usr/bin/env python3
"""
Sample data generator for the Vessel Maintenance AI System
This script generates realistic vessel maintenance records, sensor alerts, and incident reports
for testing and demonstration purposes.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta

# Sample vessel maintenance records
MAINTENANCE_RECORDS = [
    """
    Vessel ID: MV-ATLANTIC-001
    Date: 2024-01-15
    
    Main Engine Maintenance Report:
    During routine inspection of main engine, discovered oil leak from cylinder head gasket.
    Engine temperature readings showing 5-degree increase over normal operating range.
    Oil pressure maintaining within acceptable limits but showing gradual decline over past week.
    Recommended immediate replacement of gasket and oil system check.
    Engine room bilge shows oil contamination requiring cleanup.
    """,
    
    """
    Sensor Alert - Navigation System
    Vessel: MV-PACIFIC-TRADER
    Alert Time: 2024-01-16 14:30 UTC
    
    GPS navigation system showing intermittent signal loss.
    Backup compass readings inconsistent with primary navigation.
    Radar display experiencing periodic blackouts during storm conditions.
    Bridge team reporting difficulty maintaining accurate position.
    Weather conditions: Heavy rain, 8-foot swells, visibility reduced to 2 nautical miles.
    """,
    
    """
    Incident Report - Environmental Compliance
    Vessel: MV-GLOBAL-CARRIER
    Incident Date: 2024-01-17
    
    Accidental fuel discharge during bunkering operations.
    Estimated 50 gallons of marine gas oil released into harbor waters.
    Immediate containment booms deployed around vessel.
    Port authorities notified and environmental response team activated.
    Crew implementing emergency response procedures.
    MARPOL Annex I violation requires immediate reporting to flag state.
    """,
    
    """
    Critical Equipment Failure Alert
    Vessel: MV-NORTH-STAR
    Date: 2024-01-18 02:15 UTC
    
    Generator #2 complete electrical failure during night watch.
    Emergency generator automatically engaged but showing unstable voltage output.
    Main propulsion system operating on backup power only.
    Hull stress monitors indicating increased vibration levels.
    Engineering team reports burning smell from electrical panel.
    Immediate port call required for electrical system inspection.
    """,
    
    """
    Routine Maintenance Schedule
    Vessel: MV-SOUTHERN-CROSS
    Date: 2024-01-19
    
    Monthly safety equipment inspection completed.
    Life jacket inspection: 2 jackets require replacement due to wear.
    Fire extinguisher pressure check: All systems operational.
    Emergency lighting test: Backup battery replacement needed in cargo hold.
    Lifeboat davit lubrication completed successfully.
    Water tank cleaning scheduled for next port call.
    """,
    
    """
    Safety Violation Report
    Vessel: MV-EASTERN-WIND
    Date: 2024-01-20
    
    Safety inspection revealed missing safety barriers on upper deck.
    Crew member reported near-miss incident during cargo operations.
    Fire alarm system showing fault codes in engine room sector.
    Emergency muster stations partially blocked by cargo containers.
    Safety officer recommends immediate corrective action before departure.
    ISM Code compliance review required.
    """,
    
    """
    Navigational Hazard Alert
    Vessel: MV-WESTERN-PRIDE
    Date: 2024-01-21 18:45 UTC
    
    Collision avoidance system detected underwater obstacle not shown on charts.
    Depth sounder readings inconsistent with charted depths in approach channel.
    Harbor pilot reports dredging operations may have altered channel.
    Vessel maintaining safe distance and reduced speed.
    Coast Guard notified of potential navigational hazard.
    """,
    
    """
    Engine Room Temperature Alert
    Vessel: MV-ARCTIC-EXPLORER
    Date: 2024-01-22
    
    Main engine cooling system showing elevated temperatures.
    Coolant levels dropping despite recent top-off.
    Heat exchanger performance degraded, requires cleaning.
    Engine room ventilation fans operating at maximum capacity.
    Thermal imaging shows hot spots on exhaust manifold.
    Reducing engine load to prevent damage.
    """,
    
    """
    Hull Inspection Report
    Vessel: MV-TROPICAL-BREEZE
    Date: 2024-01-23
    
    Underwater hull inspection revealed minor corrosion on port side plating.
    Anti-fouling coating showing wear at waterline.
    Propeller performance slightly reduced due to marine growth.
    No structural damage detected but monitoring required.
    Dry dock maintenance recommended within 6 months.
    """,
    
    """
    Fuel System Anomaly
    Vessel: MV-DESERT-WIND
    Date: 2024-01-24 11:20 UTC
    
    Fuel consumption rate 15% higher than normal for current voyage conditions.
    Fuel quality testing shows higher sulfur content than specified.
    Engine performance monitoring indicates incomplete combustion.
    Fuel filters requiring more frequent replacement.
    Investigation needed to determine if fuel contamination present.
    """
]

SENSOR_ALERTS = [
    """
    CRITICAL ALARM: Engine overpressure detected
    Vessel: MV-STORM-RIDER
    Sensor: Main Engine Pressure Monitor
    Reading: 125 PSI (Normal: 80-100 PSI)
    
    Automatic engine shutdown initiated to prevent damage.
    Backup propulsion systems activated.
    Engineering team investigating pressure relief valve malfunction.
    """,
    
    """
    WARNING: Bilge water level rising
    Vessel: MV-OCEAN-PEARL
    Sensor: Bilge Level Monitor - Engine Room
    
    Water level increased 6 inches in past 2 hours.
    Bilge pumps activated but unable to maintain normal levels.
    Source of water ingress under investigation.
    Hull integrity check recommended.
    """,
    
    """
    ALERT: Fire detection system activated
    Vessel: MV-CARGO-MASTER
    Location: Cargo Hold #3
    Sensor: Smoke Detection Array
    
    Elevated particulate levels detected in cargo compartment.
    Fire suppression system on standby.
    Crew conducting visual inspection of cargo hold.
    No visible flames or smoke reported.
    """,
    
    """
    ANOMALY: Fuel leak detection
    Vessel: MV-TRADE-WINDS
    Sensor: Hydrocarbon Detector - Fuel Tank Area
    
    Fuel vapor concentrations above normal threshold.
    Tank level monitoring shows gradual decrease.
    Potential leak in fuel line connections.
    Ventilation systems increased to maximum.
    """
]

def send_sample_data(base_url="http://localhost:8000"):
    """Send sample data to the vessel maintenance AI system"""
    print("🚢 Sending sample vessel maintenance data to AI system...")
    
    all_samples = MAINTENANCE_RECORDS + SENSOR_ALERTS
    
    for i, sample in enumerate(all_samples):
        try:
            print(f"\n📄 Processing sample {i+1}/{len(all_samples)}")
            
            response = requests.post(
                f"{base_url}/process/text",
                json={"text": sample},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Successfully processed - {len(results)} results generated")
                
                for result in results:
                    print(f"   🏷️  Classification: {result['classification']}")
                    print(f"   ⚠️  Priority: {result['priority']}")
                    print(f"   📋 Summary: {result['summary'][:100]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            
        # Add small delay between requests
        time.sleep(1)
    
    print("\n🎉 Sample data loading completed!")
    print(f"🌐 View results at: {base_url}")

def generate_real_time_alerts(base_url="http://localhost:8000", duration_minutes=5):
    """Generate real-time alerts for demonstration"""
    print(f"🔄 Generating real-time alerts for {duration_minutes} minutes...")
    
    emergency_scenarios = [
        "EMERGENCY: Engine room fire alarm activated. Crew evacuating engine compartment.",
        "CRITICAL: Main engine seized. Complete loss of propulsion. Dead in water.",
        "URGENT: Hull breach detected in cargo hold. Water ingress rate increasing.",
        "ALERT: GPS navigation system failure. Vessel operating on backup compass only.",
        "WARNING: Fuel contamination detected. Engine performance degraded.",
        "CRITICAL: Steering system hydraulic failure. Manual steering activated.",
        "EMERGENCY: Man overboard alarm. Search and rescue operations initiated.",
        "URGENT: Generator failure. Emergency power systems activated."
    ]
    
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    while datetime.now() < end_time:
        try:
            # Random delay between alerts (15-60 seconds)
            delay = random.randint(15, 60)
            time.sleep(delay)
            
            # Select random emergency scenario
            alert = random.choice(emergency_scenarios)
            vessel_id = f"MV-DEMO-{random.randint(100, 999)}"
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            full_alert = f"Vessel ID: {vessel_id}\nTimestamp: {timestamp}\n\n{alert}"
            
            response = requests.post(
                f"{base_url}/process/text",
                json={"text": full_alert},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"🚨 REAL-TIME ALERT: {results[0]['classification']} - {results[0]['priority']}")
            
        except Exception as e:
            print(f"⚠️  Alert generation error: {e}")
    
    print("✅ Real-time alert generation completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample data for Vessel Maintenance AI")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--realtime", action="store_true", help="Generate real-time alerts")
    parser.add_argument("--duration", type=int, default=5, help="Duration for real-time alerts (minutes)")
    
    args = parser.parse_args()
    
    print("🌊 Vessel Maintenance AI - Sample Data Generator")
    print("=" * 50)
    
    if args.realtime:
        generate_real_time_alerts(args.url, args.duration)
    else:
        send_sample_data(args.url)