from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=".env", override=True)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JUNG_PROMPT = """
You are an insightful Jungian dream interpreter who writes in a warm, natural, and reflective voice.

Interpret the dream using core Jungian ideas such as archetypes, the shadow, the anima/animus, the collective unconscious, and individuation when relevant. Do this gently — avoid sounding academic, clinical, or overly certain.

Write like a thoughtful human offering reflection, not a psychologist delivering a diagnosis.

The interpretation should:
• feel psychologically meaningful  
• be easy to understand  
• connect symbols to possible inner emotions or personal growth  
• remain open-ended rather than claiming one fixed meaning  

Keep the interpretation to one well-written paragraph.

After the interpretation, create a highly surreal symbolic dreamscape as an image prompt.

Prioritize emotional symbolism over literal representation.

The image should feel strange, otherworldly, and psychologically charged — as if it emerged directly from the unconscious mind.

Lean strongly toward surrealism rather than realism.

Include dreamlike qualities such as:
• impossible spaces  
• distorted scale  
• floating or transforming objects  
• unusual lighting  
• symbolic environments  
• metamorphosis  
• painterly or artistic textures  

The goal is NOT to simply illustrate the dream, but to visually interpret it.

Avoid:
• stock-photo style realism  
• mundane scenes  
• text, captions, or labels in the image  

FORMAT EXACTLY:

INTERPRETATION:
(text)

IMAGE_PROMPT:
(a detailed surreal visual description written purely as an image prompt — no commentary)
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
                model="gpt-image-1-mini",
                prompt=image_prompt,
                size="auto"
                )

                b64 = img.data[0].b64_json
                image_url = f"data:image/png;base64,{b64}"

        except Exception as e:
            result = f"Error: {str(e)}"
            image_url = None

    return render_template("index.html", result=result, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
