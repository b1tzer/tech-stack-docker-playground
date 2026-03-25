import re
import os

with open('infra/redis/Makefile', 'r') as f:
    content = f.read()

targets = ['test-failover', 'test-persistence', 'test-bigkey', 'test-oom', 'test-avalanche', 'test-penetration']

for target in targets:
    # Find the block for the target
    pattern = re.compile(r'^' + target + r':\n((?:\t.*\n)+)', re.MULTILINE)
    match = pattern.search(content)
    if match:
        block = match.group(1)
        # Clean up the block
        lines = block.split('\n')
        script_lines = ['#!/bin/bash', 'AUTO=${AUTO:-0}']
        for line in lines:
            if not line.strip(): continue
            # Remove leading tab and @
            line = re.sub(r'^\t@?', '', line)
            # Replace $$ with $
            line = line.replace('$$', '$')
            # Replace $(AUTO) with $AUTO
            line = line.replace('$(AUTO)', '$AUTO')
            script_lines.append(line)
        
        script_path = f'scripts/demos/{target.replace("-", "_")}.sh'
        with open(script_path, 'w') as sf:
            sf.write('\n'.join(script_lines) + '\n')
        os.chmod(script_path, 0o755)
        print(f'Extracted {target} to {script_path}')

