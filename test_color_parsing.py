#!/usr/bin/env python3
import sys
import json
import re
sys.path.append('.')

def test_parsing():
    response_text = '''```json
{
  "primary_color": "#A0522D",
  "secondary_color": "#DEB887",
  "accent_color": "#FFD700",
  "neutral_color": "#F5F5DC",
  "background_color": "#FAEBD7",
  "text_color": "#36454F"
}
```'''
    
    print("Original response:")
    print(repr(response_text))
    
    # Clean the response text - remove markdown code blocks
    cleaned_text = response_text.strip()
    
    # Remove ```json and ``` markers if present
    if cleaned_text.startswith('```json'):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith('```'):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith('```'):
        cleaned_text = cleaned_text[:-3]
    
    cleaned_text = cleaned_text.strip()
    
    print('\nCleaned text:')
    print(repr(cleaned_text))
    
    # Try to extract JSON
    try:
        json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        if json_match:
            print('\nJSON match found:')
            json_text = json_match.group()
            print(repr(json_text))
            color_data = json.loads(json_text)
            print('\nParsed successfully:', color_data)
            
            # Extract colors
            palette = []
            color_keys = ['primary_color', 'secondary_color', 'accent_color', 
                         'neutral_color', 'background_color', 'text_color']
            
            for key in color_keys:
                if key in color_data and color_data[key]:
                    color = color_data[key].strip()
                    if color.startswith('#') and len(color) == 7:
                        palette.append(color)
            
            print(f'\nExtracted palette: {palette}')
            return palette
        else:
            print('No JSON match found')
    except Exception as e:
        print(f'JSON parsing error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_parsing()