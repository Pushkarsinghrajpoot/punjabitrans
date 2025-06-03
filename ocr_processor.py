import pytesseract
from PIL import Image
import streamlit as st
import os

class OCRProcessor:
    def __init__(self):
        self.punjabi_config = '--oem 3 --psm 6 -l pan'  # pan is the Tesseract language code for Punjabi
        
    def extract_punjabi_text(self, image):
        """
        Extract Punjabi text from an image using Tesseract OCR
        
        Args:
            image (PIL.Image): Input image containing Punjabi text
            
        Returns:
            str: Extracted Punjabi text
        """
        try:
            # Preprocess image for better OCR
            processed_image = self._preprocess_for_ocr(image)
            
            # Perform OCR with Punjabi language support
            text = pytesseract.image_to_string(
                processed_image,
                config=self.punjabi_config
            )
            
            # Clean up the extracted text
            cleaned_text = self._clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            st.error(f"OCR processing failed: {str(e)}")
            return ""
    
    def _preprocess_for_ocr(self, image):
        """
        Preprocess image specifically for OCR optimization
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            # Convert to grayscale for better OCR performance
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if image is too small (OCR works better with larger images)
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000/width, 1000/height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            st.warning(f"Image preprocessing for OCR failed: {str(e)}")
            return image
    
    def _clean_text(self, text):
        """
        Clean and format extracted text
        
        Args:
            text (str): Raw OCR output
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and empty lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_ocr_confidence(self, image):
        """
        Get OCR confidence score for the extracted text
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            float: Average confidence score (0-100)
        """
        try:
            processed_image = self._preprocess_for_ocr(image)
            
            # Get detailed OCR data including confidence scores
            data = pytesseract.image_to_data(
                processed_image,
                config=self.punjabi_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence for words with confidence > 0
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.0
                
        except Exception as e:
            st.warning(f"Could not calculate OCR confidence: {str(e)}")
            return 0.0
    
    def check_tesseract_punjabi_support(self):
        """
        Check if Tesseract has Punjabi language support installed
        
        Returns:
            bool: True if Punjabi is supported, False otherwise
        """
        try:
            available_languages = pytesseract.get_languages()
            return 'pan' in available_languages
        except Exception:
            return False
