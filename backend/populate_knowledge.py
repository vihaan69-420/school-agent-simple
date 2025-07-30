#!/usr/bin/env python3
"""
Script to populate the knowledge base with Everest Academy data
"""

import logging
from database import DatabaseManager
from knowledge_service import KnowledgeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_everest_academy_data():
    """Return the Everest Academy knowledge base data"""
    
    knowledge_entries = [
        {
            "category": "School Overview",
            "title": "Homepage & Core Stats",
            "content": """Everest Academy Manila is the First International Catholic K‑12 School in the Philippines. 
            
Key Information:
- Tagline: Integral Formation® for Future Leaders
- Part of Regnum Christi network
- Uses Integral Formation® model for Catholic, academic, and leadership development
- 500+ students
- Class sizes: Kindergarten ~20/class, Grades 1–12 ~25/class
- 64% of faculty hold Master's or advanced degrees
- 4 AP courses offered
- Recognized under RA 11255 (March 29, 2019)
- 196 university acceptances (2018–2020)
- 9 varsity teams

Contact Information:
- Phone: +632 8882 5019 / +632 8882 4981
- Address: 3846 38th Drive North, BGC, Taguig 1634
- Email: admin@everestmanila.edu.ph""",
            "tags": ["overview", "stats", "contact", "basic_info"]
        },
        {
            "category": "About",
            "title": "Executive Director's Message",
            "content": """Rosa María López, Executive Director, welcomes families emphasizing:
- Integral Formation (intellectual, human, spiritual, apostolic)
- Core values: Excellence, Community, Charity, Integrity, Joy
- RC network connection
- Strong curriculum and AP program
- R-LIFE remote learning capabilities during pandemic

The school focuses on developing future leaders through comprehensive Catholic education.""",
            "tags": ["leadership", "values", "integral_formation", "director"]
        },
        {
            "category": "About",
            "title": "School FAQs",
            "content": """Key FAQ Information:

International Status:
- RC Education (Atlanta) curriculum
- AdvancED accreditation
- DepEd-recognized under RA 11255 (March 29, 2019)

Academic Programs:
- Not IB school; offers AP via College Board
- Blends progressive and traditional teaching methods
- RC Education curriculum + PH DepEd K-12 + Catholic Formation
- Languages, arts, PE, technology, and AP in high school

Student Demographics:
- ~70% Filipino, ~20% mixed heritage, ~10% foreign
- Accepts non-Catholics; Catholic Formation is mandatory

Special Features:
- Grades 4–8 are single-sex based on developmental research
- Co-ed for younger grades and mixed activities
- 10-11 R‑LIFE remote learning program
- Progressive bullying policy with Dean review

Faculty:
- All licensed teachers
- 64% hold Master's degrees
- Yearly in-service training
- Performance evaluation with tenure after 3 years""",
            "tags": ["faq", "international", "academic", "demographics", "faculty"]
        },
        {
            "category": "Academics",
            "title": "Academic Programs & Curriculum",
            "content": """Curriculum Structure:
- Follows RC Education common-core standards
- Integrated with Philippine K-12 requirements
- Subjects: English, Filipino, Math, History/Geography, Science, Catholic Formation, second language, fine arts, PE, technology

Teaching Methods:
- Inquiry-based learning
- Problem-solving approach
- Technology-enhanced instruction
- Structured with routine and assessments
- Character education integration

Grading System:
- Proficiency-based grading
- Student-teacher ratios: Kinder ~1:20, Grades 1–12 ~1:25

Special Programs:
- Career Planning & Guidance Office
- Academic Fairs (2021, 2022)
- Everest Altius program""",
            "tags": ["curriculum", "academics", "teaching", "programs"]
        },
        {
            "category": "Academics",
            "title": "Advanced Placement (AP) Program",
            "content": """AP Courses Offered:
- AP Biology
- AP Calculus AB
- AP English Language & Composition (Grades 10 & 12)
- AP World History
- AP English Literature
- AP Statistics

AP Performance Metrics (2017–2022):
- Exams taken: 44 to 110 (growth over years)
- Average scores: 3.63→3.70→3.56→3.37→2.88→2.90
- AP Scholar rate: ~20%
- AP Scholar with Honors: 4%
- AP Scholar with Distinction: 3%

Testing:
- College Board AP Testing Center
- Official AP exams administered on campus""",
            "tags": ["ap", "advanced_placement", "college_board", "testing"]
        },
        {
            "category": "Academics",
            "title": "Graduation Requirements & Awards",
            "content": """Diploma Requirements:
- 31-credit diploma required for graduation

Student Awards:
- Valedictorian
- Salutatorian
- Semper Altius Award
- Integer Award

Academic Recognition:
- No class rank due to small cohort sizes
- Focus on individual achievement and growth
- University acceptance tracking for graduates""",
            "tags": ["graduation", "diploma", "awards", "recognition"]
        },
        {
            "category": "Admissions",
            "title": "Admission Process",
            "content": """Application Steps:
1. Online inquiry form via E-SIMS portal
2. Interview process
3. Document upload
4. Application fee payment:
   - Kindergarten: ₱4,500
   - Grades 1–11: ₱7,000
5. Entrance examinations
6. Admission decision

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
- Contact: admissions@everestmanila.edu.ph for calendar mismatches""",
            "tags": ["admissions", "application", "requirements", "entrance_exam"]
        },
        {
            "category": "Admissions",
            "title": "Tuition & Fees",
            "content": """Tuition Fees (AY 2024-25 → 2025-26):
- Kindergarten: ₱306,000 → ₱320,000
- Grades 1–2: ₱413,500 → ₱433,000
- Grades 3–5: ₱441,000 → ₱462,000
- Grades 6–8: ₱469,000 → ₱491,000
- Grades 9–10: ₱497,000 → ₱520,000
- Grades 11–12: ₱525,000 → ₱550,000

Additional Fees:
- Capital Development Fee (one-time): ₱90,000 (Kinder) or ₱120,000 (Grades 1+)
- Miscellaneous Fee: ₱16,000 (books, supplies, services)
- Matriculation Fee (new students): ₱55,000

Sibling Discounts:
- 2 siblings: 10% discount
- 3 siblings: 15% discount
- 4 siblings: 20% discount
- 5+ siblings: 25% discount

Financial Aid:
- No scholarships available
- Financial aid inquiries can be made directly to the school""",
            "tags": ["tuition", "fees", "payment", "financial_aid", "sibling_discount"]
        },
        {
            "category": "Campus Life",
            "title": "Facilities & Campus",
            "content": """Campus Facilities:
- Multi-level libraries
- Computer & science laboratories
- Technology labs
- Conference hall
- Multi-purpose gymnasium
- Covered courts
- Indoor swimming pool

Learning Environment:
- Modern classrooms with technology integration
- Specialized spaces for different subjects
- Athletic facilities for sports programs
- Library resources for research and study""",
            "tags": ["facilities", "campus", "library", "labs", "sports"]
        },
        {
            "category": "Campus Life",
            "title": "Spiritual Formation",
            "content": """Catholic Formation:
- Daily Eucharist and Confession available
- Monthly First Friday Mass (broadcast via YouTube)
- Chaplaincy services by Legionaries of Christ/Regnum Christi
- Mandatory Catholic Formation for all students
- Annual retreats
- Feast day celebrations (e.g., Immaculate Conception)
- Baccalaureate Mass & Graduation ceremonies
- Ash Wednesday and Palm Sunday observances
- Holy Week activities

YouTube Channel:
- Mass broadcasts
- Event coverage
- Spiritual formation content""",
            "tags": ["spiritual", "catholic", "mass", "chaplaincy", "formation"]
        },
        {
            "category": "Campus Life",
            "title": "Athletics & Extracurricular",
            "content": """Varsity Sports (9 teams):
- Basketball
- Volleyball
- Badminton
- Futsal
- Taekwondo
- Jiu-jitsu
- Swimming
- Tennis
- Chess

Competition:
- MISAA (Metro Manila International Schools Athletic Association)
- ISSA (International School Sports Association)

Clubs & Activities:
- Speech & Debate
- Model United Nations
- Robotics
- Digital Gaming Development
- Choir
- Dance
- Theater
- Photography
- Film
- Everest Altius
- Business Council
- Sustainability Club
- Student Government

Service Requirements:
- 30-hour community service requirement
- Partnership with Mano Amiga
- Pineda community projects (water well & church construction)""",
            "tags": ["athletics", "sports", "clubs", "extracurricular", "service"]
        },
        {
            "category": "Campus Life",
            "title": "Academic Calendar & Events",
            "content": """Annual Events:
- New Parents Orientation
- Opening of Classes
- Clubs Start
- National celebrations
- First Friday Mass (YouTube broadcast)
- Teacher's Day
- Quarter ends
- Wellness Breaks
- Christmas Break
- Holy Week break
- Graduation & Baccalaureate Mass
- Moving‑Up Ceremonies
- Independence Day (June 12)
- Academic Fairs
- Madrigal Concert
- Annual Retreats

Regular Schedule:
- Monthly First Friday Mass
- Quarterly academic periods
- Seasonal breaks and holidays
- Health and wellness breaks""",
            "tags": ["calendar", "events", "schedule", "traditions"]
        },
        {
            "category": "Global Network",
            "title": "Regnum Christi Network",
            "content": """Global Presence:
- Part of Regnum Christi network
- 154 schools in 19 countries worldwide

Sister Schools:
- United States: Georgia, Michigan, California, Illinois
- Canada
- Ireland
- Switzerland
- Philippines: Laguna sister school

Educational Standards:
- RC Education curriculum (Atlanta-based)
- Global teacher training programs
- International educational standards
- Consistent Catholic formation across network

Accreditation:
- Cognia accreditation
- ICIF (International Catholic Identity Framework)
- CEAP (Catholic Educational Association of the Philippines)
- DepEd recognition under RA 11255""",
            "tags": ["global", "network", "regnum_christi", "international", "accreditation"]
        },
        {
            "category": "Administration",
            "title": "Leadership & Administration",
            "content": """Key Leadership:
- Executive Director: Rosa María López
- High School Head & AP Coordinator: Agenor Neil Luayon
- HS Counselor & SAT Coordinator: Liberty Valencerina

Administrative Offices:
- Admissions Manager
- Registrar
- Operations
- Information Technology
- Business Office
- Human Resources

Contact Information:
- General: admin@everestmanila.edu.ph
- Admissions: admissions@everestmanila.edu.ph
- Registrar: registrar@everestmanila.edu.ph
- Business Office: businessoff@everestmanila.edu.ph
- Recruitment: recruitment@everestmanila.edu.ph
- IT Support: it@everestmanila.edu.ph""",
            "tags": ["leadership", "administration", "staff", "contacts"]
        },
        {
            "category": "Technology",
            "title": "Digital Systems & Portal",
            "content": """ESSIMS/E-SIMS Portal:
- URL: https://myeverestacademy.everestmanila.com
- Secure login system
- Student grades access
- Class schedules
- School announcements
- Password reset functionality
- Inquiry forms
- Parent-student communication

R-LIFE Program:
- Remote learning platform
- Google Classroom integration
- G-Suite tools
- RC curriculum delivery
- Video/webinar capabilities
- Learning management system

Website Features:
- Domain: everestmanila.com
- Google Analytics integration
- Cookie policy compliance
- Privacy policy available
- Mobile-responsive design
- Social media integration (Facebook, TikTok, YouTube)""",
            "tags": ["technology", "portal", "digital", "r-life", "online"]
        },
        {
            "category": "University Preparation",
            "title": "College Guidance & Outcomes",
            "content": """University Acceptance Record (2018-2020):
- Total acceptances: 196
- International universities: 45% (abroad)
- Local universities: 55% (Philippines)

Notable International Acceptances:
- New York University (NYU)
- Johns Hopkins University
- University of Notre Dame
- Other prestigious institutions

Philippine Universities:
- Ateneo de Manila University
- University of the Philippines Diliman
- Other top local institutions

College Preparation:
- Career Planning & Guidance Office
- SAT preparation and coordination
- AP program for college credit
- University application support
- Counseling services
- School profile for college applications""",
            "tags": ["university", "college", "guidance", "outcomes", "preparation"]
        }
    ]
    
    return knowledge_entries

def main():
    """Main function to populate the knowledge base"""
    try:
        logger.info("Initializing database and services...")
        db_manager = DatabaseManager()
        knowledge_service = KnowledgeService(db_manager)
        
        logger.info("Getting Everest Academy data...")
        knowledge_entries = get_everest_academy_data()
        
        logger.info(f"Adding {len(knowledge_entries)} knowledge entries...")
        added_ids = knowledge_service.bulk_add_knowledge(knowledge_entries)
        
        logger.info(f"Successfully added {len(added_ids)} knowledge entries to the database!")
        
        # Verify the data was added
        logger.info("Verifying data...")
        categories = knowledge_service.get_all_categories()
        logger.info(f"Categories in knowledge base: {categories}")
        
        # Test search functionality
        test_search = knowledge_service.search_knowledge(query="tuition")
        logger.info(f"Test search for 'tuition' returned {len(test_search)} results")
        
        logger.info("Knowledge base population completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to populate knowledge base: {e}")
        raise

if __name__ == "__main__":
    main()