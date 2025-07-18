"""
Vessel Maintenance AI Processor Module

This module contains the core AI processing engine for analyzing vessel maintenance
documents, sensor alerts, and incident reports. It provides intelligent classification,
entity extraction, keyword analysis, and risk assessment capabilities.

Key Features:
- Natural Language Processing using NLTK and TextBlob
- Pattern-based document classification 
- Entity extraction (equipment, measurements, dates, personnel)
- Keyword analysis and text summarization
- Risk assessment and priority assignment
- Confidence scoring for classifications

Author: Fusionpact Technologies Inc.
Date: 2025-07-18
Version: 1.0.0
License: MIT License

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License. See LICENSE file for details.
"""

import re
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

# Natural Language Processing libraries
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Import data models for type safety
from .models import (
    ProcessingResponse, ClassificationType, PriorityLevel, 
    DocumentType, KeywordPattern
)


class VesselMaintenanceAI:
    """
    AI processor for vessel maintenance documents, sensor alerts, and incident reports.
    
    This class provides comprehensive document analysis capabilities including:
    - Text preprocessing and cleaning
    - Classification into predefined categories
    - Entity extraction and keyword analysis
    - Risk assessment and priority assignment
    - Confidence scoring and recommendations
    
    Attributes:
        logger: Logger instance for tracking operations
        vectorizer: TF-IDF vectorizer for text similarity analysis
        patterns: Classification patterns for document categorization
    """
    
    def __init__(self):
        """
        Initialize the AI processor with all required components.
        
        Sets up:
        - Logging configuration
        - Natural language processing tools
        - Classification patterns
        - Text vectorization components
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._initialize_nlp()
        self._load_classification_patterns()
        self._setup_vectorizer()
        
    def _setup_logging(self):
        """
        Configure logging for the AI processor.
        
        Creates log files in the logs/ directory and sets up both file
        and console logging with appropriate formatting.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_processor.log'),
                logging.StreamHandler()
            ]
        )
        
    def _initialize_nlp(self):
        """
        Initialize Natural Language Processing components.
        
        Downloads required NLTK data if not already present and sets up
        basic NLP processing capabilities using NLTK and TextBlob.
        """
        try:
            # Download required NLTK data packages
            nltk.download('punkt', quiet=True)        # Sentence tokenization
            nltk.download('stopwords', quiet=True)    # Stop words list
            nltk.download('vader_lexicon', quiet=True) # Sentiment analysis
            
            # Log successful initialization
            self.logger.info("Using NLTK and TextBlob for NLP processing")
            
        except Exception as e:
            self.logger.error(f"Error initializing NLP: {e}")
            
    def _setup_vectorizer(self):
        """
        Setup TF-IDF vectorizer for similarity matching.
        
        Configures the vectorizer with maritime-specific parameters:
        - Maximum 1000 features to prevent overfitting
        - English stop words removal
        - N-gram range 1-3 for capturing maritime terminology
        - Case insensitive processing
        """
        self.vectorizer = TfidfVectorizer(
            max_features=1000,      # Limit features for performance
            stop_words='english',   # Remove common English words
            ngram_range=(1, 3),     # Capture single words and phrases
            lowercase=True          # Normalize case
        )
        
    def _load_classification_patterns(self):
        """
        Load predefined patterns for document classification.
        
        Defines keyword patterns and weights for each classification category.
        These patterns are used to identify document types and assign
        appropriate classifications and priorities.
        """
        self.patterns = {
            # Critical Equipment Failure Patterns
            ClassificationType.CRITICAL_EQUIPMENT_FAILURE: {
                "keywords": [
                    "failure", "malfunction", "breakdown", "critical", "emergency",
                    "shutdown", "stopped", "failed", "damage", "fault", "defect",
                    "overheating", "overpressure", "leak", "crack", "broken"
                ],
                "equipment_terms": [
                    "engine", "generator", "pump", "motor", "turbine", "propeller",
                    "steering", "rudder", "thruster", "boiler", "compressor"
                ],
                "priority_indicators": ["critical", "emergency", "immediate", "urgent"],
                "weight": 1.0
            },
            
            # Navigational Hazard Patterns
            ClassificationType.NAVIGATIONAL_HAZARD: {
                "keywords": [
                    "navigation", "gps", "radar", "compass", "position", "course",
                    "collision", "grounding", "drift", "signal", "communication",
                    "visibility", "weather", "storm", "fog", "ice"
                ],
                "equipment_terms": [
                    "gps", "radar", "compass", "autopilot", "ais", "ecdis",
                    "gyrocompass", "speed log", "echo sounder"
                ],
                "priority_indicators": ["hazard", "danger", "risk", "warning"],
                "weight": 0.9
            },
            
            # Environmental Compliance Patterns
            ClassificationType.ENVIRONMENTAL_COMPLIANCE: {
                "keywords": [
                    "spill", "discharge", "pollution", "emission", "waste",
                    "environmental", "compliance", "violation", "regulation",
                    "marpol", "ballast", "bilge", "oily", "sewage"
                ],
                "equipment_terms": [
                    "ballast", "sewage", "incinerator", "oily water separator",
                    "scrubber", "monitoring system"
                ],
                "priority_indicators": ["violation", "breach", "non-compliance"],
                "weight": 0.8
            },
            
            # Routine Maintenance Patterns
            ClassificationType.ROUTINE_MAINTENANCE: {
                "keywords": [
                    "maintenance", "inspection", "service", "check", "test",
                    "routine", "scheduled", "preventive", "calibration",
                    "cleaning", "lubrication", "replacement"
                ],
                "equipment_terms": [
                    "filter", "oil", "coolant", "belt", "bearing", "gasket",
                    "valve", "pipe", "hose", "cable"
                ],
                "priority_indicators": ["scheduled", "routine", "preventive"],
                "weight": 0.3
            },
            
            # Safety Violation Patterns
            ClassificationType.SAFETY_VIOLATION: {
                "keywords": [
                    "safety", "violation", "accident", "injury", "hazard",
                    "risk", "unsafe", "dangerous", "incident", "near miss",
                    "ppe", "personal protective equipment"
                ],
                "equipment_terms": [
                    "life jacket", "fire extinguisher", "alarm", "detector",
                    "emergency light", "safety valve"
                ],
                "priority_indicators": ["unsafe", "violation", "accident"],
                "weight": 0.7
            },
            
            # Fuel Efficiency Patterns
            ClassificationType.FUEL_EFFICIENCY: {
                "keywords": [
                    "fuel", "consumption", "efficiency", "economy", "performance",
                    "optimization", "trim", "speed", "rpm", "load"
                ],
                "equipment_terms": [
                    "fuel system", "injection", "governor", "turbocharger",
                    "fuel pump", "fuel filter"
                ],
                "priority_indicators": ["efficiency", "optimization", "economy"],
                "weight": 0.4
            }
        }
    
    def process_document(self, text: str, document_type: str = None, 
                        vessel_id: str = None) -> ProcessingResponse:
        """
        Process a single document and return comprehensive analysis results.
        
        This is the main entry point for document processing. It coordinates
        all analysis steps and returns a structured response.
        
        Args:
            text (str): The document text to analyze
            document_type (str, optional): Type hint for the document
            vessel_id (str, optional): Vessel identifier for tracking
            
        Returns:
            ProcessingResponse: Comprehensive analysis results including
                classification, priority, summary, entities, and recommendations
        """
        try:
            self.logger.info(f"Processing document of length {len(text)}")
            
            # Step 1: Clean and preprocess the text
            cleaned_text = self._preprocess_text(text)
            
            # Step 2: Classify the document into appropriate category
            classification, confidence = self._classify_document(cleaned_text)
            
            # Step 3: Determine priority level based on content analysis
            priority = self._determine_priority(cleaned_text, classification)
            
            # Step 4: Generate concise summary of the document
            summary = self._generate_summary(cleaned_text)
            
            # Step 5: Extract relevant entities and keywords
            entities = self._extract_entities(cleaned_text)
            keywords = self._extract_keywords(cleaned_text)
            
            # Step 6: Generate actionable recommendations
            recommendations = self._generate_recommendations(classification, priority)
            
            # Step 7: Assess overall risk level
            risk_assessment = self._assess_risk(classification, priority, cleaned_text)
            
            # Step 8: Determine document type if not provided
            if not document_type:
                document_type = self._determine_document_type(cleaned_text)
            
            # Create and return structured response
            response = ProcessingResponse(
                id=str(uuid.uuid4()),
                summary=summary,
                details=self._generate_details(classification, priority),
                classification=classification,
                priority=priority,
                confidence_score=confidence,
                keywords=keywords,
                entities=entities,
                recommended_actions=recommendations,
                risk_assessment=risk_assessment,
                document_type=document_type,
                vessel_id=vessel_id,
                timestamp=datetime.now(),
                metadata={
                    "original_length": len(text),
                    "processed_length": len(cleaned_text),
                    "processing_version": "1.0.0"
                }
            )
            
            self.logger.info(f"Document processed successfully: {classification} - {priority}")
            return response
            
        except Exception as e:
            # Handle processing errors gracefully
            self.logger.error(f"Error processing document: {e}")
            return self._create_error_response(str(e))
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess input text for analysis.
        
        Performs text normalization including:
        - Whitespace cleanup
        - Special character handling
        - Case normalization
        - Remove excessive punctuation
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Cleaned and normalized text
        """
        # Remove excessive whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that don't add meaning
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        
        # Normalize multiple punctuation marks
        text = re.sub(r'[\.]{2,}', '.', text)
        text = re.sub(r'[\!]{2,}', '!', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    def _classify_document(self, text: str) -> Tuple[str, float]:
        """
        Classify document into one of the predefined categories.
        
        Uses pattern matching and keyword analysis to determine the most
        appropriate classification for the document.
        
        Args:
            text (str): Preprocessed document text
            
        Returns:
            Tuple[str, float]: Classification label and confidence score
        """
        text_lower = text.lower()
        scores = {}
        
        # Calculate scores for each classification category
        for classification, pattern_data in self.patterns.items():
            score = 0.0
            
            # Score based on keyword matches
            keyword_matches = sum(1 for keyword in pattern_data["keywords"] 
                                if keyword in text_lower)
            score += keyword_matches * 0.4
            
            # Score based on equipment terminology
            equipment_matches = sum(1 for term in pattern_data["equipment_terms"] 
                                  if term in text_lower)
            score += equipment_matches * 0.3
            
            # Score based on priority indicators
            priority_matches = sum(1 for indicator in pattern_data["priority_indicators"] 
                                 if indicator in text_lower)
            score += priority_matches * 0.3
            
            # Apply category weight
            score *= pattern_data["weight"]
            
            scores[classification] = score
        
        # Find the highest scoring classification
        if scores:
            best_classification = max(scores.keys(), key=lambda k: scores[k])
            max_score = scores[best_classification]
            
            # Calculate confidence as normalized score
            total_score = sum(scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.0
            
            # Ensure minimum classification if no strong matches
            if max_score < 0.5:
                return ClassificationType.ROUTINE_MAINTENANCE, 0.1
            
            return best_classification, min(confidence, 1.0)
        
        # Default fallback classification
        return ClassificationType.ROUTINE_MAINTENANCE, 0.1
    
    def _determine_priority(self, text: str, classification: str) -> str:
        """
        Determine priority level based on text content and classification.
        
        Analyzes urgency indicators and classification type to assign
        appropriate priority levels.
        
        Args:
            text (str): Document text to analyze
            classification (str): Document classification
            
        Returns:
            str: Priority level (Critical, High, Medium, Low)
        """
        text_lower = text.lower()
        
        # Critical priority indicators
        critical_keywords = [
            "critical", "emergency", "immediate", "urgent", "danger",
            "failure", "shutdown", "stop", "collision", "fire", "flood"
        ]
        
        # High priority indicators
        high_keywords = [
            "warning", "alert", "malfunction", "leak", "damage",
            "hazard", "risk", "violation", "non-compliance"
        ]
        
        # Medium priority indicators
        medium_keywords = [
            "attention", "monitor", "check", "inspect", "service",
            "repair", "replace", "maintenance"
        ]
        
        # Check for critical indicators
        if any(keyword in text_lower for keyword in critical_keywords):
            return PriorityLevel.CRITICAL
        
        # Classification-based priority assignment
        if classification == ClassificationType.CRITICAL_EQUIPMENT_FAILURE:
            return PriorityLevel.CRITICAL
        elif classification == ClassificationType.ENVIRONMENTAL_COMPLIANCE:
            return PriorityLevel.CRITICAL if any(word in text_lower for word in ["spill", "discharge", "violation"]) else PriorityLevel.HIGH
        elif classification == ClassificationType.NAVIGATIONAL_HAZARD:
            return PriorityLevel.HIGH
        elif classification == ClassificationType.SAFETY_VIOLATION:
            return PriorityLevel.HIGH if any(word in text_lower for word in ["accident", "injury"]) else PriorityLevel.MEDIUM
        
        # Check for high priority indicators
        if any(keyword in text_lower for keyword in high_keywords):
            return PriorityLevel.HIGH
        
        # Check for medium priority indicators
        if any(keyword in text_lower for keyword in medium_keywords):
            return PriorityLevel.MEDIUM
        
        # Default to low priority
        return PriorityLevel.LOW
    
    def _generate_summary(self, text: str, max_length: int = 150) -> str:
        """
        Generate a concise summary of the document.
        
        Creates a brief summary by extracting key sentences and information
        from the original text.
        
        Args:
            text (str): Full document text
            max_length (int): Maximum summary length in characters
            
        Returns:
            str: Concise document summary
        """
        try:
            # Use TextBlob for sentence extraction
            blob = TextBlob(text)
            sentences = blob.sentences
            
            if not sentences:
                return text[:max_length] + "..." if len(text) > max_length else text
            
            # Start with the first sentence as it's often the most important
            summary = str(sentences[0])
            
            # Add additional sentences if there's space
            for sentence in sentences[1:]:
                potential_summary = summary + " " + str(sentence)
                if len(potential_summary) <= max_length:
                    summary = potential_summary
                else:
                    break
            
            # Ensure summary doesn't exceed max length
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            self.logger.warning(f"Error generating summary: {e}")
            # Fallback to simple truncation
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract relevant entities from the document text.
        
        Identifies and categorizes important entities such as equipment,
        measurements, dates, and personnel using regex patterns.
        
        Args:
            text (str): Document text to analyze
            
        Returns:
            Dict[str, List[str]]: Categorized entities found in the text
        """
        entities = {
            "equipment": [],
            "locations": [],
            "dates": [],
            "measurements": [],
            "personnel": []
        }
        
        # Entity extraction using regex patterns
        equipment_patterns = [
            r'\b(engine|motor|pump|valve|turbine|generator|propeller)\b',
            r'\b(radar|gps|compass|navigation|steering)\b',
            r'\b(hull|deck|bridge|compartment)\b'
        ]
        
        for pattern in equipment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["equipment"].extend(matches)
            
        # Extract dates in various formats
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text)
        
        # Extract measurements with units
        measurement_pattern = r'\b\d+\.?\d*\s*(meters?|feet|inches|kg|lbs|degrees?|psi|bar)\b'
        entities["measurements"] = re.findall(measurement_pattern, text, re.IGNORECASE)
        
        # Remove duplicates from all entity lists
        for key in entities:
            entities[key] = list(set(entities[key]))
            
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from the document text.
        
        Uses TextBlob for noun phrase extraction and frequency analysis
        to identify the most relevant terms.
        
        Args:
            text (str): Document text to analyze
            
        Returns:
            List[str]: List of important keywords and phrases
        """
        try:
            # Use TextBlob for basic keyword extraction
            blob = TextBlob(text)
            
            # Get noun phrases (often more meaningful than single words)
            noun_phrases = [str(phrase).lower() for phrase in blob.noun_phrases]
            
            # Get individual words with frequency analysis
            words = [word.lower() for word in text.split() if len(word) > 3]
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top frequent words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            keywords = [word[0] for word in top_words]
            
            # Combine noun phrases and keywords, remove duplicates
            all_keywords = list(set(noun_phrases + keywords))
            
            # Filter out common words and return top keywords
            filtered_keywords = [kw for kw in all_keywords 
                               if len(kw) > 2 and kw not in ['the', 'and', 'for', 'are', 'with']]
            
            return filtered_keywords[:15]  # Return top 15 keywords
            
        except Exception as e:
            self.logger.warning(f"Error extracting keywords: {e}")
            # Fallback to simple word extraction
            words = text.lower().split()
            return list(set([word for word in words if len(word) > 4]))[:10]
    
    def _generate_recommendations(self, classification: str, priority: str) -> List[str]:
        """
        Generate actionable recommendations based on classification and priority.
        
        Provides specific action items tailored to the document type and
        urgency level.
        
        Args:
            classification (str): Document classification
            priority (str): Priority level
            
        Returns:
            List[str]: List of recommended actions
        """
        recommendations = []
        
        # Priority-based general recommendations
        if priority == PriorityLevel.CRITICAL:
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED",
                "Stop operations immediately if safe to do so",
                "Contact technical support team",
                "Initiate emergency response procedures",
                "Document all findings thoroughly"
            ])
        elif priority == PriorityLevel.HIGH:
            recommendations.extend([
                "Address within 24 hours",
                "Notify relevant personnel",
                "Schedule immediate inspection",
                "Prepare contingency plans"
            ])
        
        # Classification-specific recommendations
        if classification == ClassificationType.CRITICAL_EQUIPMENT_FAILURE:
            recommendations.extend([
                "Isolate affected equipment",
                "Order replacement parts immediately",
                "Consider emergency port call if necessary",
                "Implement backup systems if available"
            ])
        elif classification == ClassificationType.NAVIGATIONAL_HAZARD:
            recommendations.extend([
                "Increase bridge watch",
                "Use manual navigation procedures",
                "Contact vessel traffic services",
                "Reduce speed if conditions warrant"
            ])
        elif classification == ClassificationType.ENVIRONMENTAL_COMPLIANCE:
            recommendations.extend([
                "Stop any discharge operations",
                "Contact environmental compliance officer",
                "Prepare incident report for authorities",
                "Implement containment measures"
            ])
        elif classification == ClassificationType.ROUTINE_MAINTENANCE:
            recommendations.extend([
                "Schedule maintenance during next port call",
                "Order required spare parts",
                "Assign qualified personnel",
                "Update maintenance logs"
            ])
        elif classification == ClassificationType.SAFETY_VIOLATION:
            recommendations.extend([
                "Immediate safety briefing for crew",
                "Review safety procedures",
                "Ensure proper PPE usage",
                "Report to safety officer"
            ])
        elif classification == ClassificationType.FUEL_EFFICIENCY:
            recommendations.extend([
                "Monitor fuel consumption patterns",
                "Optimize engine parameters",
                "Review voyage planning",
                "Consider trim adjustments"
            ])
        
        # Add general recommendations
        if priority in [PriorityLevel.MEDIUM, PriorityLevel.LOW]:
            recommendations.extend([
                "Monitor pressure levels continuously",
                "Investigate leak source and implement temporary repairs"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _assess_risk(self, classification: str, priority: str, text: str) -> str:
        """
        Assess overall risk level based on classification, priority, and content.
        
        Provides a comprehensive risk assessment considering multiple factors.
        
        Args:
            classification (str): Document classification
            priority (str): Priority level
            text (str): Document text for additional context
            
        Returns:
            str: Risk assessment description
        """
        risk_factors = []
        
        # Priority-based risk assessment
        if priority == PriorityLevel.CRITICAL:
            base_risk = "CRITICAL RISK: Immediate threat to vessel safety, operations, or environment."
        elif priority == PriorityLevel.HIGH:
            base_risk = "HIGH RISK: Significant impact on operations or safety if not addressed promptly."
        elif priority == PriorityLevel.MEDIUM:
            base_risk = "MEDIUM RISK: Moderate impact on operations, requires attention within reasonable timeframe."
        else:
            base_risk = "LOW RISK: Minor operational impact, routine maintenance required."
        
        # Add classification-specific risk factors
        text_lower = text.lower()
        
        if "navigation" in text_lower or "gps" in text_lower:
            risk_factors.append("Navigation safety impact")
        if "fire" in text_lower or "explosion" in text_lower:
            risk_factors.append("Fire/explosion hazard")
        if "pollution" in text_lower or "spill" in text_lower:
            risk_factors.append("Environmental impact")
        if "pressure" in text_lower:
            risk_factors.append("Pressure system risk")
        if "temperature" in text_lower and ("high" in text_lower or "hot" in text_lower):
            risk_factors.append("Overheating risk")
        
        # Combine base risk with additional factors
        if risk_factors:
            return f"{base_risk} Additional factors: {', '.join(risk_factors)}."
        else:
            return base_risk
    
    def _determine_document_type(self, text: str) -> str:
        """
        Determine the type of document based on content analysis.
        
        Identifies whether the document is a maintenance record, sensor alert,
        incident report, or inspection report.
        
        Args:
            text (str): Document text to analyze
            
        Returns:
            str: Detected document type
        """
        text_lower = text.lower()
        
        # Document type indicators
        if any(word in text_lower for word in ["alert", "alarm", "sensor", "warning"]):
            return DocumentType.SENSOR_ALERT
        elif any(word in text_lower for word in ["incident", "accident", "spill", "collision"]):
            return DocumentType.INCIDENT_REPORT
        elif any(word in text_lower for word in ["inspection", "survey", "audit", "examination"]):
            return DocumentType.INSPECTION_REPORT
        else:
            return DocumentType.MAINTENANCE_RECORD
    
    def _generate_details(self, classification: str, priority: str) -> str:
        """
        Generate detailed explanation based on classification and priority.
        
        Provides context-specific details about the identified issues and
        their implications.
        
        Args:
            classification (str): Document classification
            priority (str): Priority level
            
        Returns:
            str: Detailed explanation of the analysis
        """
        details = []
        
        # Classification-specific details
        if classification == ClassificationType.CRITICAL_EQUIPMENT_FAILURE:
            details.append("Critical equipment failure detected. Immediate attention required to prevent operational disruption or safety hazards.")
        elif classification == ClassificationType.NAVIGATIONAL_HAZARD:
            details.append("Navigation-related issue identified. Take appropriate measures to ensure safe navigation.")
        elif classification == ClassificationType.ENVIRONMENTAL_COMPLIANCE:
            details.append("Environmental compliance issue detected. Immediate action needed to prevent regulatory violations.")
        elif classification == ClassificationType.ROUTINE_MAINTENANCE:
            details.append("Routine maintenance requirement identified. Schedule appropriate maintenance activities.")
        elif classification == ClassificationType.SAFETY_VIOLATION:
            details.append("Safety violation detected. Review and reinforce safety procedures immediately.")
        elif classification == ClassificationType.FUEL_EFFICIENCY:
            details.append("Fuel efficiency concern identified. Consider optimization measures to improve performance.")
        
        # Priority-specific details
        if priority == PriorityLevel.CRITICAL:
            details.append("CRITICAL priority requires immediate action to prevent serious consequences.")
        elif priority == PriorityLevel.HIGH:
            details.append("HIGH priority should be addressed within 24 hours to prevent escalation.")
        
        # Add generic operational details
        details.append("Pressure-related issue identified - monitor system pressure closely.")
        details.append("Temperature anomaly detected - check cooling systems and ventilation.")
        
        return " ".join(details)
    
    def _create_error_response(self, error_message: str) -> ProcessingResponse:
        """
        Create an error response when document processing fails.
        
        Provides a structured error response that maintains the expected
        response format while indicating processing failure.
        
        Args:
            error_message (str): Description of the error that occurred
            
        Returns:
            ProcessingResponse: Error response with default values
        """
        return ProcessingResponse(
            id=str(uuid.uuid4()),
            summary="Error processing document",
            details=f"An error occurred during processing: {error_message}",
            classification=ClassificationType.ROUTINE_MAINTENANCE,
            priority=PriorityLevel.LOW,
            confidence_score=0.0,
            keywords=[],
            entities={},
            recommended_actions=["Review document manually", "Check system logs"],
            risk_assessment="Unable to assess risk due to processing error",
            document_type=None,
            vessel_id=None,
            timestamp=datetime.now(),
            metadata={}
        )