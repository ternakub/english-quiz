import os
import json
import uuid
import html
import random

from flask import Flask, request
from openai import OpenAI


app = Flask(__name__)

client = OpenAI(
    base_url="https://gateway.9arm.co/v1",
    api_key=os.getenv("API_9ARM_KEY")
)

quizzes = {}
LETTERS = ["A", "B", "C", "D"]

vocabulary = {
    "add": {"meaning": "กล่าวเพิ่มเติม", "structures": ["that + S + V"]},
    "announce": {"meaning": "ประกาศ", "structures": ["that + S + V"]},
    "complain": {
        "meaning": "บ่น / ร้องเรียน",
        "structures": ["that + S + V", "complain about + V.ing"]
    },
    "explain": {"meaning": "อธิบาย", "structures": ["that + S + V"]},
    "predict": {"meaning": "ทำนาย / คาดการณ์", "structures": ["that + S + V"]},
    "refuse": {"meaning": "ปฏิเสธ", "structures": ["to / not to + V.inf"]},
    "offer": {"meaning": "เสนอ", "structures": ["to / not to + V.inf"]},
    "promise": {"meaning": "สัญญา", "structures": ["to / not to + V.inf"]},
    "agree": {"meaning": "เห็นด้วย / ตกลง", "structures": ["to / not to + V.inf"]},
    "advise": {
        "meaning": "แนะนำ",
        "structures": ["object + to + V.inf", "that + should + S + V"]
    },
    "ask": {"meaning": "ขอ / ถาม", "structures": ["object + to + V.inf"]},
    "encourage": {
        "meaning": "สนับสนุน / ให้กำลังใจ",
        "structures": ["object + to + V.inf"]
    },
    "invite": {"meaning": "เชิญ", "structures": ["object + to + V.inf"]},
    "order": {"meaning": "สั่ง", "structures": ["object + to + V.inf"]},
    "persuade": {"meaning": "ชักชวน / โน้มน้าว", "structures": ["object + to + V.inf"]},
    "remind": {"meaning": "เตือนให้จำ", "structures": ["object + to + V.inf"]},
    "tell": {"meaning": "บอก", "structures": ["object + to + V.inf"]},
    "warn": {
        "meaning": "เตือน",
        "structures": ["object + to + V.inf", "warn someone against + V.ing"]
    },
    "deny": {"meaning": "ปฏิเสธว่าไม่ได้ทำ", "structures": ["V.ing"]},
    "admit": {"meaning": "ยอมรับ", "structures": ["V.ing"]},
    "recommend": {
        "meaning": "แนะนำ",
        "structures": ["V.ing", "that + should + S + V"]
    },
    "suggest": {
        "meaning": "เสนอแนะ",
        "structures": ["V.ing", "that + should + S + V"]
    },
    "apologise": {"meaning": "ขอโทษ", "structures": ["apologise for + V.ing"]},
    "blame": {"meaning": "ตำหนิ / โทษ", "structures": ["blame someone for + V.ing"]},
    "congratulate": {
        "meaning": "แสดงความยินดี",
        "structures": ["congratulate someone on + V.ing"]
    },
    "thank": {"meaning": "ขอบคุณ", "structures": ["thank someone for + V.ing"]},
    "request": {"meaning": "ขอร้อง / ร้องขอ", "structures": ["that + should + S + V"]}
}


QUIZ_INSTRUCTIONS = """

Return valid JSON only.

Use this exact structure:
{
  "questions": [
    {
      "question": "question text",
      "explanation": "brief explanation"
    }
  ]
}

Rules:
- Create exactly 5 questions.
- Follow question_plan in order.
- Each question must be a fill-in-the-blank question with exactly one blank.
- The blank must test the target reporting verb.
- Use the meaning and structures from vocabulary_data.
- Construct a natural English sentence so the exact target word fits grammatically.
- Use different contexts and sentence patterns across the 5 questions.
- Do not reveal the target word in the question.
- The top-level key must be "questions".
- Every question must contain only:
  "question" and "explanation".
- The explanation must be brief, clear, and educational.
- Do not use markdown.
- Do not add text outside the JSON.
"""

def page(content):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>English Quiz</title>

    <style>
        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }}

        .container {{
            width: 100%;
            max-width: 820px;
            margin: 0 auto;
            padding: 24px;
        }}

        .card, .question-card {{
            background: white;
            border-radius: 18px;
            padding: 28px;
            margin-bottom: 22px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
        }}

        .question-card {{
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 3px 14px rgba(0, 0, 0, 0.06);
        }}

        h1 {{ margin-top: 0; font-size: 32px; line-height: 1.2; }}
        h2 {{ font-size: 24px; }}
        h3 {{ font-size: 20px; line-height: 1.5; }}

        .subtitle {{ color: #6b7280; margin-bottom: 26px; }}
        .field {{ margin-bottom: 20px; }}

        label.field-label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        select, input[type="number"] {{
            width: 100%;
            padding: 14px;
            font-size: 17px;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            background: white;
        }}

        select:focus, input[type="number"]:focus {{
            outline: 2px solid #93c5fd;
            border-color: #2563eb;
        }}

        button, .button {{
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

        button:hover, .button:hover {{ background: #1d4ed8; }}
        .button.secondary {{ background: #4b5563; }}
        .button.secondary:hover {{ background: #374151; }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }}

        .info-box {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 14px 16px;
        }}

        .info-title {{ color: #6b7280; font-size: 14px; margin-bottom: 4px; }}
        .info-value {{ font-size: 17px; font-weight: 600; }}

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

        .summary-score, .result {{
            text-align: center;
            font-size: 40px;
            font-weight: 800;
        }}

        .summary-score {{ margin: 24px 0 10px; }}
        .summary-percent {{
            text-align: center;
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 14px;
        }}

        .result {{ margin-bottom: 30px; }}
        .pass {{ color: #16803b; }}
        .fail {{ color: #c62828; }}
        .review-wrong {{ border-left: 5px solid #dc2626; }}
        .your-answer {{ color: #b91c1c; }}
        .correct-answer {{ color: #15803d; }}

        .button-group {{
            display: grid;
            gap: 12px;
            margin-top: 20px;
        }}

        .loading-text {{ animation: blink 1.2s infinite; }}

        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.25; }}
        }}

        @media (max-width: 600px) {{
            .container {{ padding: 12px; }}
            .card {{ padding: 20px; border-radius: 14px; }}
            h1 {{ font-size: 26px; }}
            h2 {{ font-size: 21px; }}
            h3 {{ font-size: 18px; }}
            .info-grid {{ grid-template-columns: 1fr; }}
            .question-card {{ padding: 18px; }}
            .choice {{ padding: 14px; font-size: 16px; }}
            button, .button {{ font-size: 17px; padding: 14px; }}
            .summary-score, .result {{ font-size: 34px; }}
            .summary-percent {{ font-size: 30px; }}
        }}

        @media (min-width: 601px) and (max-width: 1024px) {{
            .container {{ max-width: 760px; padding: 22px; }}
            .choice {{ padding: 16px; }}
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


def message_page(title, message="", button_text="Return Home", href="/"):
    message_html = f"<p>{html.escape(message)}</p>" if message else ""
    return page(f"""
    <div class="card">
        <h1>{html.escape(title)}</h1>
        {message_html}
        <a class="button" href="{href}">{html.escape(button_text)}</a>
    </div>
    """)


def info_grid(quiz, full=True):
    fields = [
        ("Class", quiz["student_class"]),
        ("Student Number", quiz["student_number"])
    ]

    if full:
        fields += [
            ("Topic", quiz["topic"]),
            ("Difficulty", quiz["difficulty"])
        ]

    boxes = "".join(
        f"""
        <div class="info-box">
            <div class="info-title">{title}</div>
            <div class="info-value">{html.escape(str(value))}</div>
        </div>
        """
        for title, value in fields
    )

    return f'<div class="info-grid">{boxes}</div>'


def build_question_plan():
    selected_words = random.sample(list(vocabulary), 20)
    target_words = selected_words[:5]
    distractor_words = selected_words[5:]

    question_plan = []

    for i, target in enumerate(target_words):
        choices = [target] + distractor_words[i * 3:(i + 1) * 3]
        random.shuffle(choices)
        question_plan.append({"target": target, "choices": choices})

    return selected_words, question_plan


def generate_questions(topic, difficulty):
    selected_words, question_plan = build_question_plan()

    quiz_request = {
        "task": "Generate an English multiple-choice quiz",
        "topic": topic,
        "difficulty": difficulty,
        "question_plan": question_plan,
        "vocabulary_data": {
            plan["target"]: vocabulary[plan["target"]]
            for plan in question_plan
        },
        "instructions": QUIZ_INSTRUCTIONS,
        "language": "English"
    }

    response = client.chat.completions.create(
        model="qwen3.8-27b-fp8",
        messages=[{
            "role": "user",
            "content": json.dumps(quiz_request, ensure_ascii=False)
        }]
    )

    quiz_text = response.choices[0].message.content
    start = quiz_text.find("{")

    if start == -1:
        raise ValueError("AI response did not contain JSON.")

    quiz_data, _ = json.JSONDecoder().raw_decode(quiz_text[start:])
    questions = quiz_data.get("questions", [])

    if len(questions) != 5:
        raise ValueError("AI did not return exactly 5 questions.")

    # Python remains the source of truth for choices and answers.
    for question, plan in zip(questions, question_plan):
        question["choices"] = plan["choices"]
        question["answer"] = plan["target"]
        question["explanation"] = question.get("explanation", "")

    return questions


def render_quiz_form(questions, quiz_id):
    cards = []

    for number, question in enumerate(questions, start=1):
        choices_html = "".join(
            f"""
            <label class="choice">
                <input type="radio" name="q{number}" value="{LETTERS[index]}">
                <span>
                    <b>{LETTERS[index]}.</b>
                    {html.escape(choice)}
                </span>
            </label>
            """
            for index, choice in enumerate(question["choices"])
        )

        cards.append(f"""
        <div class="question-card">
            <div class="question-title">
                {number}. {html.escape(question["question"])}
            </div>
            {choices_html}
        </div>
        """)

    return f"""
    <form method="POST" action="/submit">
        <input type="hidden" name="quiz_id" value="{quiz_id}">
        {''.join(cards)}
        <div class="card">
            <button type="submit">Submit Quiz</button>
        </div>
    </form>
    """


def render_summary(quiz, quiz_id):
    result_class = "pass" if quiz["result"] == "Pass" else "fail"

    return page(f"""
    <div class="card">
        <h1>Quiz Summary</h1>

        {info_grid(quiz)}

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
            <a class="button" href="/review/{quiz_id}">
                Review Incorrect Answers
            </a>

            <a class="button secondary" href="/">
                Start New Quiz
            </a>
        </div>
    </div>
    """)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        student_class = request.form["student_class"]
        student_number = request.form["student_number"]
        topic = request.form["topic"]
        difficulty = request.form["difficulty"]

        try:
            questions = generate_questions(topic, difficulty)
        except Exception as error:
            print("QUIZ GENERATION ERROR:", error)
            return message_page(
                "Could not generate quiz",
                "Please try again in a moment."
            ), 500

        quiz_id = str(uuid.uuid4())

        quizzes[quiz_id] = {
            "student_class": student_class,
            "student_number": student_number,
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "submitted": False
        }

        quiz = quizzes[quiz_id]

        return page(f"""
        <div class="card">
            <h1>English Quiz</h1>
            {info_grid(quiz)}
        </div>

        {render_quiz_form(questions, quiz_id)}
        """)

    class_options = "".join(
        f"<option>M.4.{number}</option>"
        for number in [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    )

    return page(f"""
    <div class="card">
        <h1>English Quiz</h1>

        <p class="subtitle">
            Choose your class, topic and difficulty to start the quiz.
        </p>

        <form method="POST" onsubmit="showLoading()">
            <div class="field">
                <label class="field-label">Class</label>
                <select name="student_class">
                    {class_options}
                </select>
            </div>

            <div class="field">
                <label class="field-label">Student Number</label>
                <input
                    type="number"
                    name="student_number"
                    min="1"
                    max="41"
                    required
                >
            </div>

            <div class="field">
                <label class="field-label">Topic</label>
                <select name="topic">
                    <option>Reporting Verbs</option>
                    <option>Reported Statements</option>
                    <option>Reported Questions</option>
                </select>
            </div>

            <div class="field">
                <label class="field-label">Difficulty</label>
                <select name="difficulty">
                    <option>Easy</option>
                    <option>Medium</option>
                    <option>Hard</option>
                </select>
            </div>

            <button type="submit">Start Quiz</button>

            <div
                id="loading"
                style="display:none; text-align:center; margin-top:24px;"
            >
                <h2 class="loading-text">Generating your quiz...</h2>
            </div>
        </form>
    </div>
    """)


@app.route("/submit", methods=["POST"])
def submit():
    quiz_id = request.form["quiz_id"]
    quiz = quizzes.get(quiz_id)

    if not quiz:
        return message_page("Quiz not found")

    if quiz["submitted"]:
        return message_page(
            "This quiz has already been submitted.",
            "You cannot change your answers or submit this quiz again.",
            "Back to Quiz Summary",
            f"/summary/{quiz_id}"
        )

    score = 0
    review = []

    for number, question in enumerate(quiz["questions"], start=1):
        user_answer = request.form.get(f"q{number}", "")
        choices = question["choices"]
        correct_answer = question["answer"]
        explanation = question.get("explanation", "")

        correct_letter = next(
            (
                LETTERS[index]
                for index, choice in enumerate(choices)
                if choice == correct_answer
            ),
            ""
        )

        is_correct = user_answer == correct_letter
        score += int(is_correct)

        review.append({
            "number": number,
            "question": question["question"],
            "choices": choices,
            "user_answer": user_answer,
            "correct_letter": correct_letter,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "is_correct": is_correct
        })

    percentage = score / len(quiz["questions"]) * 100
    result = "Pass" if percentage >= 60 else "Fail"

    quiz.update({
        "submitted": True,
        "score": score,
        "percentage": percentage,
        "result": result,
        "review": review
    })

    return render_summary(quiz, quiz_id)


@app.route("/summary/<quiz_id>")
def quiz_summary(quiz_id):
    quiz = quizzes.get(quiz_id)

    if not quiz:
        return message_page("Quiz not found")

    if not quiz.get("submitted"):
        return message_page("Quiz has not been submitted yet.")

    return render_summary(quiz, quiz_id)


@app.route("/review/<quiz_id>")
def review_quiz(quiz_id):
    quiz = quizzes.get(quiz_id)

    if not quiz:
        return message_page("Quiz not found")

    if not quiz.get("submitted"):
        return message_page("Quiz has not been submitted yet.")

    review_cards = []

    for item in quiz["review"]:
        if item["is_correct"]:
            continue

        if item["user_answer"]:
            user_index = LETTERS.index(item["user_answer"])
            user_text = (
                f'{item["user_answer"]}. '
                f'{html.escape(item["choices"][user_index])}'
            )
        else:
            user_text = "No answer"

        correct_text = (
            f'{item["correct_letter"]}. '
            f'{html.escape(item["correct_answer"])}'
        )

        review_cards.append(f"""
        <div class="question-card review-wrong">
            <div class="question-title">
                {item["number"]}. {html.escape(item["question"])}
            </div>

            <p class="your-answer">
                <b>Your answer:</b> {user_text}
            </p>

            <p class="correct-answer">
                <b>Correct answer:</b> {correct_text}
            </p>

            <p>
                <b>Explanation:</b>
                {html.escape(item["explanation"])}
            </p>
        </div>
        """)

    if review_cards:
        review_html = "".join(review_cards)
    else:
        review_html = """
        <div class="card">
            <h2 class="pass">
                Excellent! You answered every question correctly.
            </h2>
        </div>
        """

    return page(f"""
    <div class="card">
        <h1>Incorrect Answer Review</h1>
        {info_grid(quiz, full=False)}
    </div>

    {review_html}

    <div class="card">
        <a class="button secondary" href="/summary/{quiz_id}">
            Back to Quiz Summary
        </a>
    </div>
    """)


if __name__ == "__main__":
    app.run(debug=True)
