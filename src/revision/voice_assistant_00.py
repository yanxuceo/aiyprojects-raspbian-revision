import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_plugins import (
    FileIOPlugin,
    MathPlugin,
    TextPlugin,
    TimePlugin,
)
from semantic_kernel.planning import SequentialPlanner
import os

import argparse
import locale
import logging

from cloudspeech_class import CloudSpeechClient
from button_class import Button 


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language


async def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    kernel = sk.Kernel()
  

    kernel.add_chat_service("gpt-3.5", 
                           OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo-0301", api_key=os.environ.get('OPENAI_API_KEY'), org_id=os.environ.get('OPENAI_ORG_ID'))
                        )
    kernel.import_plugin(MathPlugin(), "math")
    kernel.import_plugin(FileIOPlugin(), "fileIO")
    kernel.import_plugin(TimePlugin(), "time")
    kernel.import_plugin(TextPlugin(), "text")

    # create an instance of sequential planner.
    planner = SequentialPlanner(kernel)
   
    while True:
        if hints:
            logging.info('Say something, e.g. %s.' % ', '.join(hints))
        else:
            logging.info('Say something.')
        text = client.recognize(hint_phrases=hints)
        if text is None:
            logging.info('You said nothing.')
            continue

        logging.info('You said: "%s"' % text)
           
        # ask the sequential planner to identify a suitable function from the list of functions available.
        plan = await planner.create_plan(goal=text)

        # ask the sequential planner to execute the identified function.
        result = await plan.invoke()

        for step in plan._steps:
            print(step.description, ":", step._state.__dict__)

        print("Expected Answer:")
        print(result)
        """
        Output:
        SUNDAY
        """


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())