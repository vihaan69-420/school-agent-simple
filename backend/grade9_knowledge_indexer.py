#!/usr/bin/env python3
"""
Grade 9 Knowledge Indexer for Everest Academy
Indexes and manages Grade 9 study resources
"""

import os
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class Grade9KnowledgeIndexer:
    """Indexes and provides access to Grade 9 study materials"""
    
    def __init__(self, resources_path: str = "/home/vihaan/Grade 9 info"):
        self.resources_path = resources_path
        self.subjects = {
            "science": {
                "keywords": ["atmosphere", "weather", "solar", "cosmic", "stellar", "earthquake", "radiation"],
                "topics": []
            },
            "mathematics": {
                "keywords": ["angle", "triangle", "chord", "secant", "tangent", "slope", "equation", "parallel", "perpendicular"],
                "topics": []
            },
            "general": {
                "keywords": ["school", "details", "review"],
                "topics": []
            }
        }
        self.indexed_content = {}
        self._index_resources()
    
    def _index_resources(self):
        """Index all PDF resources in the Grade 9 directory"""
        try:
            pdf_files = [f for f in os.listdir(self.resources_path) if f.endswith('.pdf')]
            
            for pdf_file in pdf_files:
                if pdf_file.endswith('.pdf:Zone.Identifier'):
                    continue  # Skip zone identifier files
                
                file_path = os.path.join(self.resources_path, pdf_file)
                self._index_pdf(file_path, pdf_file)
                
            logger.info(f"Indexed {len(self.indexed_content)} Grade 9 resources")
            
        except Exception as e:
            logger.error(f"Error indexing Grade 9 resources: {e}")
    
    def _index_pdf(self, file_path: str, filename: str):
        """Index a single PDF file"""
        try:
            # Categorize by subject
            subject = self._categorize_by_filename(filename)
            
            # Store metadata
            self.indexed_content[filename] = {
                "path": file_path,
                "subject": subject,
                "title": self._extract_title(filename),
                "topics": self._extract_topics(filename)
            }
            
            # Add to subject topics
            if subject in self.subjects:
                self.subjects[subject]["topics"].append({
                    "file": filename,
                    "title": self.indexed_content[filename]["title"],
                    "topics": self.indexed_content[filename]["topics"]
                })
                
        except Exception as e:
            logger.error(f"Error indexing {filename}: {e}")
    
    def _categorize_by_filename(self, filename: str) -> str:
        """Categorize file by subject based on filename"""
        filename_lower = filename.lower()
        
        for subject, info in self.subjects.items():
            for keyword in info["keywords"]:
                if keyword in filename_lower:
                    return subject
        
        return "general"
    
    def _extract_title(self, filename: str) -> str:
        """Extract clean title from filename"""
        # Remove file extension and clean up
        title = filename.replace('.pdf', '')
        title = title.replace('_', ' ')
        title = re.sub(r'Lesson \d+[_:]?\s*', '', title)
        title = re.sub(r'Q\d+\s*Unit\s*\d+\s*PPT\s*\d*\s*', '', title)
        return title.strip()
    
    def _extract_topics(self, filename: str) -> List[str]:
        """Extract topics from filename"""
        topics = []
        
        # Extract lesson numbers
        lesson_match = re.search(r'Lesson (\d+)', filename)
        if lesson_match:
            topics.append(f"Lesson {lesson_match.group(1)}")
        
        # Extract quarter/unit info
        quarter_match = re.search(r'Q(\d+)', filename)
        if quarter_match:
            topics.append(f"Quarter {quarter_match.group(1)}")
        
        unit_match = re.search(r'Unit (\d+)', filename)
        if unit_match:
            topics.append(f"Unit {unit_match.group(1)}")
        
        return topics
    
    def search_resources(self, query: str, subject: Optional[str] = None) -> List[Dict]:
        """Search for resources based on query"""
        query_lower = query.lower()
        results = []
        
        for filename, info in self.indexed_content.items():
            # Skip if subject filter doesn't match
            if subject and info["subject"] != subject:
                continue
            
            # Check if query matches title or topics
            if (query_lower in info["title"].lower() or
                any(query_lower in topic.lower() for topic in info["topics"]) or
                any(keyword in query_lower for keyword in self.subjects[info["subject"]]["keywords"])):
                
                results.append({
                    "filename": filename,
                    "title": info["title"],
                    "subject": info["subject"],
                    "topics": info["topics"],
                    "path": info["path"]
                })
        
        return results
    
    def get_subject_overview(self, subject: str) -> Dict:
        """Get overview of resources for a specific subject"""
        if subject not in self.subjects:
            return {"error": "Subject not found"}
        
        subject_info = self.subjects[subject]
        resources = [info for info in self.indexed_content.values() if info["subject"] == subject]
        
        return {
            "subject": subject,
            "total_resources": len(resources),
            "topics": subject_info["topics"],
            "resource_list": [
                {
                    "title": res["title"],
                    "topics": res["topics"]
                }
                for res in resources
            ]
        }
    
    def get_all_subjects(self) -> List[str]:
        """Get list of all available subjects"""
        subjects_with_resources = []
        
        for subject in self.subjects.keys():
            if any(info["subject"] == subject for info in self.indexed_content.values()):
                subjects_with_resources.append(subject)
        
        return subjects_with_resources
    
    def format_for_context(self, resources: List[Dict]) -> str:
        """Format resources for LLM context"""
        if not resources:
            return "No Grade 9 resources found for this query."
        
        context_parts = ["=== GRADE 9 STUDY RESOURCES ===\n"]
        
        # Group by subject
        by_subject = {}
        for res in resources:
            subject = res["subject"]
            if subject not in by_subject:
                by_subject[subject] = []
            by_subject[subject].append(res)
        
        for subject, subject_resources in by_subject.items():
            context_parts.append(f"\n**{subject.title()} Resources:**")
            
            for res in subject_resources:
                context_parts.append(f"\n- {res['title']}")
                if res['topics']:
                    context_parts.append(f"  Topics: {', '.join(res['topics'])}")
                context_parts.append(f"  File: {res['filename']}")
        
        context_parts.append("\n\nNote: These are official Grade 9 study materials from Everest Academy. Students can request specific topics or lessons.")
        
        return "\n".join(context_parts)

# Global instance
grade9_indexer = Grade9KnowledgeIndexer()

if __name__ == "__main__":
    # Test the indexer
    logging.basicConfig(level=logging.INFO)
    
    print("Grade 9 Resources Index:")
    print("-" * 50)
    
    # Show all subjects
    subjects = grade9_indexer.get_all_subjects()
    print(f"Available subjects: {', '.join(subjects)}")
    
    # Show science resources
    science_overview = grade9_indexer.get_subject_overview("science")
    print(f"\nScience resources: {science_overview['total_resources']}")
    
    # Test search
    results = grade9_indexer.search_resources("atmosphere")
    print(f"\nSearch results for 'atmosphere': {len(results)} found")
    
    # Format for context
    context = grade9_indexer.format_for_context(results)
    print(f"\nFormatted context:\n{context}")