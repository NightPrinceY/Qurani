"""
Tajweed Rule Analyzer
Maps text positions to audio timestamps and analyzes specific segments
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger("TAJWEED_ANALYZER")

class TajweedAnalyzer:
    def __init__(self, tajweed_dir: Path, surah_dir: Path):
        self.tajweed_dir = tajweed_dir
        self.surah_dir = surah_dir
        self.tajweed_cache = {}
        self.surah_cache = {}
    
    def load_tajweed_data(self, surah_index: str) -> Optional[Dict]:
        """Load Tajweed rules for a surah"""
        if surah_index in self.tajweed_cache:
            return self.tajweed_cache[surah_index]
        
        tajweed_file = self.tajweed_dir / f"surah_{surah_index}.json"
        if not tajweed_file.exists():
            return None
        
        try:
            with open(tajweed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.tajweed_cache[surah_index] = data
            return data
        except Exception as e:
            logger.error(f"Failed to load tajweed data for surah {surah_index}: {e}")
            return None
    
    def load_surah_data(self, surah_index: str) -> Optional[Dict]:
        """Load surah verse text"""
        if surah_index in self.surah_cache:
            return self.surah_cache[surah_index]
        
        surah_file = self.surah_dir / f"surah_{surah_index}.json"
        if not surah_file.exists():
            return None
        
        try:
            with open(surah_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.surah_cache[surah_index] = data
            return data
        except Exception as e:
            logger.error(f"Failed to load surah data for surah {surah_index}: {e}")
            return None
    
    def find_matching_verse(self, transcript: str, surah_index: str) -> Optional[Tuple[str, str]]:
        """
        Find which verse in the surah matches the transcript
        Returns: (verse_key, expected_text) or None
        """
        surah_data = self.load_surah_data(surah_index)
        if not surah_data:
            return None
        
        # Clean transcript (remove diacritics variation, whitespace)
        transcript_clean = self._clean_text(transcript)
        
        best_match = None
        best_score = 0.0
        
        for verse_key, expected_text in surah_data.get("verse", {}).items():
            expected_clean = self._clean_text(expected_text)
            # Calculate similarity
            similarity = self._text_similarity(transcript_clean, expected_clean)
            
            if similarity > best_score:
                best_score = similarity
                best_match = (verse_key, expected_text)
                
                # If very high similarity, return immediately
                if similarity > 0.95:
                    break
        
        if best_score > 0.7:  # Reasonable threshold
            return best_match
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for comparison"""
        # Remove extra whitespace, normalize
        import re
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove some diacritics variations for matching
        return text
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple Jaccard on character sets)"""
        if not text1 or not text2:
            return 0.0
        
        set1 = set(text1.replace(' ', ''))
        set2 = set(text2.replace(' ', ''))
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def map_text_positions_to_audio(
        self, 
        transcript: str, 
        expected_text: str, 
        word_timestamps: List[Dict],
        audio_duration: float
    ) -> Dict[int, Tuple[float, float]]:
        """
        Map character positions in expected text to audio timestamps
        Returns: {char_position: (start_time, end_time)}
        """
        # Create mapping from character positions to timestamps
        position_to_time = {}
        
        # Remove diacritics and normalize for alignment
        expected_clean = expected_text.replace(' ', '').replace('ٱ', '').replace('ۖ', '').replace('ۭ', '')
        transcript_clean = transcript.replace(' ', '').replace('ٱ', '').replace('ۖ', '').replace('ۭ', '')
        
        # Simple approach: map character positions proportionally
        # Calculate time per character based on expected text length
        if len(expected_clean) > 0:
            time_per_char = audio_duration / len(expected_clean)
            
            # Create position map for expected text (with spaces)
            char_idx = 0
            for char in expected_text:
                if char.strip():  # Not a space
                    position_to_time[char_idx] = (
                        char_idx * time_per_char,
                        (char_idx + 1) * time_per_char
                    )
                char_idx += 1
        
        # If we have word timestamps, try to refine the mapping
        if word_timestamps and len(word_timestamps) > 0:
            # Try to align words more precisely
            expected_words = expected_text.split()
            transcript_words = transcript.split()
            
            char_idx = 0
            word_idx = 0
            
            for expected_word in expected_words:
                expected_word_clean = self._clean_text(expected_word).replace(' ', '')
                found_match = False
                
                # Try to find matching word in transcript
                for i in range(word_idx, min(word_idx + 3, len(transcript_words))):
                    transcript_word_clean = self._clean_text(transcript_words[i]).replace(' ', '')
                    if self._text_similarity(expected_word_clean, transcript_word_clean) > 0.6:
                        # Found approximate match
                        if i < len(word_timestamps):
                            word_start = word_timestamps[i].get('start', 0.0)
                            word_end = word_timestamps[i].get('end', word_start + 0.5)
                            
                            # Update character positions for this word
                            word_len = len(expected_word.replace(' ', ''))
                            if word_len > 0:
                                time_per_char_word = (word_end - word_start) / word_len
                                word_char_start = char_idx
                                for j in range(word_len):
                                    position_to_time[word_char_start + j] = (
                                        word_start + j * time_per_char_word,
                                        word_start + (j + 1) * time_per_char_word
                                    )
                                char_idx += word_len
                            word_idx = i + 1
                            found_match = True
                            break
                
                if not found_match:
                    # Use proportional mapping
                    word_len = len(expected_word.replace(' ', ''))
                    char_idx += word_len
                char_idx += 1  # Space after word
        
        return position_to_time
    
    def get_tajweed_rules_for_verse(
        self, 
        surah_index: str, 
        verse_key: str
    ) -> List[Dict]:
        """Get expected Tajweed rules for a specific verse"""
        tajweed_data = self.load_tajweed_data(surah_index)
        if not tajweed_data:
            return []
        
        verse_rules = tajweed_data.get("verse", {}).get(verse_key, [])
        return verse_rules
    
    def extract_audio_segment(
        self, 
        audio: np.ndarray, 
        start_char: int, 
        end_char: int, 
        position_map: Dict[int, Tuple[float, float]]
    ) -> np.ndarray:
        """
        Extract audio segment corresponding to character positions
        """
        # Find time range for these character positions
        start_time = None
        end_time = None
        
        for char_pos in range(start_char, min(end_char + 1, len(position_map))):
            if char_pos in position_map:
                char_start, char_end = position_map[char_pos]
                if start_time is None or char_start < start_time:
                    start_time = char_start
                if end_time is None or char_end > end_time:
                    end_time = char_end
        
        # Add some padding (100ms before and after)
        padding = 0.1
        start_time = max(0, start_time - padding) if start_time else 0
        end_time = min(len(audio) / SAMPLE_RATE, end_time + padding) if end_time else len(audio) / SAMPLE_RATE
        
        # Extract segment
        start_sample = int(start_time * SAMPLE_RATE)
        end_sample = int(end_time * SAMPLE_RATE)
        
        segment = audio[start_sample:end_sample]
        
        # Ensure minimum length
        min_length = int(0.1 * SAMPLE_RATE)  # 100ms minimum
        if len(segment) < min_length:
            # Pad with zeros
            segment = np.pad(segment, (0, min_length - len(segment)), mode='constant')
        
        return segment

# SAMPLE_RATE constant
SAMPLE_RATE = 16000

