import re
from deep_translator import GoogleTranslator


def translate_to_english(text: str) -> str:
    if not text:
        return ""
    try:
        return GoogleTranslator(source='id', target='en').translate(text)
    except Exception:
        return text


def translate_to_indonesian(text: str) -> str:
    if not text:
        return ""
    try:
        result = GoogleTranslator(source='en', target='id').translate(text)
        result = re.sub(r'(\d+)\s*ton\b', r'\1 sendok teh', result)

        fraction_map = {0.25: "¼", 0.5: "½", 0.75: "¾", 0.33: "⅓", 0.67: "⅔", 0.66: "⅔"}

        def format_decimal(match):
            num = float(match.group(0))
            if num.is_integer():
                return str(int(num))
            integer_part = int(num)
            decimal_part = round(num - integer_part, 2)
            if decimal_part in fraction_map:
                frac = fraction_map[decimal_part]
                return f"{integer_part} {frac}" if integer_part > 0 else frac
            return f"{num:.2f}"

        result = result.replace(',', '.')
        result = re.sub(r'\d+\.\d+', format_decimal, result)
        result = re.sub(r'(\d+|¼|½|¾|⅓|⅔)\s*(c|cup|cups)\b\.?',        r'\1 cangkir',      result)
        result = re.sub(r'\b(c|cup|cups)\b',                               'cangkir',          result)
        result = re.sub(r'(\d+|¼|½|¾|⅓|⅔)\s*(tbsp|tablespoon|tablespoons)\b\.?', r'\1 sendok makan', result)
        result = re.sub(r'(\d+|¼|½|¾|⅓|⅔)\s*(tsp|teaspoon|teaspoons)\b\.?',      r'\1 sendok teh',   result)
        result = re.sub(r'\b(gallon|gallons|gal)\b', 'galon',              result)
        result = re.sub(r'\bcangkir\s+cangkir\b',    'cangkir',            result)
        return result
    except Exception:
        return text
