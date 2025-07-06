import json
from models import AssessmentQuestion, Assessment, Country
from app import db

class AssessmentEngine:
    """Privacy posture assessment engine"""
    
    @staticmethod
    def get_questions():
        """Get all active assessment questions organized by category"""
        questions = AssessmentQuestion.query.filter_by(is_active=True).order_by(
            AssessmentQuestion.category, AssessmentQuestion.order
        ).all()
        
        # If no questions exist, create default ones
        if not questions:
            AssessmentEngine.create_default_questions()
            questions = AssessmentQuestion.query.filter_by(is_active=True).order_by(
                AssessmentQuestion.category, AssessmentQuestion.order
            ).all()
        
        # Group by category
        categorized_questions = {}
        for question in questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return categorized_questions
    
    @staticmethod
    def create_default_questions():
        """Create default assessment questions"""
        questions_data = [
            {
                'category': 'Data Collection',
                'questions': [
                    {
                        'text': 'Does your organization collect personal data from customers or employees?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 3,
                        'order': 1
                    },
                    {
                        'text': 'Do you have a clear privacy policy that explains what data you collect?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 2,
                        'order': 2
                    },
                    {
                        'text': 'How do you obtain consent for data collection?',
                        'type': 'multiple_choice',
                        'options': json.dumps([
                            'Written consent forms',
                            'Digital consent (checkboxes, buttons)',
                            'Verbal consent only',
                            'No formal consent process',
                            'Not applicable'
                        ]),
                        'weight': 3,
                        'order': 3
                    }
                ]
            },
            {
                'category': 'Data Security',
                'questions': [
                    {
                        'text': 'How do you protect personal data in your systems?',
                        'type': 'multiple_choice',
                        'options': json.dumps([
                            'Encryption and access controls',
                            'Basic password protection',
                            'Physical security only',
                            'No specific security measures',
                            'Not sure'
                        ]),
                        'weight': 4,
                        'order': 1
                    },
                    {
                        'text': 'Do you have a data breach response plan?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 3,
                        'order': 2
                    },
                    {
                        'text': 'How often do you backup personal data?',
                        'type': 'multiple_choice',
                        'options': json.dumps([
                            'Daily automated backups',
                            'Weekly backups',
                            'Monthly backups',
                            'Rarely or never',
                            'Not applicable'
                        ]),
                        'weight': 2,
                        'order': 3
                    }
                ]
            },
            {
                'category': 'Data Rights',
                'questions': [
                    {
                        'text': 'Can individuals request to see what personal data you hold about them?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 3,
                        'order': 1
                    },
                    {
                        'text': 'Can individuals request deletion of their personal data?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 3,
                        'order': 2
                    },
                    {
                        'text': 'How do you handle data subject requests?',
                        'type': 'multiple_choice',
                        'options': json.dumps([
                            'Formal process with timelines',
                            'Ad-hoc basis',
                            'No formal process',
                            'Not applicable'
                        ]),
                        'weight': 2,
                        'order': 3
                    }
                ]
            },
            {
                'category': 'Compliance & Training',
                'questions': [
                    {
                        'text': 'Do you provide privacy training to your staff?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 2,
                        'order': 1
                    },
                    {
                        'text': 'Do you have a designated Data Protection Officer (DPO)?',
                        'type': 'yes_no',
                        'options': json.dumps(['Yes', 'No']),
                        'weight': 2,
                        'order': 2
                    },
                    {
                        'text': 'How familiar are you with privacy laws in your country?',
                        'type': 'multiple_choice',
                        'options': json.dumps([
                            'Very familiar',
                            'Somewhat familiar',
                            'Limited knowledge',
                            'Not familiar at all'
                        ]),
                        'weight': 3,
                        'order': 3
                    }
                ]
            }
        ]
        
        for category_data in questions_data:
            category = category_data['category']
            for q_data in category_data['questions']:
                question = AssessmentQuestion(
                    category=category,
                    question_text=q_data['text'],
                    question_type=q_data['type'],
                    options=q_data['options'],
                    weight=q_data['weight'],
                    order=q_data['order']
                )
                db.session.add(question)
        
        db.session.commit()
    
    @staticmethod
    def calculate_score(responses, user_country=None):
        """Calculate privacy posture score based on responses"""
        total_score = 0
        max_possible_score = 0
        
        questions = AssessmentQuestion.query.filter_by(is_active=True).all()
        
        for question in questions:
            max_possible_score += question.weight * 100
            
            if str(question.id) in responses:
                response = responses[str(question.id)]
                question_score = AssessmentEngine._score_response(question, response)
                total_score += question_score * question.weight
        
        if max_possible_score == 0:
            return 0, 'Unknown'
        
        # Calculate percentage score
        percentage_score = int((total_score / max_possible_score) * 100)
        
        # Determine risk level
        if percentage_score >= 80:
            risk_level = 'Low'
        elif percentage_score >= 60:
            risk_level = 'Medium'
        elif percentage_score >= 40:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
        
        return percentage_score, risk_level
    
    @staticmethod
    def _score_response(question, response):
        """Score individual question response"""
        if question.question_type == 'yes_no':
            # For yes/no questions, "Yes" is typically better
            if response.lower() == 'yes':
                return 100
            else:
                return 0
        
        elif question.question_type == 'multiple_choice':
            options = json.loads(question.options)
            # Score based on position in options (first option = highest score)
            try:
                option_index = options.index(response)
                # Reverse scoring: first option gets highest score
                score = 100 - (option_index * (100 / len(options)))
                return max(0, score)
            except ValueError:
                return 0
        
        return 0
    
    @staticmethod
    def generate_recommendations(score, risk_level, user_country=None):
        """Generate personalized recommendations based on score and country"""
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level == 'Critical':
            recommendations.extend([
                "Immediate action required: Develop a comprehensive data protection policy",
                "Implement basic security measures to protect personal data",
                "Establish formal consent processes for data collection",
                "Consider hiring a Data Protection Officer or consultant"
            ])
        elif risk_level == 'High':
            recommendations.extend([
                "Strengthen your current data protection measures",
                "Implement a data breach response plan",
                "Review and update your privacy policy",
                "Provide staff training on data protection"
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                "Good foundation - focus on improving data subject rights processes",
                "Regular security audits and updates",
                "Enhanced staff training programs",
                "Consider advanced security measures"
            ])
        else:  # Low risk
            recommendations.extend([
                "Excellent privacy posture - maintain current standards",
                "Regular compliance reviews and updates",
                "Stay informed about evolving privacy regulations",
                "Consider becoming a privacy champion in your industry"
            ])
        
        # Country-specific recommendations
        country_recommendations = AssessmentEngine.get_country_recommendations(user_country)
        if country_recommendations:
            recommendations.extend(country_recommendations)
        
        return recommendations
    
    @staticmethod
    def get_country_recommendations(country_code):
        """Get country-specific privacy recommendations"""
        country_advice = {
            'NG': [
                "Ensure compliance with Nigeria Data Protection Act (NDPA)",
                "Register with the Nigeria Data Protection Commission (NDPC)",
                "Implement local data residency requirements where applicable"
            ],
            'KE': [
                "Comply with Kenya's Data Protection Act 2019",
                "Register with the Data Protection Commissioner",
                "Ensure proper cross-border data transfer agreements"
            ],
            'GH': [
                "Adhere to Ghana's Data Protection Act 2012",
                "Register with the Data Protection Commission",
                "Implement adequate data security measures as required"
            ],
            'ZA': [
                "Ensure compliance with Protection of Personal Information Act (POPIA)",
                "Register with the Information Regulator if required",
                "Implement appropriate security measures"
            ],
            'ZW': [
                "Follow Zimbabwe's Cyber and Data Protection Act (CDPA) provisions",
                "Ensure proper consent mechanisms are in place",
                "Consider regional data protection requirements"
            ],
            'ZM': [
                "Prepare for upcoming data protection legislation",
                "Implement international best practices",
                "Consider regional compliance requirements"
            ],
            'BW': [
                "Follow emerging data protection guidelines",
                "Implement international best practices",
                "Prepare for potential future legislation"
            ]
        }
        
        return country_advice.get(country_code, [])
    
    @staticmethod
    def create_assessment_record(user_id, responses, score, risk_level, recommendations):
        """Create assessment record in database"""
        assessment = Assessment(
            user_id=user_id,
            score=score,
            risk_level=risk_level,
            responses=json.dumps(responses),
            recommendations=json.dumps(recommendations)
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return assessment
