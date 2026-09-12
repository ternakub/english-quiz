import os
import json
import uuid
import html

from flask import Flask, request
from openai import OpenAI


app = Flask(__name__)

client = OpenAI(
    base_url="https://gateway.9arm.co/v1",
    api_key=os.getenv("API_9ARM_KEY")
)

quizzes = {}


# =========================================================
# PAGE TEMPLATE
# =========================================================

def page(content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>English Quiz</title>

        <style>

    .loading-text {{
        animation: blink 1.2s infinite;
    }}

    @keyframes blink {{
        0%, 100% {{
            opacity: 1;
        }}

        50% {{
            opacity: 0.25;
        }}
    }}
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;

                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    Arial,
                    sans-serif;

                background: #f4f6f8;
                color: #1f2937;
            }}

            .container {{
                width: 100%;
                max-width: 820px;
                margin: 0 auto;
                padding: 24px;
            }}

            .card {{
                background: white;
                border-radius: 18px;
                padding: 28px;
                margin-bottom: 22px;

                box-shadow:
                    0 6px 24px rgba(0, 0, 0, 0.08);
            }}

            h1 {{
                margin-top: 0;
                font-size: 32px;
                line-height: 1.2;
            }}

            h2 {{
                font-size: 24px;
            }}

            h3 {{
                font-size: 20px;
                line-height: 1.5;
            }}

            .subtitle {{
                color: #6b7280;
                margin-bottom: 26px;
            }}

            .field {{
                margin-bottom: 20px;
            }}

            label.field-label {{
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
            }}

            select,
            input[type="number"] {{
                width: 100%;
                padding: 14px;

                font-size: 17px;

                border: 1px solid #d1d5db;
                border-radius: 12px;

                background: white;
            }}

            select:focus,
            input[type="number"]:focus {{
                outline: 2px solid #93c5fd;
                border-color: #2563eb;
            }}

            button,
            .button {{
                display: inline-block;

                width: 100%;

                padding: 15px 20px;

                border: none;
                border-radius: 12px;

                background: #2563eb;
                color: white;

                font-size: 18px;
                font-weight: 600;

                cursor: pointer;

                text-align: center;
                text-decoration: none;
            }}

            button:hover,
            .button:hover {{
                background: #1d4ed8;
            }}

            .button.secondary {{
                background: #4b5563;
            }}

            .button.secondary:hover {{
                background: #374151;
            }}

            .info-grid {{
                display: grid;

                grid-template-columns:
                    repeat(2, minmax(0, 1fr));

                gap: 12px;

                margin-bottom: 24px;
            }}

            .info-box {{
                background: #f8fafc;

                border-radius: 12px;

                padding: 14px 16px;
            }}

            .info-title {{
                color: #6b7280;
                font-size: 14px;
                margin-bottom: 4px;
            }}

            .info-value {{
                font-size: 17px;
                font-weight: 600;
            }}

            .question-card {{
                background: white;

                border-radius: 16px;

                padding: 22px;

                margin-bottom: 18px;

                box-shadow:
                    0 3px 14px rgba(0, 0, 0, 0.06);
            }}

            .question-title {{
                font-size: 19px;
                font-weight: 600;

                line-height: 1.5;

                margin-bottom: 18px;
            }}

            .choice {{
                display: flex;
                align-items: flex-start;

                width: 100%;

                padding: 14px 16px;
                margin-bottom: 10px;

                border: 1px solid #dbe1e8;
                border-radius: 12px;

                cursor: pointer;

                font-size: 17px;
                line-height: 1.4;

                transition: 0.15s;
            }}

            .choice:hover {{
                background: #eff6ff;
                border-color: #93c5fd;
            }}

            .choice input {{
                margin-top: 4px;
                margin-right: 12px;

                transform: scale(1.25);
            }}

            .summary-score {{
                text-align: center;

                font-size: 40px;
                font-weight: 800;

                margin: 24px 0 10px;
            }}

            /* เปอร์เซ็นต์ใหญ่ขึ้น */
            .summary-percent {{
                text-align: center;

                font-size: 36px;
                font-weight: 800;

                margin-bottom: 14px;
            }}

            /* Pass / Fail ใหญ่ขึ้น */
            .result {{
                text-align: center;

                font-size: 40px;
                font-weight: 800;

                margin-bottom: 30px;
            }}

            /* ผ่าน = เขียว */
            .pass {{
                color: #16803b;
            }}

            /* ไม่ผ่าน = แดง */
            .fail {{
                color: #c62828;
            }}

            .review-wrong {{
                border-left: 5px solid #dc2626;
            }}

            .your-answer {{
                color: #b91c1c;
            }}

            .correct-answer {{
                color: #15803d;
            }}

            .button-group {{
                display: grid;
                gap: 12px;
                margin-top: 20px;
            }}

            .divider {{
                height: 1px;
                background: #e5e7eb;
                margin: 24px 0;
            }}


            /* PHONE */

            @media (max-width: 600px) {{

                .container {{
                    padding: 12px;
                }}

                .card {{
                    padding: 20px;
                    border-radius: 14px;
                }}

                h1 {{
                    font-size: 26px;
                }}

                h2 {{
                    font-size: 21px;
                }}

                h3 {{
                    font-size: 18px;
                }}

                .info-grid {{
                    grid-template-columns: 1fr;
                }}

                .question-card {{
                    padding: 18px;
                }}

                .choice {{
                    padding: 14px;
                    font-size: 16px;
                }}

                button,
                .button {{
                    font-size: 17px;
                    padding: 14px;
                }}

                .summary-score {{
                    font-size: 34px;
                }}

                .summary-percent {{
                    font-size: 30px;
                }}

                .result {{
                    font-size: 34px;
                }}
            }}


            /* iPad / Tablet */

            @media
            (min-width: 601px)
            and
            (max-width: 1024px) {{

                .container {{
                    max-width: 760px;
                    padding: 22px;
                }}

                .choice {{
                    padding: 16px;
                }}
            }}

        </style>

    </head>

    <body>

        <div class="container">

            {content}

        </div>
        <script>
            function showLoading() {{
               document.getElementById("loading").style.display = "block";
            }}
        </script>
    </body>

    </html>
    """


# =========================================================
# HOME / SETUP
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        student_class = request.form["student_class"]
        student_number = request.form["student_number"]
        topic = request.form["topic"]
        difficulty = request.form["difficulty"]

        quiz_request = {

            "task":
                "Generate an English multiple-choice quiz",

            "topic":
                topic,

            "difficulty":
                difficulty,

            "number_of_questions":
                5,

            "choices_per_question":
                4,

            "instructions":
            """
Return valid JSON only.

Use EXACTLY this structure:

{
  "questions": [
    {
      "question": "question text",
      "choices": [
        "choice 1",
        "choice 2",
        "choice 3",
        "choice 4"
      ],
      "answer": "correct choice text"
            "explanation": "brief explanation of why the correct answer is correct"
    }
  ]
}

Rules:

- The top-level key must be "questions".
- Do not add a "quiz" key.
- Every question must also include the key "explanation".
- The explanation must be brief, clear, and educational.
- Every question must use the keys
  "question", "choices", "answer", and "explanation".
- Choices must contain plain text only.
- Do not include A., B., C., or D.
  inside choices.
- Do not use markdown code blocks.
- Do not add explanations outside the JSON.
""",

            "language":
                "English"
        }


        response = client.chat.completions.create(

            model="qwen3.8-27b-fp8",

            messages=[
                {
                    "role": "user",
                    "content": json.dumps(
                        quiz_request,
                        ensure_ascii=False
                    )
                }
            ]
        )


        quiz_text = response.choices[0].message.content

        start = quiz_text.find("{")

        quiz_text = quiz_text[start:]

        quiz_data, end = (
            json.JSONDecoder().raw_decode(quiz_text)
        )

        questions = quiz_data["questions"]

        quiz_id = str(uuid.uuid4())

        quizzes[quiz_id] = {

            "student_class":
                student_class,

            "student_number":
                student_number,

            "topic":
                topic,

            "difficulty":
                difficulty,

            "questions":
                questions,

            "submitted":
                False
        }


        quiz_html = ""

        letters = ["A", "B", "C", "D"]


        for number, question in enumerate(
            questions,
            start=1
        ):

            question_text = html.escape(
                question["question"]
            )

            choices_html = ""

            for index, choice in enumerate(
                question["choices"]
            ):

                letter = letters[index]

                choice_text = html.escape(choice)

                choices_html += f"""
                <label class="choice">

                    <input
                        type="radio"
                        name="q{number}"
                        value="{letter}"
                    >

                    <span>
                        <b>{letter}.</b>
                        {choice_text}
                    </span>

                </label>
                """


            quiz_html += f"""

            <div class="question-card">

                <div class="question-title">
                    {number}. {question_text}
                </div>

                {choices_html}

            </div>

            """


        return page(f"""

        <div class="card">

            <h1>English Quiz</h1>

            <div class="info-grid">

                <div class="info-box">
                    <div class="info-title">
                        Class
                    </div>
                    <div class="info-value">
                        {html.escape(student_class)}
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-title">
                        Student Number
                    </div>
                    <div class="info-value">
                        {html.escape(student_number)}
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-title">
                        Topic
                    </div>
                    <div class="info-value">
                        {html.escape(topic)}
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-title">
                        Difficulty
                    </div>
                    <div class="info-value">
                        {html.escape(difficulty)}
                    </div>
                </div>

            </div>

        </div>


        <form method="POST" action="/submit">

            <input
                type="hidden"
                name="quiz_id"
                value="{quiz_id}"
            >

            {quiz_html}

            <div class="card">

                <button type="submit">
                    Submit Quiz
                </button>

            </div>

        </form>

        """)


    return page("""

    <div class="card">

        <h1>English Quiz</h1>

        <p class="subtitle">
            Choose your class, topic and difficulty
            to start the quiz.
        </p>

        <form method="POST" onsubmit="showLoading()">

            <div class="field">

                <label class="field-label">
                    Class
                </label>

                <select name="student_class">

                    <option>M.4.2</option>
                    <option>M.4.5</option>
                    <option>M.4.6</option>
                    <option>M.4.7</option>
                    <option>M.4.8</option>
                    <option>M.4.9</option>
                    <option>M.4.10</option>
                    <option>M.4.11</option>
                    <option>M.4.12</option>
                    <option>M.4.13</option>
                    <option>M.4.14</option>

                </select>

            </div>


            <div class="field">

                <label class="field-label">
                    Student Number
                </label>

                <input
                    type="number"
                    name="student_number"
                    min="1"
                    max="41"
                    required
                >

            </div>


            <div class="field">

                <label class="field-label">
                    Topic
                </label>

                <select name="topic">

                    <option>
                        Reporting Verbs
                    </option>

                    <option>
                        Reported Statements
                    </option>

                    <option>
                        Reported Questions
                    </option>

                </select>

            </div>


            <div class="field">

                <label class="field-label">
                    Difficulty
                </label>

                <select name="difficulty">

                    <option>
                        Easy
                    </option>

                    <option>
                        Medium
                    </option>

                    <option>
                        Hard
                    </option>

                </select>

            </div>


            <button type="submit">
                Start Quiz
            </button>
            <div id="loading" style="display:none; text-align:center; margin-top:24px;">
                <h2 class="loading-text">
                        Generating your quiz...
                </h2>
            </div>

        </form>

    </div>

    """)


# =========================================================
# SUBMIT
# =========================================================

@app.route("/submit", methods=["POST"])
def submit():

    quiz_id = request.form["quiz_id"]

    if quiz_id not in quizzes:

        return page("""
        <div class="card">
            <h1>Quiz not found</h1>

            <a class="button" href="/">
                Return Home
            </a>
        </div>
        """)


    quiz = quizzes[quiz_id]


    if quiz["submitted"]:

        return page(f"""

        <div class="card">

            <h1>
                This quiz has already been submitted.
            </h1>

            <p>
                You cannot change your answers
                or submit this quiz again.
            </p>

            <a
                class="button"
                href="/summary/{quiz_id}"
            >
                Back to Quiz Summary
            </a>

        </div>

        """)


    questions = quiz["questions"]

    letters = ["A", "B", "C", "D"]

    score = 0

    review = []


    for number, question in enumerate(
        questions,
        start=1
    ):

        user_answer = request.form.get(
            f"q{number}",
            ""
        )

        choices = question["choices"]

        correct_answer = question["answer"]

        explanation = question.get(
            "explanation",
            ""
        )

        correct_letter = ""


        for index, choice in enumerate(choices):

            if choice == correct_answer:

                correct_letter = letters[index]

                break


        is_correct = (
            user_answer == correct_letter
        )


        if is_correct:
            score += 1


        review.append({

            "number":
                number,

            "question":
                question["question"],

            "choices":
                choices,

            "user_answer":
                user_answer,

            "correct_letter":
                correct_letter,

            "correct_answer":
                correct_answer,

            "explanation":
                explanation,

            "is_correct":
                is_correct
        })


    percentage = (
        score / len(questions)
    ) * 100


    if percentage >= 60:

        result = "Pass"

        result_class = "pass"

    else:

        result = "Fail"

        result_class = "fail"


    quiz["submitted"] = True
    quiz["score"] = score
    quiz["percentage"] = percentage
    quiz["result"] = result
    quiz["review"] = review


    return page(f"""

    <div class="card">

        <h1>Quiz Summary</h1>

        <div class="info-grid">

            <div class="info-box">
                <div class="info-title">Class</div>
                <div class="info-value">
                    {html.escape(quiz["student_class"])}
                </div>
            </div>

            <div class="info-box">
                <div class="info-title">Student Number</div>
                <div class="info-value">
                    {html.escape(quiz["student_number"])}
                </div>
            </div>

            <div class="info-box">
                <div class="info-title">Topic</div>
                <div class="info-value">
                    {html.escape(quiz["topic"])}
                </div>
            </div>

            <div class="info-box">
                <div class="info-title">Difficulty</div>
                <div class="info-value">
                    {html.escape(quiz["difficulty"])}
                </div>
            </div>

        </div>


        <div class="summary-score">

            {score}/{len(questions)}

        </div>


        <div class="summary-percent {result_class}">

            {percentage:.1f}%

        </div>


        <div class="result {result_class}">

            {result}

        </div>

<div class="button-group">

    <a
        class="button"
        href="/review/{quiz_id}"
    >
        Review Incorrect Answers
    </a>

    <a
        class="button secondary"
        href="/"
    >
        Start New Quiz
    </a>

</div>

    </div>

    """)


# =========================================================
# SUMMARY
# =========================================================

@app.route("/summary/<quiz_id>")
def quiz_summary(quiz_id):

    if quiz_id not in quizzes:

        return page("""
        <div class="card">

            <h1>Quiz not found</h1>

            <a class="button" href="/">
                Return Home
            </a>

        </div>
        """)


    quiz = quizzes[quiz_id]


    if not quiz.get("submitted"):

        return page("""
        <div class="card">
            <h1>
                Quiz has not been submitted yet.
            </h1>
        </div>
        """)


    if quiz["result"] == "Pass":

        result_class = "pass"

    else:

        result_class = "fail"


    return page(f"""

    <div class="card">

        <h1>Quiz Summary</h1>


        <div class="info-grid">

            <div class="info-box">

                <div class="info-title">
                    Class
                </div>

                <div class="info-value">
                    {html.escape(quiz["student_class"])}
                </div>

            </div>


            <div class="info-box">

                <div class="info-title">
                    Student Number
                </div>

                <div class="info-value">
                    {html.escape(quiz["student_number"])}
                </div>

            </div>


            <div class="info-box">

                <div class="info-title">
                    Topic
                </div>

                <div class="info-value">
                    {html.escape(quiz["topic"])}
                </div>

            </div>


            <div class="info-box">

                <div class="info-title">
                    Difficulty
                </div>

                <div class="info-value">
                    {html.escape(quiz["difficulty"])}
                </div>

            </div>

        </div>


        <div class="summary-score">

            {quiz["score"]}/{len(quiz["questions"])}

        </div>


        <div class="summary-percent {result_class}">

            {quiz["percentage"]:.1f}%

        </div>


        <div class="result {result_class}">

            {quiz["result"]}

        </div>


<div class="button-group">

    <a
        class="button"
        href="/review/{quiz_id}"
    >
        Review Incorrect Answers
    </a>

    <a
        class="button secondary"
        href="/"
    >
        Start New Quiz
    </a>

</div>

    </div>

    """)


# =========================================================
# REVIEW WRONG ANSWERS
# =========================================================

@app.route("/review/<quiz_id>")
def review_quiz(quiz_id):

    if quiz_id not in quizzes:

        return page("""
        <div class="card">

            <h1>Quiz not found</h1>

            <a class="button" href="/">
                Return Home
            </a>

        </div>
        """)


    quiz = quizzes[quiz_id]


    if not quiz.get("submitted"):

        return page("""
        <div class="card">

            <h1>
                Quiz has not been submitted yet.
            </h1>

        </div>
        """)


    review_html = ""

    letters = ["A", "B", "C", "D"]


    for item in quiz["review"]:

        if item["is_correct"]:
            continue


        if item["user_answer"] == "":

            user_text = "No answer"

        else:

            user_index = letters.index(
                item["user_answer"]
            )

            user_choice = (
                item["choices"][user_index]
            )

            user_text = (
                item["user_answer"]
                + ". "
                + html.escape(user_choice)
            )


        correct_text = (

            item["correct_letter"]
            + ". "
            + html.escape(
                item["correct_answer"]
            )
        )


        review_html += f"""

        <div class="
            question-card
            review-wrong
        ">

            <div class="question-title">

                {item["number"]}.
                {html.escape(item["question"])}

            </div>


            <p class="your-answer">

                <b>Your answer:</b>

                {user_text}

            </p>


            <p class="correct-answer">

                <b>Correct answer:</b>

                {correct_text}

            </p>

            <p
                                <b>Explanation:</b>

                {html.escape(item["explanation"])}

            </p>

        </div>

        """


    if review_html == "":

        review_html = """

        <div class="card">

            <h2 class="pass">

                Excellent!
                You answered every question correctly.

            </h2>

        </div>

        """


    return page(f"""

    <div class="card">

        <h1>
            Incorrect Answer Review
        </h1>

        <div class="info-grid">

            <div class="info-box">

                <div class="info-title">
                    Class
                </div>

                <div class="info-value">
                    {html.escape(quiz["student_class"])}
                </div>

            </div>


            <div class="info-box">

                <div class="info-title">
                    Student Number
                </div>

                <div class="info-value">
                    {html.escape(quiz["student_number"])}
                </div>

            </div>

        </div>

    </div>


    {review_html}


    <div class="card">

        <a
            class="button secondary"
            href="/summary/{quiz_id}"
        >
            Back to Quiz Summary
        </a>

    </div>

    """)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)