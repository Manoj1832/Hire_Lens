"""
MCQ Generator Module
Generates multiple choice questions based on extracted skills
"""
import random
import json
import os

# Knowledge base for common technical skills
SKILL_QUESTIONS = {
    "python": [
        {
            "question": "What is the output of: print(2 ** 3)?",
            "options": ["6", "8", "9", "5"],
            "correct": 1
        },
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["func", "def", "function", "define"],
            "correct": 1
        },
        {
            "question": "What does 'len()' function do in Python?",
            "options": ["Returns the length of a string/list", "Converts to lowercase", "Splits a string", "Joins strings"],
            "correct": 0
        }
    ],
    "java": [
        {
            "question": "What is the default value of a boolean variable in Java?",
            "options": ["true", "false", "null", "0"],
            "correct": 1
        },
        {
            "question": "Which method is used to start a thread in Java?",
            "options": ["run()", "start()", "execute()", "begin()"],
            "correct": 1
        }
    ],
    "javascript": [
        {
            "question": "What is the result of: typeof null?",
            "options": ["null", "undefined", "object", "string"],
            "correct": 2
        },
        {
            "question": "Which method adds an element to the end of an array?",
            "options": ["push()", "pop()", "shift()", "unshift()"],
            "correct": 0
        }
    ],
    "sql": [
        {
            "question": "Which SQL clause is used to filter records?",
            "options": ["SELECT", "WHERE", "FROM", "ORDER BY"],
            "correct": 1
        },
        {
            "question": "What does JOIN do in SQL?",
            "options": ["Combines rows from multiple tables", "Deletes records", "Updates values", "Creates indexes"],
            "correct": 0
        }
    ],
    "html": [
        {
            "question": "Which tag is used to create a hyperlink?",
            "options": ["<link>", "<a>", "<href>", "<url>"],
            "correct": 1
        }
    ],
    "css": [
        {
            "question": "Which property is used to change text color?",
            "options": ["text-color", "color", "font-color", "text-style"],
            "correct": 1
        }
    ],
    "django": [
        {
            "question": "What is Django's ORM used for?",
            "options": ["Template rendering", "Database operations", "URL routing", "Authentication"],
            "correct": 1
        }
    ],
    "react": [
        {
            "question": "What is a React component?",
            "options": ["A JavaScript function", "A reusable UI element", "A database table", "A CSS class"],
            "correct": 1
        }
    ],
    "machine learning": [
        {
            "question": "What is overfitting in machine learning?",
            "options": ["Model performs well on training but poorly on test data", "Model is too simple", "Model has too few features", "Model trains too slowly"],
            "correct": 0
        }
    ],
    "data analysis": [
        {
            "question": "What is the purpose of data normalization?",
            "options": ["To scale data to a common range", "To delete outliers", "To add missing values", "To sort data"],
            "correct": 0
        }
    ]
}

# Generic questions for skills not in the knowledge base
GENERIC_QUESTIONS = [
    {
        "question": "Which of the following is a best practice in software development?",
        "options": ["Writing code without comments", "Regular code reviews", "Ignoring error handling", "Hardcoding values"],
        "correct": 1
    },
    {
        "question": "What is version control used for?",
        "options": ["Compiling code", "Tracking changes in code", "Running tests", "Deploying applications"],
        "correct": 1
    },
    {
        "question": "What is the purpose of unit testing?",
        "options": ["To test the entire system", "To test individual components", "To deploy code", "To write documentation"],
        "correct": 1
    },
    {
        "question": "Which is an important aspect of code quality?",
        "options": ["Code complexity", "Readability and maintainability", "Long variable names", "No documentation"],
        "correct": 1
    },
    {
        "question": "What does API stand for?",
        "options": ["Application Programming Interface", "Automated Program Integration", "Advanced Programming Interface", "Application Process Integration"],
        "correct": 0
    }
]


def normalize_skill(skill):
    """Normalize skill name for matching"""
    return skill.lower().strip()


def generate_mcq_from_skills(skills, num_questions=10):
    """
    Generate MCQ questions based on extracted skills
    
    Args:
        skills: List of skill strings
        num_questions: Number of questions to generate (default 10)
    
    Returns:
        List of question dictionaries
    """
    questions = []
    normalized_skills = [normalize_skill(skill) for skill in skills]
    
    # Collect questions from skill-specific knowledge base
    skill_questions = []
    for skill in normalized_skills:
        # Check for exact match
        if skill in SKILL_QUESTIONS:
            skill_questions.extend(SKILL_QUESTIONS[skill])
        else:
            # Check for partial match
            for key, qs in SKILL_QUESTIONS.items():
                if key in skill or skill in key:
                    skill_questions.extend(qs)
                    break
    
    # If we have enough skill-specific questions, use them
    if len(skill_questions) >= num_questions:
        selected = random.sample(skill_questions, num_questions)
    else:
        # Mix skill-specific and generic questions
        selected = skill_questions.copy()
        remaining = num_questions - len(selected)
        generic = random.sample(GENERIC_QUESTIONS, min(remaining, len(GENERIC_QUESTIONS)))
        selected.extend(generic)
        
        # If still not enough, duplicate and shuffle
        while len(selected) < num_questions:
            selected.extend(random.sample(GENERIC_QUESTIONS, min(num_questions - len(selected), len(GENERIC_QUESTIONS))))
    
    # Shuffle and limit to num_questions
    random.shuffle(selected)
    questions = selected[:num_questions]
    
    # Shuffle options for each question
    for q in questions:
        correct_answer = q['options'][q['correct']]
        options = q['options'].copy()
        random.shuffle(options)
        q['correct'] = options.index(correct_answer)
        q['options'] = options
    
    return questions


def save_questions(questions, filepath="test_questions.json"):
    """Save questions to a JSON file"""
    with open(filepath, 'w') as f:
        json.dump(questions, f, indent=2)


def load_questions(filepath="test_questions.json"):
    """Load questions from a JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


if __name__ == "__main__":
    # Test the generator
    test_skills = ["Python", "JavaScript", "SQL", "Django"]
    questions = generate_mcq_from_skills(test_skills, 10)
    print(f"Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        for j, opt in enumerate(q['options']):
            marker = "✓" if j == q['correct'] else " "
            print(f"   {marker} {chr(65+j)}. {opt}")

