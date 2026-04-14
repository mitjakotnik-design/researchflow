"""Test the consistency validator."""

import asyncio
import sys
sys.path.insert(0, '.')
from agents.consistency_validator import ConsistencyValidatorAgent

async def test():
    # Read article
    with open('output/article_scoping_review.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Validate
    validator = ConsistencyValidatorAgent()
    validator.set_canonical_values({
        'timeframe_start': '2015',
        'timeframe_end': '2025',
    })
    validator.on_initialize()
    
    result = await validator._validate_article(content)
    print('=' * 60)
    print('CONSISTENCY VALIDATION RESULT')
    print('=' * 60)
    print(f'Valid: {result["valid"]}')
    print(f'Errors: {result["errors"]}')
    print(f'Warnings: {result["warnings"]}')
    print()
    
    if result['issues']:
        print('Issues found:')
        for issue in result['issues']:
            print(f'  [{issue["severity"].upper()}] {issue["issue_type"]}:')
            print(f'    Found: "{issue["found"]}"')
            print(f'    Expected: "{issue["expected"]}"')
    else:
        print('No issues found!')

if __name__ == "__main__":
    asyncio.run(test())
