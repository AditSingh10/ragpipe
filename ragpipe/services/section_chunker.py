"""
Intelligent text chunking based on paper sections

Detects section headers in academic papers and creates meaningful chunks.
Focuses on numbered sections and common academic paper structure.
"""

import re
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Text chunk with section metadata"""
    content: str
    section_header: str
    section_level: int  # 1 = main section, 2 = subsection, etc.
    start_index: int
    end_index: int
    chunk_size: int

class SectionChunker:
    """Chunks paper text based on detected section headers"""
    
    def __init__(self, max_chunk_size: int = 2000, min_chunk_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.section_patterns = [
            (r'^\s*(\d+)\.\s+([A-Z][^.\n]*)', 1),
            (r'^\s*(\d+\.\d+(?:\.\d+)*)\s+([A-Z][^.\n]*)', 2),
            (r'^\s*(Abstract|Introduction|Conclusion|References|Bibliography|Appendix|Methods|Results|Discussion|Related Work|Background)', 1),
            (r'^\s*([A-Z][A-Za-z\s]+)(?=\n|$)', 2),
        ]
        
        # Additional patterns for common academic paper structures
        self.enhanced_patterns = [
            # Look for ALL CAPS lines (often section headers)
            (r'^\s*([A-Z][A-Z\s]+)$', 1),
            
            # Look for lines that are mostly capitalized (potential headers)
            (r'^\s*([A-Z][A-Za-z\s]*[A-Z][A-Za-z\s]*)$', 2),
            
            # Look for numbered lists that might be sections
            (r'^\s*(\d+\)\s+[A-Z][^.\n]*)', 2),
        ]
    
    def chunk_paper(self, text: str) -> List[TextChunk]:
        """
        Chunk paper text based on detected section headers
        
        Args:
            text: Raw text from PDF
            
        Returns:
            List of TextChunk objects
        """
        if not text:
            return []
        
        # Find all section headers and their positions
        section_positions = self._find_section_positions(text)
        
        if not section_positions:
            # No sections found, fall back to simple chunking
            return self._fallback_chunking(text)
        
        # Create chunks based on section boundaries
        chunks = self._create_chunks_from_sections(text, section_positions)
        
        # If chunks are too large, split them further
        final_chunks = self._split_large_chunks(chunks)
        
        # Filter out tiny chunks
        final_chunks = self._filter_tiny_chunks(final_chunks)
        
        return final_chunks
    
    def _find_section_positions(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Find all section headers and their positions
        
        Args:
            text: Full text to search
            
        Returns:
            List of (header_text, start_pos, level) tuples
        """
        sections = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Try primary patterns first
            for pattern, level in self.section_patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    # Calculate position in full text
                    start_pos = text.find(line)
                    if start_pos != -1:
                        header_text = line_stripped
                        sections.append((header_text, start_pos, level))
                        break  # Found a match for this line, move to next
            
            # If no primary pattern matched, try enhanced patterns
            else:
                for pattern, level in self.enhanced_patterns:
                    match = re.match(pattern, line_stripped)
                    if match:
                        # Additional validation: check if this looks like a real header
                        if self._is_likely_header(line_stripped):
                            start_pos = text.find(line)
                            if start_pos != -1:
                                header_text = line_stripped
                                sections.append((header_text, start_pos, level))
                                break
        
        # Sort by position
        sections.sort(key=lambda x: x[1])
        return sections
    
    def _is_likely_header(self, line: str) -> bool:
        """
        Determine if a line is likely to be a section header
        
        Args:
            line: Line to check
            
        Returns:
            True if line appears to be a header
        """
        # Skip very short lines (likely not headers)
        if len(line) < 3:
            return False
        
        # Skip very long lines (likely paragraphs, not headers)
        if len(line) > 100:
            return False
        
        # Skip lines that end with common sentence endings
        if line.endswith(('.', '!', '?')):
            return False
        
        # Skip lines that contain common paragraph indicators
        if any(word in line.lower() for word in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']):
            # Only if it's a short line that's mostly capitalized
            if len(line) < 30 and line.isupper():
                return True
            return False
        
        return True
    
    def _create_chunks_from_sections(self, text: str, section_positions: List[Tuple[str, int, int]]) -> List[TextChunk]:
        """
        Create chunks based on section boundaries
        
        Args:
            text: Full text
            section_positions: List of (header, position, level) tuples
            
        Returns:
            List of TextChunk objects
        """
        chunks = []
        
        for i, (header, start_pos, level) in enumerate(section_positions):
            # Determine end position (next section or end of text)
            if i + 1 < len(section_positions):
                end_pos = section_positions[i + 1][1]
            else:
                end_pos = len(text)
            
            # Extract content for this section
            content = text[start_pos:end_pos].strip()
            
            # Create chunk
            chunk = TextChunk(
                content=content,
                section_header=header,
                section_level=level,
                start_index=start_pos,
                end_index=end_pos,
                chunk_size=len(content)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_large_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """
        Split chunks that exceed the maximum size
        
        Args:
            chunks: List of chunks to potentially split
            
        Returns:
            List of chunks, with large ones split
        """
        final_chunks = []
        
        for chunk in chunks:
            if chunk.chunk_size <= self.max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split large chunk into smaller pieces
                sub_chunks = self._split_chunk_arbitrarily(chunk)
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    def _filter_tiny_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """
        Filter out chunks that are too small to be useful
        
        Args:
            chunks: List of chunks to filter
            
        Returns:
            List of chunks with tiny ones removed
        """
        filtered_chunks = []
        
        for chunk in chunks:
            # Skip chunks that are too small
            if chunk.chunk_size >= self.min_chunk_size:
                filtered_chunks.append(chunk)
            else:
                print(f"   Filtering out tiny chunk: '{chunk.section_header}' ({chunk.chunk_size} chars)")
        
        return filtered_chunks
    
    def _split_chunk_arbitrarily(self, chunk: TextChunk) -> List[TextChunk]:
        """
        Split a large chunk into smaller pieces using arbitrary boundaries
        
        Args:
            chunk: Chunk to split
            
        Returns:
            List of smaller chunks
        """
        sub_chunks = []
        content = chunk.content
        current_pos = 0
        
        while current_pos < len(content):
            # Calculate end position for this sub-chunk
            end_pos = min(current_pos + self.max_chunk_size, len(content))
            
            # Try to break at a sentence boundary
            if end_pos < len(content):
                # Look for sentence endings in the last 100 characters
                search_start = max(current_pos, end_pos - 100)
                search_text = content[search_start:end_pos]
                
                # Find last sentence ending
                last_period = search_text.rfind('.')
                last_exclamation = search_text.rfind('!')
                last_question = search_text.rfind('?')
                
                cut_point = max(last_period, last_exclamation, last_question)
                
                if cut_point > 0:
                    # Found a good sentence boundary
                    end_pos = search_start + cut_point + 1
            
            # Create sub-chunk
            sub_content = content[current_pos:end_pos].strip()
            if sub_content:
                sub_chunk = TextChunk(
                    content=sub_content,
                    section_header=chunk.section_header,
                    section_level=chunk.section_level,
                    start_index=chunk.start_index + current_pos,
                    end_index=chunk.start_index + end_pos,
                    chunk_size=len(sub_content)
                )
                sub_chunks.append(sub_chunk)
            
            current_pos = end_pos
        
        return sub_chunks
    
    def _fallback_chunking(self, text: str) -> List[TextChunk]:
        """
        Fallback chunking when no sections are detected
        
        Args:
            text: Text to chunk
            
        Returns:
            List of chunks
        """
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = min(current_pos + self.max_chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end_pos < len(text):
                search_start = max(current_pos, end_pos - 100)
                search_text = text[search_start:end_pos]
                
                last_period = search_text.rfind('.')
                last_exclamation = search_text.rfind('!')
                last_question = search_text.rfind('?')
                
                cut_point = max(last_period, last_exclamation, last_question)
                
                if cut_point > 0:
                    end_pos = search_start + cut_point + 1
            
            content = text[current_pos:end_pos].strip()
            if content:
                chunk = TextChunk(
                    content=content,
                    section_header="Unknown Section",
                    section_level=1,
                    start_index=current_pos,
                    end_index=end_pos,
                    chunk_size=len(content)
                )
                chunks.append(chunk)
            
            current_pos = end_pos
        
        return chunks

# Example usage and testing
if __name__ == "__main__":
    # Test with sample text
    chunker = SectionChunker(max_chunk_size=1500)
    
    sample_text = """
    Attention Is All You Need
    
    Abstract
    The dominant sequence transduction models are based on complex recurrent or
    convolutional neural networks that include an encoder and a decoder.
    
    1. Introduction
    Recurrent neural networks, long short-term memory and gated recurrent neural networks
    in particular, have been firmly established as state of the art approaches.
    
    2. Background
    The goal of reducing sequential computation also forms the foundation.
    
    2.1 Neural Networks
    Neural networks have been used for various tasks.
    
    3. Model Architecture
    Most competitive neural sequence transduction models have an encoder-decoder structure.
    """
    
    chunks = chunker.chunk_paper(sample_text)
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  {i+1}. {chunk.section_header} (Level {chunk.section_level})")
        print(f"     Size: {chunk.chunk_size} chars")
        print(f"     Preview: {chunk.content[:100]}...")
        print()
