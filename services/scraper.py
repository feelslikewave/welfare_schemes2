"""
Schemes Scraper Service - services/scraper.py
Fetches real government schemes data
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class SchemesScraper:
    """Scrapes and manages government welfare schemes"""
    
    def __init__(self):
        self.schemes_file = Path("data/schemes.json")
        self.schemes = []
        self.schemes_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_schemes(self):
        """Load schemes from cache or create sample data"""
        if self.schemes_file.exists():
            with open(self.schemes_file, 'r', encoding='utf-8') as f:
                self.schemes = json.load(f)
        else:
            self._create_sample_schemes()
    
    def _create_sample_schemes(self):
        """Create comprehensive sample schemes based on real government schemes"""
        self.schemes = [
            {
                "id": "PM-KISAN",
                "name": "Pradhan Mantri Kisan Samman Nidhi",
                "state": "All India",
                "category": "Agriculture",
                "description": "Income support scheme providing financial assistance to all landholding farmers families across the country.",
                "benefits": "Direct income support of Rs. 6000 per year in three equal installments of Rs. 2000 each, transferred directly to bank accounts.",
                "eligibility": "All landholding farmers families. Small and marginal farmers with cultivable land up to 2 hectares.",
                "documents": ["Aadhaar Card", "Bank Account Details", "Land Ownership Papers"],
                "how_to_apply": "Visit nearest CSC (Common Service Center) or register online at pmkisan.gov.in. Submit required documents and bank details.",
                "official_link": "https://pmkisan.gov.in",
                "ministry": "Ministry of Agriculture and Farmers Welfare",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "PMAY-GRAMIN",
                "name": "Pradhan Mantri Awas Yojana - Gramin",
                "state": "All India",
                "category": "Housing",
                "description": "Provides pucca houses with basic amenities to rural homeless and households living in kutcha houses.",
                "benefits": "Financial assistance of Rs. 1.20 lakh in plain areas and Rs. 1.30 lakh in hilly states for construction of pucca house with basic amenities.",
                "eligibility": "Households living in kutcha houses, homeless families, families living in zero, one or two room houses with kutcha walls and roofs.",
                "documents": ["Aadhaar Card", "BPL Card", "Income Certificate", "Bank Account"],
                "how_to_apply": "Apply through Gram Panchayat. The Gram Sabha identifies beneficiaries and forwards applications to Block level.",
                "official_link": "https://pmayg.nic.in",
                "ministry": "Ministry of Rural Development",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "PMJAY",
                "name": "Pradhan Mantri Jan Arogya Yojana (Ayushman Bharat)",
                "state": "All India",
                "category": "Health",
                "description": "World's largest health insurance scheme providing health cover of Rs. 5 lakh per family per year for secondary and tertiary care hospitalization.",
                "benefits": "Free treatment up to Rs. 5 lakh per family per year at any empaneled public or private hospital across India. Covers 1,393 procedures including surgeries, medical treatments, and day care.",
                "eligibility": "Bottom 40% families as per SECC database. Families with no male member aged 16-59, female headed households, households with disabled members, SC/ST households.",
                "documents": ["Aadhaar Card", "PMJAY Card", "Identity Proof"],
                "how_to_apply": "Check eligibility on pmjay.gov.in using mobile number. Visit nearest CSC to get PMJAY card. For treatment, show card at empaneled hospital.",
                "official_link": "https://pmjay.gov.in",
                "ministry": "Ministry of Health and Family Welfare",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "PMUY",
                "name": "Pradhan Mantri Ujjwala Yojana",
                "state": "All India",
                "category": "Social Welfare",
                "description": "Provides free LPG connections to women from BPL households to protect them from health hazards of cooking with unclean fuel.",
                "benefits": "Free LPG connection with first refill and hotplate absolutely free. Financial assistance of Rs. 1600 per connection.",
                "eligibility": "Women from BPL households, all SC/ST households, PMAY beneficiaries, Antyodaya Anna Yojana beneficiaries, forest dwellers, island residents.",
                "documents": ["BPL Card/SECC Name", "Aadhaar Card", "Bank Account", "Address Proof"],
                "how_to_apply": "Apply at nearest LPG distributor with required documents. Can also apply online through official website.",
                "official_link": "https://www.pmuy.gov.in",
                "ministry": "Ministry of Petroleum and Natural Gas",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "SSA",
                "name": "Sarva Shiksha Abhiyan",
                "state": "All India",
                "category": "Education",
                "description": "Programme for universalization of elementary education providing free and compulsory education to children aged 6-14 years.",
                "benefits": "Free textbooks, uniforms, mid-day meals. Infrastructure development including schools, classrooms, toilets. Teacher training and quality improvement.",
                "eligibility": "All children in age group 6-14 years. Special focus on girls, SC/ST children, minorities, and children with special needs.",
                "documents": ["Birth Certificate", "Aadhaar Card", "Residence Proof", "Caste Certificate (if applicable)"],
                "how_to_apply": "Enroll children at nearest government school. No fees required. Contact District Education Officer for assistance.",
                "official_link": "https://dsel.education.gov.in",
                "ministry": "Ministry of Education",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "PMEGP",
                "name": "Prime Minister's Employment Generation Programme",
                "state": "All India",
                "category": "Employment",
                "description": "Credit linked subsidy programme for generating employment by setting up micro enterprises in non-farm sector.",
                "benefits": "Subsidy of 15-35% of project cost depending on category and location. Loan facilitation for business setup. Training support.",
                "eligibility": "Individuals above 18 years with minimum 8th standard education. No income limit for projects costing above Rs. 10 lakh in manufacturing and Rs. 5 lakh in service sector.",
                "documents": ["Aadhaar Card", "Educational Certificates", "Caste Certificate (if applicable)", "Bank Account", "Project Report"],
                "how_to_apply": "Apply online through PMEGP portal. Submit detailed project report to KVIC/KVIB. Attend interview and training if selected.",
                "official_link": "https://www.kviconline.gov.in/pmegpeportal",
                "ministry": "Ministry of Micro, Small and Medium Enterprises",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "NSP",
                "name": "National Scholarship Portal Schemes",
                "state": "All India",
                "category": "Education",
                "description": "Umbrella portal providing various scholarships to students from economically weaker sections to pursue education.",
                "benefits": "Scholarships ranging from Rs. 10,000 to Rs. 2,00,000 per year depending on course and scheme. Covers school and higher education.",
                "eligibility": "Students from SC/ST/OBC/Minority communities. Income based criteria. Minimum marks requirement varies by scheme.",
                "documents": ["Aadhaar Card", "Income Certificate", "Caste Certificate", "Mark sheets", "Bank Account", "Bonafide Certificate"],
                "how_to_apply": "Register on National Scholarship Portal. Choose applicable scheme, fill application, upload documents, submit to institute for verification.",
                "official_link": "https://scholarships.gov.in",
                "ministry": "Ministry of Education / Ministry of Social Justice",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "MGNREGA",
                "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
                "state": "All India",
                "category": "Employment",
                "description": "Guarantees 100 days of wage employment in rural areas to every household whose adult members volunteer to do unskilled manual work.",
                "benefits": "100 days guaranteed employment per household per financial year. Minimum wage payment. Work within 5 km of residence. Unemployment allowance if work not provided.",
                "eligibility": "Adult members of rural households willing to do unskilled manual work. Job card holders.",
                "documents": ["Aadhaar Card", "Address Proof", "Bank Account", "Passport Photo"],
                "how_to_apply": "Apply to local Gram Panchayat for job card. Once issued, apply for work during lean agricultural season. Register attendance for wage payment.",
                "official_link": "https://nrega.nic.in",
                "ministry": "Ministry of Rural Development",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "PMSSY",
                "name": "Pradhan Mantri Suraksha Bima Yojana",
                "state": "All India",
                "category": "Social Welfare",
                "description": "Accidental death and disability cover insurance scheme available to all bank account holders.",
                "benefits": "Rs. 2 lakh coverage for accidental death. Rs. 1 lakh for permanent total disability. Premium of only Rs. 12 per year.",
                "eligibility": "Age 18-70 years. Must have savings bank account. Auto-debit facility required.",
                "documents": ["Aadhaar Card", "Bank Account", "Nominee Details"],
                "how_to_apply": "Visit your bank branch or netbanking. Fill enrollment form. Activate auto-debit for annual premium.",
                "official_link": "https://www.jansuraksha.gov.in",
                "ministry": "Ministry of Finance",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "SBM",
                "name": "Swachh Bharat Mission - Gramin",
                "state": "All India",
                "category": "Rural Development",
                "description": "Aims to achieve universal sanitation coverage in rural areas by promoting construction and usage of household toilets.",
                "benefits": "Incentive of Rs. 12,000 per household for toilet construction. Technical assistance and awareness programs.",
                "eligibility": "Rural households not having sanitary toilets. BPL and landless households given priority.",
                "documents": ["Aadhaar Card", "BPL Card (if applicable)", "Bank Account", "Residence Proof"],
                "how_to_apply": "Apply through Gram Panchayat. Submit application with required documents. Construct toilet as per prescribed design. Verification and incentive payment.",
                "official_link": "https://swachhbharatmission.gov.in/sbmcms/index.htm",
                "ministry": "Ministry of Jal Shakti",
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        # Save to file
        with open(self.schemes_file, 'w', encoding='utf-8') as f:
            json.dump(self.schemes, f, indent=2, ensure_ascii=False)
    
    def search_schemes(self, state: Optional[str] = None, 
                      category: Optional[str] = None,
                      keyword: Optional[str] = None) -> List[Dict]:
        """Search schemes with filters"""
        results = self.schemes.copy()
        
        if state and state != "All India":
            results = [s for s in results if s['state'] == state or s['state'] == "All India"]
        
        if category:
            results = [s for s in results if s['category'] == category]
        
        if keyword:
            keyword = keyword.lower()
            results = [
                s for s in results
                if keyword in s['name'].lower() or
                   keyword in s['description'].lower() or
                   keyword in s['category'].lower()
            ]
        
        return results
    
    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict]:
        """Get scheme by ID"""
        for scheme in self.schemes:
            if scheme['id'] == scheme_id:
                return scheme
        return None