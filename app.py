import json
import os
import random
import string
import hashlib
import datetime
import time
import csv
from pathlib import Path

def get_low_accuracy_questions(exams_dir, threshold):
    """
    Get a list of questions with a correct answer rate below the threshold.
    :param exams_dir: Directory containing completed tests.
    :param threshold: Correct answer rate threshold (0 - 100).
    :return: List of questions.
    """
    done_tests = get_done_tests(exams_dir)
    question_stats = {}

    # Calculate the correct answer rate for each question
    for test in done_tests:
        exam_data = load_exam(test)
        for result in exam_data["questions"]:
            question_id = result["question"]["id"]
            correct_answer_ids = {
                ans["id"] for ans in result["question"]["answers"] if ans["correct"]
            }
            is_correct = set(result["user_answer"]) == correct_answer_ids

            if question_id not in question_stats:
                question_stats[question_id] = {
                    "question": result["question"],
                    "correct_count": 0,
                    "attempts": 0,
                }
            question_stats[question_id]["attempts"] += 1
            if is_correct:
                question_stats[question_id]["correct_count"] += 1

    # Filter questions with a correct answer rate below the threshold
    low_accuracy_questions = []
    for stats in question_stats.values():
        attempts = stats["attempts"]
        correct_count = stats["correct_count"]
        accuracy = (correct_count / attempts) * 100 if attempts > 0 else 0
        if accuracy < threshold:
            low_accuracy_questions.append(stats["question"])

    return low_accuracy_questions


def save_statistics_to_csv():
    exams_dir = "exams"
    output_file = "statistics.csv"

    done_tests = get_done_tests(exams_dir, order="oldest")
    print(done_tests)
    question_statistics = {}

    # Read information from completed tests
    for _, test in enumerate(done_tests):
        exam_data = load_exam(test)

        for result in exam_data["questions"]:
            question_id = result["question"]["id"]
            question_desc = result["question"]["description"]
            answers = result["question"]["answers"]

            # Create answer string A, B, C, D
            answer_str = "\n".join(
                f"{chr(65 + i)}. {ans['value']}" for i, ans in enumerate(answers)
            )

            correct_answers = [
                f"\n{chr(65 + i)}. {ans['value']}" for i, ans in enumerate(answers) if ans['correct']
            ]
            correct_answers_str = "Correct answers: " + ", ".join(correct_answers)
            full_question_desc = (
                f"{question_desc}\n{answer_str}\n\n{correct_answers_str}"
            )
            # If the question is not in statistics, initialize a new line
            if question_id not in question_statistics:
                question_statistics[question_id] = {
                    "question": full_question_desc,
                    "results": [],
                }

            # Check your answer and record the result
            user_answer = result["user_answer"]
            correct_answer_ids = {ans["id"] for ans in answers if ans["correct"]}
            passed = set(user_answer) == correct_answer_ids
            status = "Correct" if passed else "Incorrect"
            question_statistics[question_id]["results"].append(status)

    # Create headers for the CSV file
    headers = ["Question"]
    max_attempts = max(len(stat["results"]) for stat in question_statistics.values())
    headers.extend([f"Attempt {i+1}" for i in range(max_attempts)])

    # Save statistics data to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for question_id, stat in question_statistics.items():
            row = [stat["question"]]
            row.extend(stat["results"] + [""] * (max_attempts - len(stat["results"])))
            writer.writerow(row)

    print(f"\nStatistics exported to file: {output_file}")
    input("\nPress Enter to return to the main menu.")


def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def md5_hash(text):
    """Generate MD5 hash from content."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_questions(data_file):
    """Load questions from JSON file and calculate hash ID."""
    with open(data_file, "r", encoding="utf-8") as f:
        questions = json.load(f)
        for question in questions:
            question["id"] = md5_hash(question["description"])
            for answer in question["answers"]:
                answer["id"] = md5_hash(answer["value"])
        return questions


def get_done_tests(exams_dir, order="newest"):
    """Get a list of completed tests, can be sorted by newest or oldest."""
    if os.path.exists(exams_dir):
        files = [
            os.path.join(exams_dir, filename)
            for filename in os.listdir(exams_dir)
            if filename.endswith(".json")
        ]

        # Sort by time (newest or oldest)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=(order == "newest"))
        return files
    return []


def save_exam(exam_dir, exam_data):
    """Save test results to a file."""
    os.makedirs(exam_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exam_{timestamp}.json"
    filepath = os.path.join(exam_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(exam_data, f, ensure_ascii=False, indent=4)
    print(f"\nResults saved at: {filepath}")


def ask_question(
    question, index, total_questions, time_limit, start_time, prev_answer=None
):
    """Display the question and get the answer from the user, also display the previously selected answer if any."""
    while True:
        clear_screen()
        print("=" * 40)
        print(f"Question {index + 1}/{total_questions}")
        print("\n")
        print(question["description"])
        print("\n")
        print("*" * 40)
        print("\n")
        choices = question["answers"]
        for i, choice in enumerate(choices):
            print(f"{string.ascii_uppercase[i]}. {choice['value']}\n")

        # Display the previously selected answer if any
        if prev_answer:
            selected_choices = [
                string.ascii_uppercase[i]
                for i, choice in enumerate(choices)
                if choice["id"] in prev_answer
            ]
            print(f"\nYour previous answer: {', '.join(selected_choices)}")

        # Calculate elapsed time and remaining time
        elapsed_time = time.time() - start_time
        remaining_time = time_limit * 60 - elapsed_time  # Remaining time in seconds

        if remaining_time <= 0:
            print("\nTime's up!")
            return "TIME_UP"

        remaining_minutes = int(remaining_time // 60)
        remaining_seconds = int(remaining_time % 60)
        print("*" * 40)
        print(f"\nRemaining time: {remaining_minutes:02}:{remaining_seconds:02}")

        # Get answer from the user
        answer = (
            input(
                "\nSelect answer (e.g., AB, 'back' to go back, 'next' to skip, or 'r' to reset time): "
            )
            .strip()
            .upper()
        )

        if answer == "BACK":
            return "BACK"
        if answer == "NEXT":
            if not prev_answer:  # If no previous answer
                print(
                    "\nYou haven't selected any answer. Please select at least one answer before continuing."
                )
                input("\nPress Enter to continue.")
                continue
            return "NEXT"
        if answer == "R":
            continue  # Reset time and display the question again
        if all(ch in string.ascii_uppercase[: len(choices)] for ch in answer):
            return [choices[string.ascii_uppercase.index(ch)]["id"] for ch in answer]
        print("Invalid answer, please try again.")
        input("\nPress Enter to continue.")


def shuffle_answers(questions):
    """Shuffle the order of answers for each question."""
    for question in questions:
        random.shuffle(question["answers"])


def load_exam(exam_path):
    """Load saved test."""
    with open(exam_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main_menu():
    """Display the main menu."""
    clear_screen()
    print("Welcome to the testing system!")
    print("1. Take a new test")
    print("2. Retake an old test")
    print("3. Test result statistics")
    print("4. Take a test from questions with low correct rate")
    print("5. Exit")
    choice = input("\nYour choice: ").strip()
    return choice


def get_questions_from_done_tests(exams_dir):
    """Get all questions that have been in old tests."""
    done_tests = get_done_tests(exams_dir)
    seen_questions = set()  # Use set to easily check for duplicates
    for test in done_tests:
        exam_data = load_exam(test)
        for result in exam_data["questions"]:
            seen_questions.add(result["question"]["id"])
    return seen_questions


def main():
    folder_path = Path("exams")
    folder_path.mkdir(parents=True, exist_ok=True)
    # File and directory paths
    data_file = "data.json"
    exams_dir = "exams"

    while True:
        choice = main_menu()
        if choice == "1":
            seen_questions = get_questions_from_done_tests(exams_dir)
            # Take a new test
            questions = load_questions(data_file)

            # Ask the user if they want to skip questions already done in previous tests
            skip_old_questions = (
                input("Skip questions already done in previous tests? (y/n): ")
                .strip()
                .lower()
            )

            # Take a new test
            questions = load_questions(data_file)

            if skip_old_questions == "y":
                # Remove questions that have already appeared in old tests
                questions = [
                    q
                    for q in questions
                    if md5_hash(q["description"]) not in seen_questions
                ]

            if not questions:
                print("No new questions to take.")
                input("\nPress Enter to return to the main menu.")
                continue

            shuffle_answers(questions)

            num_questions = int(input(f"Number of questions (max {len(questions)}): "))
            num_questions = min(num_questions, len(questions))
            time_limit = int(input("Test time (minutes): "))
            pass_condition = input(
                "Pass condition (e.g., 70% or 7 questions): "
            ).strip()

            # Randomly select questions
            selected_questions = random.sample(questions, num_questions)
            results = [{"question": q, "user_answer": []} for q in selected_questions]

            # Record start time
            start_time = time.time()

            # Take the test
            index = 0
            while index < len(results):
                user_answer = ask_question(
                    results[index]["question"],
                    index,
                    len(results),
                    time_limit,
                    start_time,
                    prev_answer=results[index]["user_answer"],
                )

                if user_answer == "BACK":
                    if index > 0:
                        index -= 1
                elif user_answer == "TIME_UP":
                    break
                elif user_answer == "NEXT":
                    index += 1
                else:
                    results[index][
                        "user_answer"
                    ] = user_answer  # Only update if the user enters an answer
                    index += 1

            # Calculate results
            correct_count = sum(
                set(result["user_answer"])
                == {
                    ans["id"] for ans in result["question"]["answers"] if ans["correct"]
                }
                for result in results
            )
            total_questions = len(results)
            percentage = (correct_count / total_questions) * 100
            passed = (
                percentage >= float(pass_condition.strip("%"))
                if "%" in pass_condition
                else correct_count >= int(pass_condition)
            )

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)

            # Display results
            clear_screen()
            print("\nTest results:")
            print(f"Correct answers: {correct_count}/{total_questions}")
            print(f"Score: {percentage:.2f}%")
            print(f"Status: {'PASS' if passed else 'FAIL'}")
            print(f"Time taken: {elapsed_minutes:02}:{elapsed_seconds:02}")

            # Save results
            exam_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "questions": results,
                "score": correct_count,
                "total": total_questions,
                "percentage": percentage,
                "passed": passed,
                "pass_condition": pass_condition,
                "elapsed_time": f"{elapsed_minutes:02}:{elapsed_seconds:02}",
                "time_limit": time_limit,  # Save test time
            }
            save_exam(exams_dir, exam_data)

            input("\nPress Enter to return to the main menu.")

        elif choice == "2":
            # Retake an old test
            done_tests = get_done_tests(exams_dir)
            if not done_tests:
                print("No saved tests found.")
                input("\nPress Enter to return to the menu.")
                continue

            while True:
                clear_screen()
                print("\nList of saved tests:")
                for i, test in enumerate(done_tests):
                    print(f"{i + 1}. {os.path.basename(test)}")

                test_choice = (
                    input(
                        "\nSelect a test (number) or enter 'back' to return to the menu: "
                    )
                    .strip()
                    .lower()
                )
                if test_choice == "back":
                    break

                if test_choice.isdigit() and 1 <= int(test_choice) <= len(done_tests):
                    test_choice = int(test_choice) - 1
                    exam_data = load_exam(done_tests[test_choice])

                    # Display saved test information
                    clear_screen()
                    print("\nSaved test information:")
                    print(f"Date and time: {exam_data['timestamp']}")
                    print(f"Correct answers: {exam_data['score']}/{exam_data['total']}")
                    print(f"Score: {exam_data['percentage']:.2f}%")
                    print(f"Status: {'PASS' if exam_data['passed'] else 'FAIL'}")
                    print(f"Pass condition: {exam_data['pass_condition']}")
                    print(f"Time taken: {exam_data['elapsed_time']}")
                    print(f"Test time: {exam_data['time_limit']} minutes")

                    # Option to retake the test
                    action = (
                        input(
                            "\nEnter 'start' to retake the test or 'back' to return to the list: "
                        )
                        .strip()
                        .lower()
                    )
                    if action == "back":
                        continue
                    elif action == "start":
                        # Proceed to retake the test
                        questions = [q["question"] for q in exam_data["questions"]]
                        shuffle_answers(questions)

                        time_limit = exam_data.get("time_limit")
                        if time_limit is None:
                            time_limit = int(input("Test time (minutes): "))

                        # Retake the test
                        results = [
                            {"question": q, "user_answer": []} for q in questions
                        ]
                        start_time = time.time()  # Record start time
                        index = 0

                        while index < len(results):
                            user_answer = ask_question(
                                results[index]["question"],
                                index,
                                len(results),
                                time_limit,
                                start_time,
                                prev_answer=results[index]["user_answer"],
                            )

                            if user_answer == "BACK":
                                if index > 0:
                                    index -= 1
                            elif user_answer == "TIME_UP":
                                break
                            else:
                                results[index]["user_answer"] = user_answer
                                index += 1

                        # Calculate results
                        correct_count = sum(
                            set(result["user_answer"])
                            == {
                                ans["id"]
                                for ans in result["question"]["answers"]
                                if ans["correct"]
                            }
                            for result in results
                        )
                        total_questions = len(results)
                        percentage = (correct_count / total_questions) * 100
                        pass_condition = exam_data["pass_condition"]
                        passed = (
                            percentage >= float(pass_condition.strip("%"))
                            if "%" in pass_condition
                            else correct_count >= int(pass_condition)
                        )

                        # Calculate elapsed time
                        elapsed_time = time.time() - start_time
                        elapsed_minutes = int(elapsed_time // 60)
                        elapsed_seconds = int(elapsed_time % 60)

                        # Display results
                        clear_screen()
                        print("\nTest results:")
                        print(f"Correct answers: {correct_count}/{total_questions}")
                        print(f"Score: {percentage:.2f}%")
                        print(f"Status: {'PASS' if passed else 'FAIL'}")
                        print(f"Time taken: {elapsed_minutes:02}:{elapsed_seconds:02}")

                        # Save retaken test results
                        exam_data = {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "questions": results,
                            "score": correct_count,
                            "total": total_questions,
                            "percentage": percentage,
                            "passed": passed,
                            "pass_condition": pass_condition,  # Save pass condition to exam_data
                            "elapsed_time": f"{elapsed_minutes:02}:{elapsed_seconds:02}",  # Save time taken
                            "time_limit": time_limit,  # Save test time
                        }
                        save_exam(exams_dir, exam_data)
                        input("\nPress Enter to return to the main menu.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
                        input("\nPress Enter to continue.")
                else:
                    print("Invalid choice. Please try again.")
                    input("\nPress Enter to continue.")

        elif choice == "3":
            save_statistics_to_csv()

        elif choice == "4":
            threshold = float(input("Enter the maximum correct answer rate (0-100): "))
            low_accuracy_questions = get_low_accuracy_questions(exams_dir, threshold)

            if not low_accuracy_questions:
                print(
                    "No questions found with a correct rate below the entered threshold."
                )
                input("\nPress Enter to return to the main menu.")
                continue

            shuffle_answers(low_accuracy_questions)

            num_questions = int(
                input(f"Number of questions (max {len(low_accuracy_questions)}): ")
            )
            num_questions = min(num_questions, len(low_accuracy_questions))
            time_limit = int(input("Test time (minutes): "))
            pass_condition = input(
                "Pass condition (e.g., 70% or 7 questions): "
            ).strip()

            selected_questions = random.sample(low_accuracy_questions, num_questions)
            results = [{"question": q, "user_answer": []} for q in selected_questions]

            start_time = time.time()

            index = 0
            while index < len(results):
                user_answer = ask_question(
                    results[index]["question"],
                    index,
                    len(results),
                    time_limit,
                    start_time,
                    prev_answer=results[index]["user_answer"],
                )

                if user_answer == "BACK":
                    if index > 0:
                        index -= 1
                elif user_answer == "TIME_UP":
                    break
                else:
                    results[index]["user_answer"] = user_answer
                    index += 1

            correct_count = sum(
                set(result["user_answer"])
                == {
                    ans["id"] for ans in result["question"]["answers"] if ans["correct"]
                }
                for result in results
            )
            total_questions = len(results)
            percentage = (correct_count / total_questions) * 100
            passed = (
                percentage >= float(pass_condition.strip("%"))
                if "%" in pass_condition
                else correct_count >= int(pass_condition)
            )

            elapsed_time = time.time() - start_time
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)

            clear_screen()
            print("\nTest results:")
            print(f"Correct answers: {correct_count}/{total_questions}")
            print(f"Score: {percentage:.2f}%")
            print(f"Status: {'PASS' if passed else 'FAIL'}")
            print(f"Time taken: {elapsed_minutes:02}:{elapsed_seconds:02}")

            exam_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "questions": results,
                "score": correct_count,
                "total": total_questions,
                "percentage": percentage,
                "passed": passed,
                "pass_condition": pass_condition,
                "elapsed_time": f"{elapsed_minutes:02}:{elapsed_seconds:02}",
                "time_limit": time_limit,
            }
            save_exam(exams_dir, exam_data)
            input("\nPress Enter to return to the main menu.")

        elif choice == "5":
            print("Exiting the program. See you again!")
            break

        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to return to the menu.")


main()
