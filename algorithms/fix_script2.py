with open('68_continuous_adaptive_search.py', 'r') as file:
    lines = file.readlines()

# Fix the second RIPEMD160 error handling
lines[3827] = '        except (Exception, ValueError) as e:\n'

with open('68_continuous_adaptive_search.py', 'w') as file:
    file.writelines(lines)

print("Second fix applied successfully")
