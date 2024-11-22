# Terminal Quiz Application

## Overview

This Terminal Quiz Application is a Python-based tool designed to facilitate interactive quizzes directly within your terminal. It allows users to take quizzes, review past tests, analyze test results, and focus on questions with a low correct rate. The application is highly customizable, enabling users to set various parameters such as the number of questions, time limits, and pass criteria for each quiz.

## Features

1. **Take a New Test**: Start a new quiz with customizable settings such as the number of questions, time limit, and pass criteria.
2. **Retake an Old Test**: Review and retake previously taken quizzes.
3. **Test Result Statistics**: Analyze your performance with detailed statistics on past quizzes.
4. **Take a Test from Questions with Low Correct Rate**: Focus on improving your knowledge by taking quizzes consisting of questions with a low correct rate.

## Installation

To run this application, you need to have Python 3 installed on your system. Follow these steps to get started:

1. Clone the repository:

   ```bash
   git clone https://github.com/onmeyy/terminal-quiz.git
   ```

2. Navigate to the project directory:

   ```bash
   cd terminal-quiz
   ```

## Usage

Run the application by executing the following command in your terminal:

```bash
python app.py
```

## Adding Questions

Questions are stored in the `data.json` file. Each question follows the format below:

```json
{
  "description": "Google Cloud Platform resources are managed hierarchically using organization, folders, and projects. When Cloud Identity and Access Management (IAM) policies exist at these different levels, what is the effective policy at a particular node of the hierarchy?",
  "answers": [
    {
      "value": "The effective policy is determined only by the policy set at the node",
      "correct": false
    },
    {
      "value": "The effective policy is the policy set at the node and restricted by the policies of its ancestors",
      "correct": false
    },
    {
      "value": "The effective policy is the union of the policy set at the node and policies inherited from its ancestors",
      "correct": true
    },
    {
      "value": "The effective policy is the intersection of the policy set at the node and policies inherited from its ancestors",
      "correct": false
    }
  ]
}
```

The `data.json` file contains an array of such questions:

```json
[
  {
    "description": "Google Cloud Platform resources are managed hierarchically using organization, folders, and projects. When Cloud Identity and Access Management (IAM) policies exist at these different levels, what is the effective policy at a particular node of the hierarchy?",
    "answers": [
      {
        "value": "The effective policy is determined only by the policy set at the node",
        "correct": false
      },
      {
        "value": "The effective policy is the policy set at the node and restricted by the policies of its ancestors",
        "correct": false
      },
      {
        "value": "The effective policy is the union of the policy set at the node and policies inherited from its ancestors",
        "correct": true
      },
      {
        "value": "The effective policy is the intersection of the policy set at the node and policies inherited from its ancestors",
        "correct": false
      }
    ]
  }
]
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## License

This project is licensed under the MIT License
