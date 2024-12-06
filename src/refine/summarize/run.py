import sys
import json
from string import Template
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

from openai import OpenAI

from mylib import Logger

def func(incoming, outgoing, args):
    client = OpenAI()

    while True:
        sample = incoming.get()
        config = json.loads(sample)
        Logger.info(' '.join(
            str(config.get(x)) for x in ('system', 'user', 'sequence'))
        )
        view = config['response']

        template = Template(args.user_prompt.read_text())
        content = template.substitute(passage=view['message'])

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

        outgoing.put(config)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--user-prompt', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args,
    )

    with Pool(args.workers, func, initargs):
        jobs = 0
        for i in sys.stdin:
            outgoing.put(i)
            jobs += 1

        for _ in range(jobs):
            result = incoming.get()
            print(json.dumps(result))
