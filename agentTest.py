# Import necessary libraries
import openai
import os
import re

# Define OpenAI API key
key = 'GPT-4-KEY'

# Set OpenAI API key
openai.api_key = key

# Define function to split text into individual questions
def split_questions(text):
    questions = []
    current_question = ""
    for char in text:
        current_question += char
        # When a question mark is found, a question has ended
        if char == "?":
            questions.append(current_question.strip())
            current_question = ""
    return questions

# Define function to generate action plan
def generate_action_plan(conversation):
    # Add an additional instruction to the conversation
    conversation.append({"role": "user", "content": "As GPT-4, you can perform any action in a browser and any amount of text manipulation, but you cannot do anything else. Create a plan that reflects these capabilities."})
    # Call OpenAI API to generate a completion with the conversation history
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation,
        max_tokens=150,
        temperature=0.6,
        n=1
    )

    # Return the content of the generated response
    return response.choices[0].message["content"]

# Define function to keep asking clarifying questions until sufficient information has been gathered
def clarifyingQuestions():
    # Get user inputs
    user_goal = input("What would you like me to do? ")
    background_context = input("Please provide any background context: ")

    # Set up the initial conversation for GPT-4 Turbo
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{user_goal}\nBackground context: {background_context}"}
    ]

    # Keep asking questions until sufficient information has been gathered
    while True:
        conversation.append({"role": "user", "content": "As GPT-4, assume you can perform any action in a browser as well as any text manipulation. "
                                                        "Ask a clarifying question to better understand the goal and create an actionable plan:"})
        question_text = generate_action_plan(conversation)
        question_text = question_text.strip()

        # Ask the generated question
        print(f"\nGPT-4 generated the following clarifying question:")
        print(f"{question_text}")
        answer = input("Your answer: ")
        conversation.append({"role": "user", "content": answer})

        # Check if there's enough information to create an action plan
        conversation.append({"role": "user", "content": "Do you have enough information to create an action plan now?"})
        response = generate_action_plan(conversation)
        response = response.strip().lower()

        if "yes" in response:
            break

    return conversation

# Define function to review and update the action plan until the user approves
def review_and_update_plan(conversation):
    action_plan_prompt = ("Based on the provided information, determine if you can accomplish the user's request "
                      "by performing actions in a browser or by text manipulation using your capabilities as GPT-4. "
                      "You cannot perform any other actions outside of these constraints. "
                      "Create an actionable plan for the user:")

    # Append the prompt to the conversation and generate the initial action plan
    conversation.append({"role": "user", "content": action_plan_prompt})
    action_plan = generate_action_plan(conversation)

    # Keep updating the plan until the user approves
    while True:
        print("\nAction plan:")
        print(action_plan)
        user_feedback = input("Do you approve of this plan? (yes/no): ")

        if user_feedback.lower() == "yes":
            break
        else:
            suggested_changes = input("Please suggest changes to the plan: ")
            conversation.append({"role": "user", "content": suggested_changes})
            action_plan = generate_action_plan(conversation)

    return action_plan

# Define function to parse the final plan into a list of action items
def parse_action_items(final_plan):
    action_items = final_plan.strip().split('\n')
    numbered_list_pattern = re.compile(r"^\d+\.")
    # Filter the list of action items to include only the items that start with a number (i.e., are part of the enumerated list)
    filtered_action_items = [item for item in action_items if numbered_list_pattern.match(item.strip())]
    return filtered_action_items

# Define function to build the plan manifest
def build_plan_manifest(action_items_list):
    plan_manifest = []
    for action_item in action_items_list:
        plan_manifest.append({
            "item": action_item,
            "planItemDescription": action_item,
            "status": "Incomplete",
        })

    return plan_manifest

# Define function to determine the type of each task in the plan manifest
def determine_task_type(plan_manifest):
    for task in plan_manifest:
        description = task["planItemDescription"]

        # Query GPT-4 Turbo to classify the task
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Classify the following task as 'GPT', 'browser session', or 'neither': {description}"}
        ]
        task_type_response = generate_action_plan(conversation).strip().lower()

        # Determine the task type based on the response
        if "gpt" in task_type_response:
            task_type = "gpt"
        elif "browser session" in task_type_response:
            task_type = "web"
        else:
            task_type = "neither"

        task["taskType"] = task_type

    return plan_manifest

# Main function
if __name__ == "__main__":
    # Gather necessary information by asking clarifying questions
    conversation_history = clarifyingQuestions()
    # Review and update the action plan until it's approved
    final_plan = review_and_update_plan(conversation_history)

    # Parse action items from the final plan and store them in a list
    action_items_list = parse_action_items(final_plan)

    # Build the plan manifest
    plan_manifest = build_plan_manifest(action_items_list)

    # Print the plan manifest
    print("\nPlan manifest:")
    for idx, item in enumerate(plan_manifest):
        print(f"item{idx + 1}: {item}")
