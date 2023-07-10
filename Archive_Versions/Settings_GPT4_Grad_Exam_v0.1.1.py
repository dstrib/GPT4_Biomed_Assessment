#!/usr/bin/env python3.8
# Daniel Stribling  |  ORCID: 0000-0002-0649-9506
# University of Florida
# GPT4_Biomed_Assessment Project
# Changelog:
#   Version 0.1.0 - 2023-05-03 - Initial release
#   Version 0.1.1 - Add expert-answer list removal for answers
#                 - Add Expert_Short mode
#                 - Add Prompt resetting


"""Settings for testing the GPT-4 model on a graduate exam."""

import textwrap

PROMPT_TEMPLATE_SIMPLE = textwrap.dedent("""\
    Please answer the following questions.
    """)

# Prompt template for the GPT-4 graduate exam.
# The first {} is the name of the exam, the second {} is the name of the field,
# and the third {} is any details on exam format.
PROMPT_TEMPLATE_EXPERT = textwrap.dedent("""\
    I am going to give you questions from an examination in a graduate course in {}.
    Please act as an expert in the field of {}.
    Please answer each question as correctly as possible, using technical or advanced
    language as necessary to answer the question correctly.

    Details regarding the examination:{}

    Some questions may have multiple parts, denoted by letters after the question number.
    For example: 1A and 1B. When answering multiple part questions, refer to the answer of
    previous parts of the question as necessary to answer each question correctly.

    Fore each quesiton, respond with an answer as a narrative paragraph, without including
    a list in the answer.
    If the answer to a question contains multiple ideas, components, or steps, respond with
    narrative paragraphs connecting topics or ideas.
    If a question asks you how you would do something, respond with a narrative paragraph
    and do not separate the answer into a list of steps.

    Some questions will refer to a figure, chart, or graphic. For these questions, ask for a
    description of each panel of the graphic before answering the question, and then use the
    graphic to answer the question as needed. **Do Not** answer questions that refer to a
    figure, chart, or graphic without first asking for a description.

    Some questions will request you to draw a figure or diagram to assist in answering the
    question. This is signified by keywords: "draw" or "sketch" in the question.
    For these questions, after providing the text of your answer, provide a full
    page of extremely detailed drawing instructions to draw up to one graphic as appropriate
    to answer the question. For drawing instructions, first start with the text:
    "[Drawing Instructions]". Then, provide detailed instructions
    on each shape and line to be drawn, and their relative position to the other shapes
    and lines in the drawing. Then provide any captions to be drawn as well as indicating
    what shapes or lines should be captioned.

    Remember, answer all questions in narrative form, acting as an expert in the field.
    Answers should be extremely clear and extremely concise.

    Thank you!"""
)

# Instructions placeholder for no specific exam format.
BLANK_INSTRUCTIONS = """"""

# Instructions for text entry of answers.
TEXT_INSTRUCTIONS = textwrap.dedent("""\


    Answers will be entered as plaintext into the response portion of a document as a student
    in an exam setting, so do not include any markdown symbols.
    Your answers should be extremely concise and extremely clear so that they can fit into the
    answer textbox for the examination."""

)
# Instructions for a handwritten exam.
HANDWRITTEN_INSTRUCTIONS = textwrap.dedent("""\


    Answers will be handwritten on a sheet of paper like a student in a classroom.
    Your answers should be extremely concise and extremely clear so that they can be handwritten.
    A 1-page answer should be at max 14 lines.
    A 1/2-page answer should be at max 7 lines.
    A 1/4-page answer should be at max 4 lines.

    Emphasize the most important words or concepts in your answer using bolded text as appropriate.
    There should be at least four bolded words or concepts in each answer, or approximately one
    bolded word or concept per 2-3 lines of text."""
)

# Initialization Statements
USER_INIT_STATEMENT = "I am ready to provide you with questions to answer."
INIT_STATEMENT_SIMPLE = "Please provide the questions from the examination."
INIT_STATEMENT_EXPERT = textwrap.dedent("""\
    Please provide the questions from the graduate-level examination. I will provide extremely
    clear and concise answers to each question, acting as an expert in the field. My answers
    will be provided as narrative paragraphs and will not not include a list unless the question
    specifically asks for a list. If the question mentions a figure, chart, or graphic, I will
    ask for a description of the figure, chart, or graphic before answering the question. If the
    question mentions providing a drawing or sketch, I will provide detailed instructions
    on how to draw a graphic illustrating my answer after providing the text of my answer.
    Please provide the first question.""")

# Request for removal of list from response
LIST_REMOVE_REQUEST = textwrap.dedent("""\
    The last answer you provided included a list. Please restate the answer as paragraphs of
    clear, concise narrative text without any numeric lists.""")

# Request to shorten response
SHORTEN_REQUEST = textwrap.dedent("""\
    Please shorten the last answer to approximately sixty-five percent of the original length.
    The shortened answer should be correct, clear, and concise without any numeric lists.""")