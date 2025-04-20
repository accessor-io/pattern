#!/usr/bin/env python3

def parse_priority_string(input_str):
    """Parse a string containing numbers with varying levels of importance (!s)"""
    items = []
    
    # Split and process each item
    for item in input_str.split():
        # Count exclamation marks
        exclamations = item.count('!')
        # Get the base number
        number = int(''.join(c for c in item if c.isdigit()))
        items.append({
            'number': number,
            'priority_level': exclamations,
            'original': item
        })
    
    return items

def analyze_priorities(items):
    """Analyze and categorize items based on their priority levels"""
    # Sort by priority level (descending) and then by number
    sorted_items = sorted(items, key=lambda x: (-x['priority_level'], x['number']))
    
    # Group by priority level
    priority_groups = {}
    for item in items:
        level = item['priority_level']
        if level not in priority_groups:
            priority_groups[level] = []
        priority_groups[level].append(item)
    
    return {
        'sorted_items': sorted_items,
        'priority_groups': priority_groups,
        'max_priority': max(item['priority_level'] for item in items),
        'min_priority': min(item['priority_level'] for item in items),
        'priority_levels': len(priority_groups)
    }

def generate_report(input_str, analysis):
    """Generate a detailed report of the priority analysis"""
    with open('priority_report.txt', 'w') as f:
        # Input summary
        f.write("Priority Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Input sequence: {input_str}\n\n")
        
        # Priority statistics
        f.write("Priority Statistics:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Number of priority levels: {analysis['priority_levels']}\n")
        f.write(f"Highest priority level: {analysis['max_priority']} (!)\n")
        f.write(f"Lowest priority level: {analysis['min_priority']} (!)\n\n")
        
        # Items by priority level
        f.write("Priority Groups:\n")
        f.write("-" * 20 + "\n")
        for level in sorted(analysis['priority_groups'].keys(), reverse=True):
            items = analysis['priority_groups'][level]
            priority_label = "!!!" * level if level > 0 else "No priority"
            f.write(f"\nPriority Level {level} ({priority_label}):\n")
            for item in sorted(items, key=lambda x: x['number']):
                f.write(f"  • {item['original']} (Number: {item['number']})\n")
        
        # Sorted list by priority
        f.write("\nItems Sorted by Priority (Highest to Lowest):\n")
        f.write("-" * 20 + "\n")
        for item in analysis['sorted_items']:
            priority_str = "!" * item['priority_level'] if item['priority_level'] > 0 else "none"
            f.write(f"  • {item['original']} (Priority: {priority_str})\n")
        
        # Priority distribution
        f.write("\nPriority Level Distribution:\n")
        f.write("-" * 20 + "\n")
        total_items = len(analysis['sorted_items'])
        for level in sorted(analysis['priority_groups'].keys(), reverse=True):
            count = len(analysis['priority_groups'][level])
            percentage = (count / total_items) * 100
            f.write(f"Level {level}: {count} items ({percentage:.1f}%)\n")

def main():
    # Input sequence
    input_str = "1 2! 3 4! 5! 6!!! 7"
    
    # Parse and analyze
    items = parse_priority_string(input_str)
    analysis = analyze_priorities(items)
    
    # Generate report
    generate_report(input_str, analysis)
    
    print("Priority analysis report has been generated in 'priority_report.txt'")

if __name__ == "__main__":
    main() 