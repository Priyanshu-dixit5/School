import google.generativeai as genai
from flask import current_app

# Tested working models (gemini-2.5-flash recommended)
FALLBACK_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
]


def _normalize_model_name(name):
    if not name:
        return 'gemini-2.5-flash'
    name = name.strip()
    if name.startswith('models/'):
        return name[7:]
    return name


def _extract_text(response):
    try:
        if response.text:
            return response.text.strip()
    except (ValueError, AttributeError):
        pass
    if getattr(response, 'candidates', None):
        for candidate in response.candidates:
            content = getattr(candidate, 'content', None)
            if content and getattr(content, 'parts', None):
                text = ''.join(
                    p.text for p in content.parts if hasattr(p, 'text') and p.text
                )
                if text.strip():
                    return text.strip()
    return None


def _get_models_to_try():
    configured = _normalize_model_name(current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash'))
    models = [configured]
    for m in FALLBACK_MODELS:
        if m not in models:
            models.append(m)
    return models


def generate_text(prompt, system_context=''):
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return None, 'AI service is not configured. Please set GEMINI_API_KEY in your .env file.'

    genai.configure(api_key=api_key)
    full_prompt = f"{system_context}\n\n{prompt}" if system_context else prompt
    last_error = None

    for model_name in _get_models_to_try():
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            text = _extract_text(response)
            if text:
                return text, None
            last_error = f'Model {model_name} returned an empty response.'
        except Exception as e:
            last_error = str(e)
            current_app.logger.warning(f'Gemini model {model_name} failed: {e}')
            continue

    return None, f'AI service error: {last_error or "All models failed."}'


def _school_context():
    return f"""
You are an AI assistant for {current_app.config.get('SCHOOL_NAME', 'Blue Bells Public School')}, a CBSE school.
School Details:
- Name: {current_app.config.get('SCHOOL_NAME', 'Blue Bells Public School')}
- Tagline: {current_app.config.get('SCHOOL_TAGLINE', 'Love To Learn — Nurturing Minds, Building Futures')}
- Classes: Nursery to Class 12
- Board: CBSE
- Facilities: Smart Classrooms, Science Labs, Library, Sports Ground, Auditorium, Morning Assembly
- Timings: 8:00 AM - 2:30 PM (Mon-Fri)
- Admission Process: Online application, document verification, interaction, confirmation
- Contact: {current_app.config.get('SCHOOL_PHONE', '')}, {current_app.config.get('SCHOOL_EMAIL', '')}
- Address: {current_app.config.get('SCHOOL_ADDRESS', '')}

Answer questions about admissions, facilities, timings, scholarships, transport, and faculty professionally and concisely.
If you don't know specific details, provide general guidance and suggest contacting the school office.
"""


def chatbot_response(message, history=None):
    context = _school_context()
    if history:
        history_text = '\n'.join([f"{h['role']}: {h['content']}" for h in history[-10:]])
        context += f"\n\nConversation history:\n{history_text}"
    prompt = f"User question: {message}\n\nProvide a helpful, friendly response:"
    return generate_text(prompt, context)


def admission_assistant(age, class_applying, location):
    school_name = current_app.config.get('SCHOOL_NAME', 'Blue Bells Public School')
    prompt = f"""A parent wants to admit their child to {school_name}.
Student Age: {age}
Class Applying For: {class_applying}
Location: {location}

Provide a detailed response covering:
1. Eligibility criteria for the requested class
2. Required documents for admission
3. Step-by-step admission process
4. Any location-specific transport information if applicable
5. Important dates and tips

Format the response with clear headings and bullet points."""
    return generate_text(prompt, _school_context())


def career_guidance(stream):
    prompt = f"""Provide comprehensive career guidance for a student choosing the {stream.upper()} stream after Class 10.

Cover:
1. Overview of the {stream} stream
2. Subject combinations available
3. Top career paths and job roles
4. Required skills to develop
5. Higher education options
6. Future opportunities and emerging fields
7. Tips for success

Format with clear headings and be encouraging and informative."""
    return generate_text(prompt, _school_context())


def generate_faqs(school_info):
    prompt = f"""Based on the following school information, generate 10 frequently asked questions with detailed answers.

School Information:
{school_info}

Format each FAQ as:
Q: [Question]
A: [Answer]

Cover topics like admissions, fees, facilities, academics, transport, and general inquiries."""
    return generate_text(prompt, _school_context())


def summarize_notice(notice):
    prompt = f"""Summarize the following school notice into a concise, parent-friendly summary (2-3 sentences max).
Also provide 3 key bullet points.

Notice:
{notice}

Format:
Summary: [brief summary]
Key Points:
- [point 1]
- [point 2]
- [point 3]"""
    return generate_text(prompt, _school_context())
