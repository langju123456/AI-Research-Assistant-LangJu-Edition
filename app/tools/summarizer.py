"""
Document summarizer tool.
"""
from typing import Optional
from app.tools.base import BaseTool
from app.utils import logger


class SummarizerTool(BaseTool):
    """Tool for summarizing text documents."""
    
    name = "summarizer"
    description = "Summarizes long text documents into concise summaries. Input should be the text to summarize."
    
    def __init__(self, model=None):
        """
        Initialize summarizer tool.
        
        Args:
            model: Language model instance for summarization
        """
        self.model = model
    
    def run(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
        
        Returns:
            Summary of the text
        """
        try:
            if not text or not text.strip():
                return "Error: No text provided to summarize."
            
            # Simple extractive summarization if no model provided
            if self.model is None:
                return self._simple_summarize(text, max_length)
            
            # Use model for abstractive summarization
            prompt = f"""Summarize the following text concisely in about {max_length} words:

{text}

Summary:"""
            
            summary = self.model.generate(prompt, max_tokens=max_length * 2)
            logger.info(f"Generated summary of {len(text)} chars -> {len(summary)} chars")
            return summary.strip()
        
        except Exception as e:
            error_msg = f"Error summarizing text: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _simple_summarize(self, text: str, max_words: int) -> str:
        """
        Simple extractive summarization.
        
        Args:
            text: Text to summarize
            max_words: Maximum words in summary
        
        Returns:
            Summary
        """
        # Split into sentences
        sentences = text.replace('\n', ' ').split('. ')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        if not sentences:
            return "Error: Could not extract sentences from text."
        
        # Take first few sentences up to max_words
        summary_sentences = []
        word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words > max_words and summary_sentences:
                break
            summary_sentences.append(sentence)
            word_count += sentence_words
        
        summary = ' '.join(summary_sentences)
        logger.info(f"Created extractive summary: {len(text)} chars -> {len(summary)} chars")
        return summary
