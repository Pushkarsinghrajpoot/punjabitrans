import tempfile
import os
from pdf2image import convert_from_path
from PIL import Image
import streamlit as st

class PDFHandler:
    def __init__(self):
        pass
    
    def pdf_to_images(self, pdf_path, dpi=200):
        """
        Convert PDF pages to images for OCR processing
        
        Args:
            pdf_path (str): Path to the PDF file
            dpi (int): Resolution for image conversion (higher = better quality but slower)
            
        Returns:
            list: List of PIL Image objects
        """
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt='PNG',
                thread_count=2  # Limit threads for container environment
            )
            
            return images
            
        except Exception as e:
            st.error(f"Error converting PDF to images: {str(e)}")
            return []
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast and sharpness for better OCR
            from PIL import ImageEnhance
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            st.warning(f"Image preprocessing failed: {str(e)}")
            return image
    
    def validate_pdf(self, file_path):
        """
        Validate if the file is a proper PDF
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            # Try to open and read first page
            images = convert_from_path(file_path, first_page=1, last_page=1)
            return len(images) > 0
        except Exception:
            return False
