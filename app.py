from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=".env", override=True)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JUNG_PROMPT = """
You are a warm, insightful Jungian dream interpreter.

Write like a thoughtful human — not an academic paper.

Your tone should feel:

• natural  
• psychologically insightful  
• gently conversational  
• emotionally intelligent  
• easy to understand  

Avoid sounding clinical, robotic, or overly scholarly.

Explain symbols in a way that feels personal to the dreamer.

Keep interpretations around 1 paragraph.

After the interpretation, create a vivid symbolic image prompt.

FORMAT EXACTLY:

INTERPRETATION:
(text)

IMAGE_PROMPT:
(visual description only, no text in image)
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    image_url = None

    if request.method == "POST":
        dream = request.form.get("prompt", "").strip()

        if not dream:
            return render_template("index.html", result="Please type your dream first.", image_url=None)

        try:
            # 1) Jungian interpretation + image prompt
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {"role": "developer", "content": JUNG_PROMPT},
                    {"role": "user", "content": dream}
                ],
                temperature=0.7,
                max_output_tokens=450
            )

            output = resp.output_text or ""
            parts = output.split("IMAGE_PROMPT:")

            interpretation = parts[0].replace("INTERPRETATION:", "").strip()
            result = interpretation if interpretation else output.strip()

            image_prompt = parts[1].strip() if len(parts) > 1 else ""

            # 2) Generate image from the image prompt
            if image_prompt:
                img = client.images.generate(
                    model="gpt-image-1-mini",   # allowed by assignment
                    prompt=image_prompt,
                    size="1024x1024"
                )
                b64 = img.data[0].b64_json
                image_url = f"data:image/png;base64,{b64}"

        except Exception as e:
            result = f"Error: {str(e)}"
            image_url = None

    return render_template("index.html", result=result, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
