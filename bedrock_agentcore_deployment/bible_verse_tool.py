#!/usr/bin/env python3
"""
Bible Verse Tool for Strands-Agents SDK
Fetches random daily Bible verses from various Bible APIs
"""

import os
import requests
import random
from datetime import datetime
from strands import tool


@tool
def get_daily_bible_verse() -> str:
    """
    Get a random daily Bible verse from Bible APIs.
    
    Returns:
        A formatted string with the Bible verse, reference, and inspirational message
    """
    try:
        # Try multiple Bible APIs for reliability
        verse_data = None
        
        # Method 1: Try Bible API (bible-api.com)
        try:
            print("📖 Fetching Bible verse from bible-api.com...")
            response = requests.get("https://labs.bible.org/api/?passage=votd&type=json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                text = data[0].get("text", "").strip()
                book = verse_data.get("bookname", "")
                chapter = verse_data.get("chapter", "")
                verse = verse_data.get("verse", "")
                reference = f"{book} {chapter}:{verse}"
            
                verse_data = {
                    "text": text,
                    "reference": reference,
                    "source": "bible.org"
                }
        except Exception as e:
            print(f"Bible API failed: {e}")
        
        # Method 2: Try Labs Bible API if first failed
        if not verse_data:
            try:
                print("📖 Fetching Bible verse from labs.bible.org...")
                # Use a predefined list of popular verses as fallback
                popular_verses = [
                    {
                        "text": "For I know the plans I have for you, declares the Lord, plans for welfare and not for evil, to give you a future and a hope.",
                        "reference": "Jeremiah 29:11"
                    },
                    {
                        "text": "Trust in the Lord with all your heart, and do not lean on your own understanding. In all your ways acknowledge him, and he will make straight your paths.",
                        "reference": "Proverbs 3:5-6"
                    },
                    {
                        "text": "And we know that for those who love God all things work together for good, for those who are called according to his purpose.",
                        "reference": "Romans 8:28"
                    },
                    {
                        "text": "Be strong and courageous. Do not fear or be in dread of them, for it is the Lord your God who goes with you. He will not leave you or forsake you.",
                        "reference": "Deuteronomy 31:6"
                    },
                    {
                        "text": "The Lord is my shepherd; I shall not want. He makes me lie down in green pastures. He leads me beside still waters.",
                        "reference": "Psalm 23:1-2"
                    },
                    {
                        "text": "Have I not commanded you? Be strong and courageous. Do not be frightened, and do not be dismayed, for the Lord your God is with you wherever you go.",
                        "reference": "Joshua 1:9"
                    },
                    {
                        "text": "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint.",
                        "reference": "Isaiah 40:31"
                    },
                    {
                        "text": "And my God will meet all your needs according to the riches of his glory in Christ Jesus.",
                        "reference": "Philippians 4:19"
                    },
                    {
                        "text": "Cast all your anxiety on him because he cares for you.",
                        "reference": "1 Peter 5:7"
                    },
                    {
                        "text": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
                        "reference": "John 3:16"
                    }
                ]
                
                # Select a verse based on the day to ensure consistency
                day_of_year = datetime.now().timetuple().tm_yday
                selected_verse = popular_verses[day_of_year % len(popular_verses)]
                
                verse_data = {
                    "text": selected_verse["text"],
                    "reference": selected_verse["reference"],
                    "source": "curated collection"
                }
                
            except Exception as e:
                print(f"Fallback verse selection failed: {e}")
        
        # Format the response
        if verse_data:
            formatted_verse = f"""
📖 Daily Bible Verse

"{verse_data['text']}"

— {verse_data['reference']}

🙏 May this verse bring you peace, strength, and inspiration today.

📅 {datetime.now().strftime('%A, %B %d, %Y')}
            """.strip()
            
            return formatted_verse
        else:
            # Ultimate fallback
            return f"""
📖 Daily Bible Verse

"Trust in the Lord with all your heart, and do not lean on your own understanding. In all your ways acknowledge him, and he will make straight your paths."

— Proverbs 3:5-6

🙏 May this verse bring you peace, strength, and inspiration today.

📅 {datetime.now().strftime('%A, %B %d, %Y')}
            """.strip()
            
    except Exception as e:
        return f"""
📖 Daily Bible Verse

"Be strong and courageous. Do not fear or be in dread of them, for it is the Lord your God who goes with you. He will not leave you or forsake you."

— Deuteronomy 31:6

🙏 May this verse bring you peace, strength, and inspiration today.

📅 {datetime.now().strftime('%A, %B %d, %Y')}

Note: Unable to fetch from external APIs, but here's an encouraging verse for you.
        """.strip()


@tool
def get_bible_verse_for_posting() -> str:
    """
    Get a Bible verse formatted specifically for social media posting.
    
    Returns:
        A concise Bible verse formatted for X (Twitter) posting
    """
    try:
        # Get the full verse
        full_verse = get_daily_bible_verse()
        
        # Extract just the verse text and reference for social media
        lines = full_verse.split('\n')
        verse_text = ""
        reference = ""
        
        for line in lines:
            if line.startswith('"') and line.endswith('"'):
                verse_text = line.strip('"')
            elif line.startswith('—'):
                reference = line.replace('—', '').strip()
        
        # Format for social media (keep it concise for Twitter)
        if len(verse_text) > 200:  # If verse is too long, truncate
            verse_text = verse_text[:197] + "..."
        
        social_post = f'{verse_text}" — {reference}\n\n#BibleVerse #DailyInspiration #Faith'
        
        return social_post
        
    except Exception as e:
        # Fallback social media post
        return f'"Trust in the Lord with all your heart, and do not lean on your own understanding."\n\n— Proverbs 3:5-6\n\n#BibleVerse #DailyInspiration #Faith'


# Test function for development
def test_bible_verse_tool():
    """Test the Bible verse tool functionality"""
    print("Testing Bible verse tool...")
    
    # Test full verse
    result = get_daily_bible_verse()
    print("Full Bible verse:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test social media version
    result = get_bible_verse_for_posting()
    print("Social media version:")
    print(result)
    print(f"Length: {len(result)} characters")


if __name__ == "__main__":
    test_bible_verse_tool()