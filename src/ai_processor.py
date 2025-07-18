import re
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import (
    ProcessingResponse, ClassificationType, PriorityLevel, 
    DocumentType, KeywordPattern
)

class VesselMaintenanceAI:
    """AI processor for vessel maintenance documents, sensor alerts, and incident reports"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._initialize_nlp()
        self._load_classification_patterns()
        self._setup_vectorizer()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_processor.log'),
                logging.StreamHandler()
            ]
        )
        
    def _initialize_nlp(self):
        """Initialize NLP models and download required data"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Using basic NLP processing with NLTK and TextBlob
            self.logger.info("Using NLTK and TextBlob for NLP processing")
                
        except Exception as e:
            self.logger.error(f"Error initializing NLP: {e}")
            
    def _setup_vectorizer(self):
        """Setup TF-IDF vectorizer for similarity matching"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True
        )
        
    def _load_classification_patterns(self):
        """Load predefined patterns for classification"""
        self.patterns = {
            ClassificationType.CRITICAL_EQUIPMENT_FAILURE: [
                KeywordPattern(
                    pattern=r"(engine|motor|propeller|turbine).*(fail|breakdown|malfunction|critical|emergency)",
                    classification=ClassificationType.CRITICAL_EQUIPMENT_FAILURE,
                    priority=PriorityLevel.CRITICAL,
                    weight=2.0
                ),
                KeywordPattern(
                    pattern=r"(hull|structure).*(crack|breach|damage|compromise)",
                    classification=ClassificationType.CRITICAL_EQUIPMENT_FAILURE,
                    priority=PriorityLevel.CRITICAL,
                    weight=2.0
                ),
                KeywordPattern(
                    pattern=r"(power|electrical|generator).*(loss|outage|failure)",
                    classification=ClassificationType.CRITICAL_EQUIPMENT_FAILURE,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
                KeywordPattern(
                    pattern=r"(steering|rudder|navigation).*(fail|stuck|unresponsive)",
                    classification=ClassificationType.CRITICAL_EQUIPMENT_FAILURE,
                    priority=PriorityLevel.CRITICAL,
                    weight=2.0
                ),
            ],
            
            ClassificationType.NAVIGATIONAL_HAZARD: [
                KeywordPattern(
                    pattern=r"(radar|gps|compass).*(malfunction|error|inaccurate)",
                    classification=ClassificationType.NAVIGATIONAL_HAZARD,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
                KeywordPattern(
                    pattern=r"(visibility|fog|storm|weather).*(poor|reduced|hazardous)",
                    classification=ClassificationType.NAVIGATIONAL_HAZARD,
                    priority=PriorityLevel.MEDIUM,
                    weight=1.2
                ),
                KeywordPattern(
                    pattern=r"(collision|grounding|obstacle|hazard)",
                    classification=ClassificationType.NAVIGATIONAL_HAZARD,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
                KeywordPattern(
                    pattern=r"(charts|mapping|navigation).*(outdated|incorrect|error)",
                    classification=ClassificationType.NAVIGATIONAL_HAZARD,
                    priority=PriorityLevel.MEDIUM,
                    weight=1.4
                ),
            ],
            
            ClassificationType.ENVIRONMENTAL_COMPLIANCE: [
                KeywordPattern(
                    pattern=r"(emission|exhaust|pollution).*(exceed|violation|breach)",
                    classification=ClassificationType.ENVIRONMENTAL_COMPLIANCE,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
                KeywordPattern(
                    pattern=r"(oil|fuel|chemical).*(spill|leak|discharge)",
                    classification=ClassificationType.ENVIRONMENTAL_COMPLIANCE,
                    priority=PriorityLevel.CRITICAL,
                    weight=2.0
                ),
                KeywordPattern(
                    pattern=r"(ballast|waste|sewage).*(improper|illegal|violation)",
                    classification=ClassificationType.ENVIRONMENTAL_COMPLIANCE,
                    priority=PriorityLevel.HIGH,
                    weight=1.6
                ),
                KeywordPattern(
                    pattern=r"(marpol|imo|environmental).*(non.compliance|violation|breach)",
                    classification=ClassificationType.ENVIRONMENTAL_COMPLIANCE,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
            ],
            
            ClassificationType.ROUTINE_MAINTENANCE: [
                KeywordPattern(
                    pattern=r"(maintenance|service|inspection).*(due|overdue|scheduled)",
                    classification=ClassificationType.ROUTINE_MAINTENANCE,
                    priority=PriorityLevel.MEDIUM,
                    weight=1.0
                ),
                KeywordPattern(
                    pattern=r"(filter|oil|fluid).*(change|replace|service)",
                    classification=ClassificationType.ROUTINE_MAINTENANCE,
                    priority=PriorityLevel.LOW,
                    weight=0.8
                ),
                KeywordPattern(
                    pattern=r"(cleaning|painting|coating).*(required|needed)",
                    classification=ClassificationType.ROUTINE_MAINTENANCE,
                    priority=PriorityLevel.LOW,
                    weight=0.6
                ),
            ],
            
            ClassificationType.SAFETY_VIOLATION: [
                KeywordPattern(
                    pattern=r"(safety|security).*(violation|breach|non.compliance)",
                    classification=ClassificationType.SAFETY_VIOLATION,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
                KeywordPattern(
                    pattern=r"(fire|emergency|alarm).*(system|equipment).*(fail|malfunction)",
                    classification=ClassificationType.SAFETY_VIOLATION,
                    priority=PriorityLevel.CRITICAL,
                    weight=2.0
                ),
                KeywordPattern(
                    pattern=r"(life|safety).*(jacket|boat|equipment).*(missing|defective)",
                    classification=ClassificationType.SAFETY_VIOLATION,
                    priority=PriorityLevel.HIGH,
                    weight=1.8
                ),
            ]
        }
        
    def process_text(self, text: str, vessel_id: str = None) -> List[ProcessingResponse]:
        """Process input text and return analysis results"""
        try:
            self.logger.info(f"Processing text input of {len(text)} characters")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Detect document type
            doc_type = self._detect_document_type(cleaned_text)
            
            # Split text into segments if too long
            segments = self._segment_text(cleaned_text)
            
            results = []
            for i, segment in enumerate(segments):
                # Generate summary
                summary = self._generate_summary(segment)
                
                # Extract entities and keywords
                entities = self._extract_entities(segment)
                keywords = self._extract_keywords(segment)
                
                # Classify content
                classification, priority, confidence = self._classify_content(segment)
                
                # Generate detailed analysis
                details = self._generate_detailed_analysis(segment, classification)
                
                # Generate risk assessment
                risk_assessment = self._assess_risk(segment, classification, priority)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(classification, priority, segment)
                
                # Create response object
                response = ProcessingResponse(
                    id=str(uuid.uuid4()),
                    summary=summary,
                    details=details,
                    classification=classification,
                    priority=priority,
                    confidence_score=confidence,
                    keywords=keywords,
                    entities=entities,
                    recommended_actions=recommendations,
                    risk_assessment=risk_assessment,
                    document_type=doc_type,
                    vessel_id=vessel_id,
                    metadata={
                        "segment_index": i,
                        "total_segments": len(segments),
                        "original_length": len(text),
                        "processed_length": len(segment)
                    }
                )
                
                results.append(response)
                
            self.logger.info(f"Generated {len(results)} analysis results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            # Return a default error response
            return [ProcessingResponse(
                id=str(uuid.uuid4()),
                summary="Error processing document",
                details=f"An error occurred during processing: {str(e)}",
                classification=ClassificationType.ROUTINE_MAINTENANCE,
                priority=PriorityLevel.LOW,
                confidence_score=0.0,
                risk_assessment="Unable to assess risk due to processing error",
                recommended_actions=["Review document manually", "Check system logs"]
            )]
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess input text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        
        return text
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect the type of document based on content"""
        text_lower = text.lower()
        
        # Define document type indicators
        type_indicators = {
            DocumentType.MAINTENANCE_RECORD: ["maintenance", "service", "repair", "overhaul", "inspection"],
            DocumentType.SENSOR_ALERT: ["sensor", "alarm", "alert", "warning", "threshold", "anomaly"],
            DocumentType.INCIDENT_REPORT: ["incident", "accident", "emergency", "collision", "grounding"],
            DocumentType.INSPECTION_REPORT: ["inspection", "survey", "audit", "compliance", "certification"],
            DocumentType.COMPLIANCE_DOCUMENT: ["compliance", "regulation", "standard", "requirement", "certification"]
        }
        
        scores = {}
        for doc_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[doc_type] = score
            
        # Return the document type with the highest score
        if scores:
            return max(scores, key=scores.get)
        else:
            return DocumentType.MAINTENANCE_RECORD  # Default
    
    def _segment_text(self, text: str, max_length: int = 2000) -> List[str]:
        """Split long text into manageable segments"""
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence + ". "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "
        
        if current_segment:
            segments.append(current_segment.strip())
            
        return segments if segments else [text]
    
    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the text"""
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return "No content to summarize"
        
        # Score sentences based on keyword frequency
        word_freq = {}
        words = text.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sentence_scores = {}
        for sentence in sentences:
            words_in_sentence = sentence.lower().split()
            score = sum(word_freq.get(word, 0) for word in words_in_sentence)
            sentence_scores[sentence] = score
        
        # Return top 2-3 sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        summary = ". ".join([sent[0] for sent in top_sentences])
        
        return summary[:300] + "..." if len(summary) > 300 else summary
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
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
            
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text)
        
        # Extract measurements
        measurement_pattern = r'\b\d+\.?\d*\s*(meters?|feet|inches|kg|lbs|degrees?|psi|bar)\b'
        entities["measurements"] = re.findall(measurement_pattern, text, re.IGNORECASE)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
            
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Use TextBlob for basic keyword extraction
        blob = TextBlob(text)
        
        # Get noun phrases
        noun_phrases = [str(phrase).lower() for phrase in blob.noun_phrases]
        
        # Get individual words with high frequency
        words = [word.lower() for word in text.split() if len(word) > 3]
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word[0] for word in top_words]
        
        # Combine and deduplicate
        all_keywords = list(set(noun_phrases + keywords))
        
        return all_keywords[:15]  # Return top 15 keywords
    
    def _classify_content(self, text: str) -> Tuple[ClassificationType, PriorityLevel, float]:
        """Classify content into predefined categories"""
        text_lower = text.lower()
        
        scores = {}
        for classification, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern.pattern, text_lower, re.IGNORECASE))
                score += matches * pattern.weight
            scores[classification] = score
        
        if not scores or max(scores.values()) == 0:
            return ClassificationType.ROUTINE_MAINTENANCE, PriorityLevel.LOW, 0.3
        
        # Get the classification with highest score
        best_classification = max(scores, key=scores.get)
        max_score = scores[best_classification]
        
        # Determine priority based on classification and content
        priority = self._determine_priority(text_lower, best_classification)
        
        # Calculate confidence (normalized score)
        confidence = min(max_score / 10.0, 1.0)  # Normalize to 0-1
        confidence = max(confidence, 0.1)  # Minimum confidence
        
        return best_classification, priority, confidence
    
    def _determine_priority(self, text: str, classification: ClassificationType) -> PriorityLevel:
        """Determine priority level based on content and classification"""
        urgent_indicators = ["critical", "emergency", "immediate", "urgent", "danger", "failure"]
        high_indicators = ["important", "significant", "major", "serious", "breach"]
        
        urgent_count = sum(1 for indicator in urgent_indicators if indicator in text)
        high_count = sum(1 for indicator in high_indicators if indicator in text)
        
        if urgent_count > 0 or classification == ClassificationType.CRITICAL_EQUIPMENT_FAILURE:
            return PriorityLevel.CRITICAL
        elif high_count > 0 or classification in [ClassificationType.NAVIGATIONAL_HAZARD, ClassificationType.ENVIRONMENTAL_COMPLIANCE]:
            return PriorityLevel.HIGH
        elif classification == ClassificationType.SAFETY_VIOLATION:
            return PriorityLevel.HIGH
        else:
            return PriorityLevel.MEDIUM
    
    def _generate_detailed_analysis(self, text: str, classification: ClassificationType) -> str:
        """Generate detailed analysis based on classification"""
        analysis_templates = {
            ClassificationType.CRITICAL_EQUIPMENT_FAILURE: 
                "Critical equipment failure detected. Immediate attention required to prevent operational disruption or safety hazards.",
            ClassificationType.NAVIGATIONAL_HAZARD: 
                "Navigational hazard identified. This issue may impact safe navigation and requires prompt resolution.",
            ClassificationType.ENVIRONMENTAL_COMPLIANCE: 
                "Environmental compliance issue detected. Immediate action needed to prevent regulatory violations.",
            ClassificationType.ROUTINE_MAINTENANCE: 
                "Routine maintenance requirement identified. Schedule appropriate maintenance activities.",
            ClassificationType.SAFETY_VIOLATION: 
                "Safety violation detected. Immediate corrective action required to ensure crew and vessel safety."
        }
        
        base_analysis = analysis_templates.get(classification, "Analysis completed.")
        
        # Add specific details based on content
        if "leak" in text.lower():
            base_analysis += " Leak detected - investigate source and implement containment measures."
        if "pressure" in text.lower():
            base_analysis += " Pressure-related issue identified - monitor system pressure closely."
        if "temperature" in text.lower():
            base_analysis += " Temperature anomaly detected - check cooling systems and ventilation."
            
        return base_analysis
    
    def _assess_risk(self, text: str, classification: ClassificationType, priority: PriorityLevel) -> str:
        """Assess risk level and potential impact"""
        risk_levels = {
            PriorityLevel.CRITICAL: "CRITICAL RISK: Immediate threat to vessel safety, operations, or environment.",
            PriorityLevel.HIGH: "HIGH RISK: Significant impact on operations or safety if not addressed promptly.",
            PriorityLevel.MEDIUM: "MEDIUM RISK: Moderate impact on operations or potential safety concern.",
            PriorityLevel.LOW: "LOW RISK: Minor operational impact, routine maintenance required."
        }
        
        base_risk = risk_levels.get(priority, "Risk assessment pending.")
        
        # Add specific risk factors
        risk_factors = []
        if "fire" in text.lower():
            risk_factors.append("Fire hazard present")
        if "structural" in text.lower():
            risk_factors.append("Structural integrity concern")
        if "pollution" in text.lower():
            risk_factors.append("Environmental contamination risk")
        if "navigation" in text.lower():
            risk_factors.append("Navigation safety impact")
            
        if risk_factors:
            base_risk += f" Additional factors: {', '.join(risk_factors)}."
            
        return base_risk
    
    def _generate_recommendations(self, classification: ClassificationType, priority: PriorityLevel, text: str) -> List[str]:
        """Generate specific recommendations based on classification and content"""
        recommendations = []
        
        # Base recommendations by classification
        classification_recs = {
            ClassificationType.CRITICAL_EQUIPMENT_FAILURE: [
                "Stop operations immediately if safe to do so",
                "Contact technical support team",
                "Initiate emergency response procedures",
                "Document all findings thoroughly"
            ],
            ClassificationType.NAVIGATIONAL_HAZARD: [
                "Alert bridge team immediately",
                "Update navigation charts and systems",
                "Implement additional lookout procedures",
                "Report to relevant maritime authorities"
            ],
            ClassificationType.ENVIRONMENTAL_COMPLIANCE: [
                "Stop any discharge operations",
                "Contact environmental compliance officer",
                "Prepare incident report for authorities",
                "Implement containment measures"
            ],
            ClassificationType.ROUTINE_MAINTENANCE: [
                "Schedule maintenance during next port call",
                "Order required spare parts",
                "Assign qualified personnel",
                "Update maintenance logs"
            ],
            ClassificationType.SAFETY_VIOLATION: [
                "Implement immediate safety measures",
                "Conduct safety briefing with crew",
                "Review safety procedures",
                "Report to safety officer"
            ]
        }
        
        recommendations = classification_recs.get(classification, ["Review and take appropriate action"])
        
        # Add priority-specific recommendations
        if priority == PriorityLevel.CRITICAL:
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED")
            recommendations.append("Consider emergency port call if necessary")
        
        # Add content-specific recommendations
        if "leak" in text.lower():
            recommendations.append("Investigate leak source and implement temporary repairs")
        if "alarm" in text.lower():
            recommendations.append("Test and verify alarm system functionality")
        if "pressure" in text.lower():
            recommendations.append("Monitor pressure levels continuously")
            
        return recommendations[:6]  # Limit to 6 recommendations