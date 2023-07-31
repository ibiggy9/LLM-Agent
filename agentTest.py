import openai
import os
import re

key = 'GPT-KEY'

openai.api_key = key

def split_questions(text):
    questions = []
    current_question = ""
    for char in text:
        current_question += char
        if char == "?":
            questions.append(current_question.strip())
            current_question = ""
    return questions

def generate_action_plan(conversation):
    conversation.append({"role": "user", "content": "As GPT-4, you can perform any action in a browser and any amount of text manipulation, but you cannot do anything else. Create a plan that reflects these capabilities."})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation,
        max_tokens=150,
        temperature=0.6,
        n=1
    )

    return response.choices[0].message["content"]



def clarifyingQuestions():
    # Get user inputs
    user_goal = input("What would you like me to do? ")
    background_context = input("Please provide any background context: ")

    # Set up the conversation for GPT-4 Turbo
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{user_goal}\nBackground context: {background_context}"}
    ]

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


def review_and_update_plan(conversation):
    action_plan_prompt = ("Based on the provided information, determine if you can accomplish the user's request "
                      "by performing actions in a browser or by text manipulation using your capabilities as GPT-4. "
                      "You cannot perform any other actions outside of these constraints. "
                      "Create an actionable plan for the user:")

    conversation.append({"role": "user", "content": action_plan_prompt})
    action_plan = generate_action_plan(conversation)

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


def parse_action_items(final_plan):
    action_items = final_plan.strip().split('\n')
    numbered_list_pattern = re.compile(r"^\d+\.")
    filtered_action_items = [item for item in action_items if numbered_list_pattern.match(item.strip())]
    return filtered_action_items


    


def build_plan_manifest(action_items_list):
    plan_manifest = []
    for action_item in action_items_list:
        plan_manifest.append({
            "item": action_item,
            "planItemDescription": action_item,
            "status": "Incomplete",
        })

    return plan_manifest




def determine_task_type(plan_manifest):
    for task in plan_manifest:
        description = task["planItemDescription"]

        # Query GPT-4 Turbo to classify the task
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Classify the following task as 'GPT', 'browser session', or 'neither': {description}"}
        ]
        task_type_response = generate_action_plan(conversation).strip().lower()

        if "gpt" in task_type_response:
            task_type = "gpt"
        elif "browser session" in task_type_response:
            task_type = "web"
        else:
            task_type = "neither"

        task["taskType"] = task_type

    return plan_manifest


if __name__ == "__main__":
    conversation_history = clarifyingQuestions()
    final_plan = review_and_update_plan(conversation_history)
   

    # Parse action items from the final plan and store them in a list
    action_items_list = parse_action_items(final_plan)

    # Build the plan manifest
    plan_manifest = build_plan_manifest(action_items_list)

   

    # Print the plan manifest
    print("\nPlan manifest:")
    for idx, item in enumerate(plan_manifest):
        print(f"item{idx + 1}: {item}")
