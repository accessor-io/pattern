with open('68_continuous_adaptive_search.py', 'r') as file:
    content = file.read()

# Fix RIPEMD160 error handling
content = content.replace(
    "        except Exception:",
    "        except (Exception, ValueError) as e:",
    2  # Replace first 2 occurrences
)

# Fix region size limit
content = content.replace(
    "    if region_size <= 62:  # Safe limit for bit operations",
    "    if region_size <= 30:  # Reduced limit to prevent overflow"
)

with open('68_continuous_adaptive_search.py', 'w') as file:
    file.write(content)

print("File fixed successfully")
