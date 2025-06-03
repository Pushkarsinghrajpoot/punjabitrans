import streamlit as st
import time
import re
import pandas as pd
import requests
import os
import json

class Translator:
    def __init__(self):
        # Set the API key for Google Cloud Translation API
        self.api_key = "AIzaSyCZl6-xJ7bFUleENKh3sVozTsR3kpEURq8"
        self.source_lang = 'pa'  # Punjabi language code for Google Translate
        self.target_lang = 'en'  # English language code
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate_to_english(self, punjabi_text):
        """
        Translate Punjabi text to English using Google Cloud Translate API
        
        Args:
            punjabi_text (str): Text in Punjabi to translate
            
        Returns:
            str: Translated English text
        """
        if not punjabi_text or not punjabi_text.strip():
            return ""
        
        try:
            # Clean the text before translation
            cleaned_text = self._clean_text_for_translation(punjabi_text)
            
            # Split text into chunks if it's too long (Google Translate has limits)
            chunks = self._split_text_into_chunks(cleaned_text)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Add a small delay between requests to avoid rate limiting
                    if i > 0:
                        time.sleep(0.2)
                    
                    try:
                        # Make direct API call to Google Cloud Translate API
                        url = f"{self.base_url}?key={self.api_key}"
                        payload = {
                            'q': chunk,
                            'source': self.source_lang,
                            'target': self.target_lang,
                            'format': 'text'
                        }
                        
                        response = requests.post(url, json=payload)
                        if response.status_code == 200:
                            result = response.json()
                            translated_text = result['data']['translations'][0]['translatedText']
                            # Post-process the translated text
                            processed_text = self._post_process_translation(translated_text)
                            translated_chunks.append(processed_text)
                        else:
                            error_msg = f"API Error: {response.status_code} - {response.text}"
                            st.warning(error_msg)
                            translated_chunks.append(f"[Translation failed for this section: {chunk[:50]}...]")
                    except Exception as chunk_error:
                        st.warning(f"Failed to translate chunk {i+1}: {str(chunk_error)}")
                        translated_chunks.append(f"[Translation failed for this section: {chunk[:50]}...]")
            
            final_translation = '\n'.join(translated_chunks)
            return self._final_cleanup(final_translation)
            
        except Exception as e:
            st.error(f"Translation failed: {str(e)}")
            return f"Translation error: {str(e)}"
    
    def _clean_text_for_translation(self, text):
        """
        Clean text before translation for better results
        
        Args:
            text (str): Input text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove excessive spaces
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _post_process_translation(self, translated_text):
        """
        Post-process translated text for better formatting
        
        Args:
            translated_text (str): Raw translated text
            
        Returns:
            str: Post-processed text
        """
        if not translated_text:
            return ""
        
        # Fix common translation issues
        text = translated_text
        
        # Capitalize proper nouns and building names
        text = self._capitalize_building_names(text)
        
        # Fix common word corrections and format standardization
        corrections = {
            'polling station': 'Polling Station',
            'primary school': 'Primary School',
            'secondary school': 'Secondary School',
            'high school': 'High School',
            'government school': 'Government School',
            'govt.': 'Government',
            'govt': 'Government',
            'sr.': 'Senior',
            'sr': 'Senior',
            'sec.': 'Secondary',
            'sec': 'Secondary',
            'community hall': 'Community Hall',
            'village panchayat': 'Village Panchayat',
            'panchayat ghar': 'Panchayat Ghar',
            'anganwadi center': 'Anganwadi Center',
            'junior high school': 'Junior High School',
            'middle school': 'Middle School',
            'municipal council': 'Municipal Council',
            'gram panchayat': 'Gram Panchayat'
        }

        for old, new in corrections.items():
            # Use word boundary for more accurate replacements
            pattern = r'\b' + re.escape(old) + r'\b'
            text = re.sub(pattern, new, text, flags=re.IGNORECASE)
        
        return text
    
    def _capitalize_building_names(self, text):
        """
        Capitalize building names and important words
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with capitalized building names
        """
        # List of important building types and keywords that should be capitalized
        building_keywords = [
            'school', 'college', 'university', 'institute', 'hall', 'center', 'centre',
            'complex', 'stadium', 'hospital', 'clinic', 'dispensary', 'office', 'bank',
            'library', 'museum', 'theater', 'theatre', 'cinema', 'mall', 'market',
            'bazaar', 'station', 'terminal', 'airport', 'port', 'depot', 'headquarters',
            'hq', 'ministry', 'department', 'authority', 'agency', 'committee', 'commission',
            'council', 'board', 'academy', 'institution', 'association', 'society',
            'foundation', 'trust', 'corporation', 'company', 'enterprise', 'store',
            'shop', 'boutique', 'outlet', 'showroom', 'gallery', 'studio', 'court',
            'tribunal', 'judiciary', 'temple', 'church', 'mosque', 'monastery', 'shrine',
            'parliament', 'assembly', 'secretariat', 'directorate', 'pavilion',
            'auditorium', 'gymnasium', 'aquarium', 'planetarium', 'observatory',
            'laboratory', 'workshop', 'factory', 'mill', 'refinery', 'distillery',
            'brewery', 'winery', 'bakery', 'restaurant', 'cafe', 'canteen', 'hostel',
            'dormitory', 'residence', 'apartment', 'flat', 'bungalow', 'villa', 'palace',
            'fort', 'castle', 'tower', 'mansion', 'cottage', 'farm', 'estate', 'garden',
            'park', 'playground', 'zoo', 'sanctuary', 'reserve', 'panchayat', 'hotel'
        ]
        
        # Join all keywords with a pipe (|) for regex OR pattern
        building_pattern = '|'.join(r'\b' + re.escape(kw) + r'\b' for kw in building_keywords)
        
        # Function to capitalize matches
        def capitalize_match(match):
            return match.group(0).capitalize()
        
        # Apply capitalization
        return re.sub(building_pattern, capitalize_match, text, flags=re.IGNORECASE)
    
    def _final_cleanup(self, text):
        """
        Final cleanup of translated text
        
        Args:
            text (str): Input text
            
        Returns:
            str: Final cleaned text
        """
        if not text:
            return ""
        
        # Process lines to normalize spaces while preserving newlines
        input_lines = text.split('\n')
        processed_lines_for_cleanup = []
        for line_content in input_lines:
            # Collapse multiple spaces within the line to a single space, then strip leading/trailing
            processed_line = ' '.join(line_content.split()).strip()
            # Keep the line if it's not empty after processing (this also handles lines that were just whitespace)
            if processed_line:
                processed_lines_for_cleanup.append(processed_line)
            # If original line was empty or only whitespace, and we want to preserve it as an empty line:
            # elif not line_content.strip(): # Check if original line was empty or all whitespace
            #    processed_lines_for_cleanup.append("") # Add back an empty line if desired
        text = '\n'.join(processed_lines_for_cleanup)

        # Fix spacing around punctuation (applied to the already line-processed text)
        text = re.sub(r'\s+([.,;:!?)])', r'\1', text) # Remove space before punc
        text = re.sub(r'([({[<])\s+', r'\1', text) # Remove space after opening punc
        text = re.sub(r'([.,;:!?)])(\S)', r'\1 \2', text) # Add space after punc if followed by non-space (handles cases like "word.Nextword")
        text = re.sub(r'(\S)([{([<])', r'\1 \2', text) # Add space before opening punc if preceded by non-space

        # Fix common HTML entities that might appear in translation
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&#39;': "'"
        }
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Fix spacing around URLs (if any) - this might need to be more robust
        # text = re.sub(r'(https?://\S+)\s', r'\1 ', text) # Original - might add trailing space
        # This ensures a space after a URL if it's followed by a non-space, non-punctuation character
        text = re.sub(r'(https?://\S+)(?=[^\s.,;:!?)])', r'\1 ', text)

        # The final strip and rejoin is to ensure consistent line endings and remove any fully empty lines created by previous steps
        # if we didn't explicitly preserve them.
        final_lines_pass = text.split('\n')
        final_cleaned_lines = []
        for final_line in final_lines_pass:
            stripped_line = final_line.strip()
            if stripped_line:
                final_cleaned_lines.append(stripped_line)
        text = '\n'.join(final_cleaned_lines)
        
        return text
    
    def _split_text_into_chunks(self, text, max_chunk_size=4500):
        """
        Split text into smaller chunks for translation
        Google Translate has a character limit per request
        
        Args:
            text (str): Input text to split
            max_chunk_size (int): Maximum characters per chunk
            
        Returns:
            list: List of text chunks
        """
        if not text:
            return []
        
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for the newline character
            
            if current_length + line_length <= max_chunk_size:
                current_chunk.append(line)
                current_length += line_length
            else:
                # If the current line is too long, break it further
                if line_length > max_chunk_size:
                    # First append the current chunk if it's not empty
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    
                    # Break long line into multiple chunks
                    for i in range(0, len(line), max_chunk_size):
                        sub_chunk = line[i:i + max_chunk_size]
                        chunks.append(sub_chunk)
                else:
                    # Append the current chunk and start a new one
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                    current_length = line_length
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def detect_language(self, text):
        """
        Detect the language of the input text
        
        Args:
            text (str): Input text
            
        Returns:
            str: Detected language code
        """
        try:
            # Make direct API call to Google Cloud Translate API for language detection
            url = f"https://translation.googleapis.com/language/translate/v2/detect?key={self.api_key}"
            payload = {'q': text}
            
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['data']['detections'][0][0]['language']
            else:
                st.warning(f"API Error: {response.status_code} - {response.text}")
                return "unknown"
        except Exception as e:
            st.error(f"Language detection error: {str(e)}")
            return "unknown"
    
    def translate_with_confidence(self, text):
        """
        Translate text and return confidence information
        
        Args:
            text (str): Input text to translate
            
        Returns:
            dict: Translation result with confidence info
        """
        try:
            # First detect the language for source confidence
            detect_url = f"https://translation.googleapis.com/language/translate/v2/detect?key={self.api_key}"
            detect_payload = {'q': text}
            
            detect_response = requests.post(detect_url, json=detect_payload)
            if detect_response.status_code != 200:
                raise Exception(f"Detection API error: {detect_response.status_code} - {detect_response.text}")
                
            detect_result = detect_response.json()
            source_lang = detect_result['data']['detections'][0][0]['language']
            source_confidence = detect_result['data']['detections'][0][0].get('confidence', 0)
            
            # Then translate
            translate_url = f"{self.base_url}?key={self.api_key}"
            translate_payload = {
                'q': text,
                'source': source_lang,
                'target': self.target_lang,
                'format': 'text'
            }
            
            translate_response = requests.post(translate_url, json=translate_payload)
            if translate_response.status_code != 200:
                raise Exception(f"Translation API error: {translate_response.status_code} - {translate_response.text}")
                
            translate_result = translate_response.json()
            translated_text = translate_result['data']['translations'][0]['translatedText']
            
            return {
                'source_language': source_lang,
                'source_confidence': source_confidence,
                'translation': translated_text,
                'translation_language': self.target_lang
            }
        except Exception as e:
            st.error(f"Translation with confidence error: {str(e)}")
            return {
                'source_language': 'unknown',
                'source_confidence': None,
                'translation': f"Translation error: {str(e)}",
                'translation_language': None
            }

    def format_translated_text_to_dataframe(self, text):
        """
        Parses the voter list text to extract polling station and voter details.
        This is a simplified parser and might need adjustments for variations in text format.
        """
        data = []
        lines = text.split('\n')
        current_polling_station_no = None
        current_polling_station_address = None
        current_sections_covered = []

        # Define ps_header_keywords once outside the loop for efficiency.
        ps_header_keywords = [
            "school", "vidyalaya", "pathshala",  # General school terms
            "government", "govt", "sarkari", # Government related
            "private", "pvt", # Private
            "primary", "middle", "high", "sr. sec", "c.sec", "c.secondary", "s.s.s.school", "el.", "gau.eli", # School types/levels
            "rigging and plant reaction sub dvt", "dvt", # Specific entities
            "s.middle", "s.pr.school", "s.p. school", "s.e.school", # Specific school prefixes
            "shaheed captain arun singh jasrotia", # Specific names
            "harijan dharamshala", "dharamshala", # Building types
            "lajpat rai", "m.s.d.rajput", "smsd rajput" # Specific school names/prefixes
        ]
        # Pattern to find the start of a section detail (e.g., "1: Village Name...") on the same line as PS header
        section_on_same_line_pattern = re.compile(r'(\d+\s*:\s*.*)')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Attempt to match as a polling station header
            match_potential_ps_line = re.match(r'(\d+)\s+(.*)', line)
            is_ps_header = False
            if match_potential_ps_line:
                potential_ps_no_text = match_potential_ps_line.group(1)
                text_after_number = match_potential_ps_line.group(2).strip().lower()
                if any(keyword in text_after_number for keyword in ps_header_keywords):
                    is_ps_header = True

            if is_ps_header:
                # If we have accumulated sections for a previous PS, add them to data
                if current_polling_station_no and current_sections_covered:
                    data.append([
                        current_polling_station_no,
                        current_polling_station_address,
                        "\n".join(current_sections_covered) # Join accumulated sections
                    ])
                    current_sections_covered = [] # Reset for the new PS
                
                # Update to the new polling station
                current_polling_station_no = potential_ps_no_text
                
                full_text_after_ps_number = match_potential_ps_line.group(2).strip()
                match_section_part = section_on_same_line_pattern.search(full_text_after_ps_number)

                if match_section_part:
                    # Section detail found on the same line as the polling station address
                    current_polling_station_address = full_text_after_ps_number[:match_section_part.start()].strip()
                    first_section_text_on_ps_line = match_section_part.group(1).strip()
                    if first_section_text_on_ps_line: # Ensure it's not empty
                        current_sections_covered.append(first_section_text_on_ps_line)
                else:
                    # No section detail found on the same line, so the full text is the address
                    current_polling_station_address = full_text_after_ps_number
                
            elif current_polling_station_no: # If it's not a PS header and we are under a PS
                current_sections_covered.append(line) # Add to current PS's sections
            # Lines before the first polling station header are ignored if they are not PS headers themselves

        # Add the last polling station's data if any sections were accumulated
        if current_polling_station_no and current_sections_covered:
            data.append([
                current_polling_station_no,
                current_polling_station_address,
                "\n".join(current_sections_covered)
            ])

        df = pd.DataFrame(data, columns=[
            'Polling Station Number',
            'Building and Address',
            'Sections Covered'
        ])

        return df
