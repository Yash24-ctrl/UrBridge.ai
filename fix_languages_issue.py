# Script to fix the languages counting issue in app.py

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the three instances where languages are incorrectly converted
# 1. In analyzer route
content = content.replace(
    "languages=int(float(data.get('languages_known', 0))),",
    "languages=count_languages(data.get('languages_known', '')),"
)

# 2. In pdf_upload route  
content = content.replace(
    "                                languages=int(float(data.get('languages_known', 0))),",
    "                                languages=count_languages(data.get('languages_known', '')),"
)

# 3. In manual_input route
content = content.replace(
    "                    languages=int(data.get('languages_known', 0)),",
    "                    languages=count_languages(data.get('languages_known', '')),"
)

# Write the fixed content back to the file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed the languages counting issue in app.py")