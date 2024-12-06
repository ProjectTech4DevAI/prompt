import sys
import json
from string import Template
from pathlib import Path
from argparse import ArgumentParser

from openai import OpenAI

from mylib import Logger

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--user-prompt', type=Path)
    args = arguments.parse_args()

    for line in sys.stdin:
        config = json.loads(line)
        Logger.info(' '.join(
            str(config.get(x)) for x in ('system', 'user', 'sequence'))
        )
        view = config['response']

        template = Template(args.user_prompt.read_text())
        content = template.substitute(passage=view['message'])

        client = OpenAI()
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                # {
                # 'role': 'system',
                # 'content': 'You are an expert summarizer',
                # },
                {
                    'role': 'user',
                    'content': content,
                },
            ],
        )
        view['summary'] = response.choices[0].message.content

        print(json.dumps(config, indent=3))
