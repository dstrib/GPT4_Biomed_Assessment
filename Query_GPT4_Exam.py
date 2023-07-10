#!/usr/bin/env python3.8
# Daniel Stribling  |  ORCID: 0000-0002-0649-9506
# University of Florida
# GPT4_Biomed_Assessment Project
# Changelog:
#   Version 0.1.0 - 2023-05-03 - Initial release
#   Version 0.1.1 - Add expert-answer list removal for answers
#                 - Add Expert_Short mode
#                 - Add Prompt resetting
#   Version 0.1.2 - Add loop over multiple inputs

"""
Script to query OpenAI GPT4 with examination questions and store the results.

This script is designed to query OpenAI GPT4 with assessment questions from higher
education courses and store the results.
This is being performed as part of a research project to evaluate the capabilities of OpenAI GPT4
to provide logically consistent and factually correct answers for questions in the biomedical
sciences.
"""

import os
import copy
import openai
import json
import datetime
from Settings_GPT4_Grad_Exam import PROMPT_TEMPLATE_SIMPLE, PROMPT_TEMPLATE_EXPERT, \
                                    BLANK_INSTRUCTIONS, TEXT_INSTRUCTIONS, \
                                    HANDWRITTEN_INSTRUCTIONS, \
                                    USER_INIT_STATEMENT, \
                                    INIT_STATEMENT_SIMPLE, INIT_STATEMENT_EXPERT, \
                                    LIST_REMOVE_REQUEST, SHORTEN_REQUEST

# Attempt to find the API key in a file located in: ../../GPT/API_KEY.txt, else ask for API_Key.
api_key_file = os.path.abspath(os.path.join('..', '..', 'GPT', 'API_KEY.txt'))
if os.path.isfile(api_key_file):
    with open(api_key_file, 'r') as api_key_file_obj:
        openai.api_key = api_key_file_obj.read().strip()
else:
    openai.api_key = input('\nEnter API Key:\n')

# Constants for the script.
SCRIPT_VERSION = 'Query_GPT4_Exam.py v0.1.2'
CHAT_URL = 'https://api.openai.com/v1/chat/completions'
MODEL = 'gpt-4'
MAX_CONTEXT_WINDOW = '8192'
CONFIRM_CONTINUE = False
PROMPT_TEMPLATES = {
    'Simple': (PROMPT_TEMPLATE_SIMPLE, INIT_STATEMENT_SIMPLE),
    'Expert': (PROMPT_TEMPLATE_EXPERT, INIT_STATEMENT_EXPERT),
    'Expert_Short': (PROMPT_TEMPLATE_EXPERT, INIT_STATEMENT_EXPERT),
}
START_AT_PROMPT = 0

IO_DIR = os.path.abspath('.')


# Add to the list of prompt componenents with a specified role and content.
def add_to_prompt(initial_prompt, role, content):
    """Add to the list of prompt componenents with a specified role and content."""
    ret_prompt = []
    for item in initial_prompt:
        ret_prompt.append(copy.deepcopy(item))
    ret_prompt.append({'role': role, 'content': content})
    return ret_prompt


# Create initial prompot by adding intial 3 components.
def prep_prompt(prompt_template,
                assistant_init_statement,
                user_init_statement=USER_INIT_STATEMENT,
                ):
    """Create initial prompot by adding intial 3 components."""
    question_prefixes = []
    question_prefixes = add_to_prompt(question_prefixes, 'system', prompt_template.lstrip())
    question_prefixes = add_to_prompt(
        question_prefixes,
        'user',
        user_init_statement
    )
    question_prefixes = add_to_prompt(
        question_prefixes,
        'assistant',
        assistant_init_statement
    )
    return question_prefixes


# Process the response from GPT4. Returns:
#   response, finish_reason, tokens_str, details, usage
def process_gpt_response(response_obj,
                         print_completion=True,
                         print_response=True,
                         print_tokens=True,
                         print_details=True,
                         ):
    """
    Process the response from GPT4.

    Returns: response, finish_reason, tokens_str, and details.
    """
    # Check for successful response.
    if 'choices' not in response_obj:
        return 'No response from GPT!', 'No_Response', None, None, None

    # Extract response and finish reason.
    response = response_obj['choices'][0]['message']['content'].strip()
    finish_reason = response_obj['choices'][0]['finish_reason']

    # Store details
    detail_keys = ['created', 'id', 'model', 'object']
    details = {'finish_reason': finish_reason}
    for key in detail_keys:
        details[key] = response_obj[key]

    # Store usage
    usage = {}
    for key in response_obj['usage']:
        usage[key] = response_obj['usage'][key]

    # Create tokens report string
    tokens_str = ''
    tokens_str += 'Prompt: ' + str(usage['prompt_tokens']) + '  '
    tokens_str += 'Response: ' + str(usage['completion_tokens']) + '  '
    tokens_str += 'Total: ' + str(usage['total_tokens']) + ' (of ' + MAX_CONTEXT_WINDOW + ')  '

    # If enabled, print the response, tokens, and/or details.
    if print_completion:
        print('API Query Complete...')
    if print_response:
        print('Response:')
        print(response)
    if print_tokens:
        print('Tokens: ' + tokens_str + '\n')
    if print_details:
        print('Details:')
        for key in detail_keys:
            print('   ', key.title() + ':',  details[key])
        print()

    return response, finish_reason, tokens_str, details, usage


# Query GPT4 with prepared prompt, process the response, and return details.
def query_gpt(prompt):
    """Query GPT4 with prepared prompt, process the response, and return details."""
    response_obj = openai.ChatCompletion.create(
        model=MODEL,
        messages=prompt,
        # temperature=float(temperature),
    )

    response, finish_reason, tokens, details, usage = process_gpt_response(
        response_obj,
        print_completion=True,
        print_response=False,
        print_tokens=True,
        print_details=True,
    )
    return response, finish_reason, tokens, details, usage


# Check if token usage is near maximum
def check_token_usage(tokens):
    """Check if token usage is near maximum."""
    if tokens > ((int(MAX_CONTEXT_WINDOW) * 9) / 10):
        input('Total tokens near max, continue?\n')


# Class to print and write output of the GPT4 query / response conversation to a file.
class Query_Reporter():
    """Class to print and write output of the GPT4 query / response conversation to a file."""

    def __init__(self, file_name, initial_dialog):
        """Hold place for module docstring."""
        self.file_name = file_name
        self.file_obj = open(self.file_name, 'w')
        self.initialize()
        for entry in initial_dialog:
            self.report(entry)

    def __call__(self, dialog, do_print=True):
        """Call the report method if class object is called."""
        self.report(dialog, do_print=do_print)

    def initialize(self):
        """Initialize the file with convseration details."""
        init_str = 'Conversation Details:\n'
        init_str += '    Script Version: ' + SCRIPT_VERSION + '\n'
        init_str += '    Performed: ' + str(datetime.datetime.now()) + '\n'
        init_str += '    Chat URL: ' + CHAT_URL + '\n'
        init_str += '    Model: ' + MODEL + '\n'
        init_str += '    Max Context Window: ' + MAX_CONTEXT_WINDOW + '\n'
        init_str += '\n'
        self.file_obj.write(init_str)

    def report(self, dialog, do_print=True):
        """Report a dialog element by writing to the file handle and printing to the screen."""
        header_bar = ' ' + ('-' * 5) + ' '
        write_str = header_bar + dialog['role'] + header_bar + '\n'
        write_str += dialog['content'].rstrip() + '\n\n'
        self.file_obj.write(write_str)
        self.file_obj.flush()
        if do_print:
            print(write_str)

    def add_details(self, details, usage):
        """Add details of the query to the report."""
        self.file_obj.write('Details:\n')
        for key in details:
            self.file_obj.write('    ' + key.title() + ': ' + str(details[key]) + '\n')
        self.file_obj.write('\n')
        self.file_obj.write('Usage:\n')
        for key in usage:
            self.file_obj.write('    ' + key.title() + ': ' + str(usage[key]) + '\n')
        self.file_obj.write('\n')
        self.file_obj.flush()

    def close(self):
        """Close the file handle."""
        self.file_obj.close()


# Execute Functionality
if __name__ == '__main__':
    # Select json file(s) containing data about the test to be examined.
    #   mapping keys in this file must include:
    #   course, field, exam_type, out_file_prefix, questions_file_name
    target_exam_file_names = [
        'Example_Course_settings.json',
    ]

    for target_exam_file_name in target_exam_file_names:
        # Create paths to relevant files and directories for the script.
        target_exam_file = os.path.abspath(os.path.join(IO_DIR, target_exam_file_name))

        # Report beginning of test:
        print('\nBeginning GPT4 test with file:', target_exam_file, '\n')

        # Load the exam parameters
        with open(target_exam_file, 'r') as target_exam_file_obj:
            exam_parameters = json.load(target_exam_file_obj)

        # Load the exam instructions based on specified exam type
        if exam_parameters['exam_type'] == 'handwritten':
            exam_instructions = HANDWRITTEN_INSTRUCTIONS
        elif exam_parameters['exam_type'] == 'text':
            exam_instructions = TEXT_INSTRUCTIONS
        else:
            exam_instructions = BLANK_INSTRUCTIONS

        # Test results for each of the prompt templates:
        for template_name, (use_prompt_template, use_init_statement) in PROMPT_TEMPLATES.items():
            # load and format the propmpt (where applicable)
            initial_prompt = prep_prompt(use_prompt_template, use_init_statement)
            initial_prompt[0]['content'] = initial_prompt[0]['content'].format(
                exam_parameters['course'], exam_parameters['field'], exam_instructions
            )

            # If reset_prompt_numbers, set variable to avoid overfilling context window
            if 'reset_prompt_numbers' in exam_parameters:
                reset_prompt_numbers = [int(i) for i in exam_parameters['reset_prompt_numbers']]
            else:
                reset_prompt_numbers = []

            # If expert mode, and enabled, propmpt to remove lists from answers where applicable.
            if 'Expert' in template_name and exam_parameters['expert_remove_lists']:
                modify_remove_lists = True
            else:
                modify_remove_lists = False

            # if expert-short mode, add a follow-on request to shorten the previous answer.
            if template_name == 'Expert_Short':
                shorten_all_answers = True
            else:
                shorten_all_answers = False

            # Load the exam questions
            full_questions_file_name = os.path.join(IO_DIR, exam_parameters['questions_file_name'])
            with open(full_questions_file_name, 'r') as questions_file_obj:
                exam_prompts = [(q.strip() + '\n') for q in questions_file_obj.read().split('-&-')]

            # Set up the output file
            out_file_name = exam_parameters['out_file_prefix'] + '_' + template_name + '.txt'
            full_out_file_name = os.path.join(IO_DIR, out_file_name)
            use_out_file_name = full_out_file_name

            # Query GPT4 with all questions
            last_prompt_set = copy.deepcopy(initial_prompt)
            query_reporter = Query_Reporter(use_out_file_name, last_prompt_set)

            for prompt_i, exam_prompt in enumerate(exam_prompts, start=1):
                # Report skipping or beginning prompt
                if prompt_i < START_AT_PROMPT:
                    print('Skipping prompt', prompt_i, '...')
                    continue
                else:
                    print('------ Mode:', template_name, 'Prompt:', prompt_i, '------')

                # If resetting prompt, close output file and open a new one.
                if prompt_i in reset_prompt_numbers:
                    query_reporter.close()
                    use_out_file_name = full_out_file_name.replace(
                        '.txt', ('_' + str(prompt_i) + '.txt')
                        )
                    last_prompt_set = copy.deepcopy(initial_prompt)
                    query_reporter = Query_Reporter(use_out_file_name, last_prompt_set)

                # Prepare next prompt
                query_reporter({'role': 'user', 'content': exam_prompt})
                next_prompt_set = add_to_prompt(last_prompt_set, 'user', exam_prompt)

                # Query GPT4 and process response
                response, finish_reason, tokens, details, usage = query_gpt(next_prompt_set)
                query_reporter({'role': 'assistant', 'content': response})
                query_reporter.add_details(details, usage)
                last_prompt_set = add_to_prompt(next_prompt_set, 'assistant', response)

                # Check for token useage nearing maximum
                check_token_usage(usage['total_tokens'])

                if modify_remove_lists and '1. ' in response:
                    next_prompt_set = add_to_prompt(last_prompt_set, 'user', LIST_REMOVE_REQUEST)
                    query_reporter({'role': 'user', 'content': LIST_REMOVE_REQUEST})

                    # Repeat query of GPT4 and process response
                    response, finish_reason, tokens, details, usage = query_gpt(next_prompt_set)
                    query_reporter({'role': 'assistant', 'content': response})
                    query_reporter.add_details(details, usage)
                    last_prompt_set = add_to_prompt(next_prompt_set, 'assistant', response)

                    # Check for token useage nearing maximum
                    check_token_usage(usage['total_tokens'])

                if shorten_all_answers:
                    next_prompt_set = add_to_prompt(last_prompt_set, 'user', SHORTEN_REQUEST)
                    query_reporter({'role': 'user', 'content': SHORTEN_REQUEST})

                    # Repeat query of GPT4 and process response
                    response, finish_reason, tokens, details, usage = query_gpt(next_prompt_set)
                    query_reporter({'role': 'assistant', 'content': response})
                    query_reporter.add_details(details, usage)
                    last_prompt_set = add_to_prompt(next_prompt_set, 'assistant', response)

                    # Check for token useage nearing maximum
                    check_token_usage(usage['total_tokens'])

                # manually require continue if enabled
                if CONFIRM_CONTINUE and exam_prompt != exam_prompts[-1]:
                    input('\nContinue?\n')

            # At completion of this prompt-style, close the output file
            query_reporter.close()

            # Report completion of this section:
            print('\nCompleted assessment with ' + template_name + ' prompt template.\n')

    print('\nDone.\n')
