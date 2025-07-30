#!/usr/bin/env python3
"""
Script to update admission information with correct URLs
"""

import logging
from database import DatabaseManager
from knowledge_service import KnowledgeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_admission_knowledge():
    """Update admission entries with correct URLs"""
    
    # Updated admission entry with correct URL
    admission_entry = {
        "category": "Admissions",
        "title": "Admission Process (Updated with correct URL)",
        "content": """Application Steps:
1. Visit the application process page: https://everestmanila.com/admissions/application-process
2. Complete the online inquiry form via E-SIMS portal
3. Attend interview process
4. Upload required documents
5. Pay application fee:
   - Kindergarten: ₱4,500
   - Grades 1–11: ₱7,000
6. Take entrance examinations
7. Wait for admission decision

Required Documents:
- Guard's ID photo
- Birth certificate
- Baptismal/First Communion certificate (Catholics)
- Parents' marriage contract
- Family photo
- Report cards
- Course descriptions (Grades 9–11)
- Recommendation forms
- Guardianship/visa documents (if applicable)

Entrance Exams:
- Math and Language Arts (Grades 1–11)
- Kindergarten readiness test
- Interviews (Grade 4+)

Age Requirements:
- Kindergarten: 5 years old by August 31

Transfer Students:
- Accepted up to early in 2nd semester
- Contact: admissions@everestmanila.edu.ph for calendar mismatches

(Source: https://everestmanila.com/admissions/application-process)""",
        "tags": ["admissions", "application", "requirements", "entrance_exam", "process", "url_updated"]
    }
    
    # Also add specific page entries
    additional_entries = [
        {
            "category": "Admissions",
            "title": "Application Process Page",
            "content": """The official application process page for Everest Academy Manila can be found at:
https://everestmanila.com/admissions/application-process

This page contains:
- Step-by-step application guide
- Requirements checklist
- Important deadlines
- Contact information for admissions office
- Links to the E-SIMS portal for online applications

For direct questions, contact: admissions@everestmanila.edu.ph

(Source: https://everestmanila.com/admissions/application-process)""",
            "tags": ["admissions", "application_process", "official_page", "url"]
        },
        {
            "category": "Website Navigation",
            "title": "Important Everest Academy URLs",
            "content": """Official Everest Academy Manila Website Pages:

Homepage: https://everestmanila.com
About Us: https://everestmanila.com/about/welcome
Who We Are: https://everestmanila.com/who-we-are
Contact: https://everestmanila.com/about/contact

Admissions:
- Application Process: https://everestmanila.com/admissions/application-process
- E-SIMS Portal: https://myeverestacademy.everestmanila.com

Note: Always use these official URLs. The admissions section is found under the application-process subdirectory, not directly at /admissions.

(Source: https://everestmanila.com)""",
            "tags": ["navigation", "urls", "website", "official_links"]
        }
    ]
    
    try:
        logger.info("Initializing database and services...")
        db_manager = DatabaseManager()
        knowledge_service = KnowledgeService(db_manager)
        
        logger.info("Adding updated admission entries...")
        
        # Add the main admission entry
        knowledge_id = knowledge_service.add_knowledge_entry(
            admission_entry['category'],
            admission_entry['title'],
            admission_entry['content'],
            admission_entry['tags']
        )
        logger.info(f"Added main admission entry with ID: {knowledge_id}")
        
        # Add additional entries
        for entry in additional_entries:
            knowledge_id = knowledge_service.add_knowledge_entry(
                entry['category'],
                entry['title'],
                entry['content'],
                entry['tags']
            )
            logger.info(f"Added entry '{entry['title']}' with ID: {knowledge_id}")
        
        logger.info("Successfully updated admission information with correct URLs!")
        
        # Test search
        test_results = knowledge_service.search_knowledge(query="application process")
        logger.info(f"Test search for 'application process' returned {len(test_results)} results")
        
    except Exception as e:
        logger.error(f"Failed to update admission knowledge: {e}")
        raise

if __name__ == "__main__":
    update_admission_knowledge()