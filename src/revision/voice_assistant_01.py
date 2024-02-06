import asyncio
from cloudspeech_class import CloudSpeechClient
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_plugins import FileIOPlugin, MathPlugin, TextPlugin, TimePlugin
from semantic_kernel.planning import SequentialPlanner
import os
import logging


import argparse
import locale


# Your existing functions (get_hints, locale_language) here
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


async def process_text_with_voice_assistant(text):
    kernel = sk.Kernel()
    kernel.add_chat_service("gpt-3.5",
                            OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo-0301",
                                                 api_key=os.environ.get('OPENAI_API_KEY'),
                                                 org_id=os.environ.get('OPENAI_ORG_ID')))
    kernel.import_plugin(MathPlugin(), "math")
    #kernel.import_plugin(FileIOPlugin(), "fileIO")
    kernel.import_plugin(TimePlugin(), "time")
    #kernel.import_plugin(TextPlugin(), "text")

    planner = SequentialPlanner(kernel)
    plan = await planner.create_plan(goal=text)
    result = await plan.invoke()

    for step in plan._steps:
        print(step.description, ":", step._state.__dict__)

    print("Assistant's Answer:")
    print(result)


async def main_async():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    client = CloudSpeechClient()
    hints = get_hints(args.language)

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
        
        await process_text_with_voice_assistant(text)

def main():
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
