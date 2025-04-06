import os
import json
import logging
import re
import requests
import traceback
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфиг
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Берем ключ из переменных окружения
MODEL_NAME = "llama3-70b-8192"

# Инициализация Groq
groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client initialized")
    except ImportError:
        logger.error("Установи groq: pip install groq")
    except Exception as e:
        logger.error(f"Ошибка Groq: {str(e)}")
else:
    logger.warning("GROQ_API_KEY не задан!")

def analyze_resume(resume_text):
    """Анализ резюме через Groq"""
    if not groq_client:
        return {"error": "Groq client not initialized"}
    
    try:
        prompt = f"""
        Проанализируй это резюме для немецкого рынка труда. 
        Укажи конкретные ошибки и дай рекомендации по улучшению:
        
        {resume_text[:3000]}
        """
        
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Ошибка анализа: {str(e)}")
        return {"error": str(e)}

def generate_anschreiben(resume_text, job_description):
    """Генерация сопроводительного письма"""
    if not groq_client:
        return {"error": "Groq client not initialized"}
    
    try:
        prompt = f"""
        Напиши сопроводительное письмо (Anschreiben) на немецком на основе:
        
        Резюме:
        {resume_text[:2000]}
        
        Описание вакансии:
        {job_description[:2000]}
        """
        
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Ошибка генерации: {str(e)}")
        return {"error": str(e)}
