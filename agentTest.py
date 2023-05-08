import openai
import os

key = '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'

openai.api_key = key

available_actions = [
    'Perform a google search and get the results',
    'Book a flight with expedia',
    'send an email with Gmail',
    'book a restaurant with OpenTable'
]

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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    return response.choices[0].message["content"]

def clarifyingQuestions():
    # Get user inputs
    user_goal = input("What would you like me to do? ")
    background_context = input("Please provide any background context: ")

    # Set up the conversation for GPT-3.5 Turbo
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{user_goal}\nBackground context: {background_context}\n\nAs GPT-3.5, ask clarifying questions to better understand the goal and create an actionable plan:"}
    ]

    clarifying_questions_text = generate_action_plan(conversation)
    clarifying_questions = split_questions(clarifying_questions_text)

    print("\nGPT-3.5 generated the following clarifying questions:")

    # Collect user's answers
    user_answers = []
    for idx, question in enumerate(clarifying_questions):
        print(f"{idx + 1}. {question}")
        answer = input("Your answer: ")
        user_answers.append(answer)
        conversation.append({"role": "user", "content": answer})

    # Display the user's answers
    print("\nYou provided the following answers:")
    for idx, answer in enumerate(user_answers):
        print(f"{idx + 1}. {answer}")

    return conversation

def review_and_update_plan(conversation):
    actions_string = ', '.join(available_actions)
    action_plan_prompt = f"Based on the provided information, determine if you can accomplish the user's request on your own or if you need to perform some actions. If the latter, consider the following available actions: {actions_string}. Create an actionable plan for the user:"
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
    return action_items

def identify_external_functionality(action_items_list):
    functionality_list = []
    external_functionality_required = False
    for action_item in action_items_list:
        can_be_done_by_gpt = action_item in available_actions
        functionality_list.append({"action_item": action_item, "can_be_done_by_gpt": can_be_done_by_gpt})
        if not can_be_done_by_gpt:
            external_functionality_required = True
    return functionality_list, external_functionality_required

    


def recommend_relevant_actions(action_items_list, functionality_list, external_functionality_required):
    if external_functionality_required:
        recommended_actions = []
        for action_item in action_items_list:
            for available_action in available_actions:
                if available_action.lower() in action_item.lower():
                    recommended_actions.append(available_action)
        if recommended_actions:
            message = "Recommended actions to enable:"
            for idx, action in enumerate(recommended_actions):
                message += f"\n{idx + 1}. {action}"
            return message
    return ""

if __name__ == "__main__":
    conversation_history = clarifyingQuestions()
    final_plan = review_and_update_plan(conversation_history)
    print("\nFinal action plan:")
    print(final_plan)

    # Parse action items from the final plan and store them in a list
    action_items_list = parse_action_items(final_plan)

    # Print the action items list
    print("\nAction items list:")
    for idx, action_item in enumerate(action_items_list):
        print(f"{idx + 1}. {action_item}")

    # Identify external functionality required for each action item
    functionality_list, external_functionality_required = identify_external_functionality(action_items_list)
    
    # Check for relevant recommended actions and print the message
    recommended_actions_message = recommend_relevant_actions(action_items_list, functionality_list, external_functionality_required)
    if recommended_actions_message:
        print("\n" + recommended_actions_message)