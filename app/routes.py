from flask import render_template, request, redirect, url_for, send_file
from app import app  # Import the app instance
import groq
import PyPDF2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Debug: Print the API key to verify it's being read correctly
#print("Groq API Key:", app.config['GROQ_API_KEY'])

client = groq.Client(api_key='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')

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def truncate_text(text, max_tokens=5000):
    """Truncate text to a maximum number of tokens."""
    words = text.split()
    truncated_text = " ".join(words[:max_tokens])
    return truncated_text

def generate_pdf(text, filename):
    """Generate a PDF file from the given text."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(72, 750, "Generated Question Paper")
    pdf.drawString(72, 730, "----------------------------------------")
    y = 700
    for line in text.split("\n"):
        pdf.drawString(72, y, line)
        y -= 12
        if y < 50:  # Add a new page if the content exceeds the page height
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_paper', methods=['GET', 'POST'])
def generate_paper():
    if request.method == 'POST':
        # Get the uploaded PDF files
        model_paper_file = request.files['model_paper']
        syllabus_file = request.files['syllabus']

        # Extract text from the PDF files
        model_paper_text = extract_text_from_pdf(model_paper_file)
        syllabus_text = extract_text_from_pdf(syllabus_file)

        # Truncate the text to stay within the token limit
        model_paper_text = truncate_text(model_paper_text, max_tokens=2000)  # Adjust max_tokens as needed
        syllabus_text = truncate_text(syllabus_text, max_tokens=2000)  # Adjust max_tokens as needed

        # Generate questions using Groq LLM
        prompt = f"Generate a question paper based on the following model paper and syllabus:\n\nModel Paper:\n{model_paper_text}\n\nSyllabus:\n{syllabus_text}"
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",  # Specify the model
                messages=[{"role": "user", "content": prompt}],  # Correct message format
                temperature=0.7,
                max_tokens=500  # Limit the response size
            )
            questions = response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}. Please check the input size and try again."

        # Generate a PDF from the questions
        pdf_buffer = generate_pdf(questions, "question_paper.pdf")

        # Return the generated PDF as a downloadable file
        return send_file(pdf_buffer, as_attachment=True, download_name="question_paper.pdf", mimetype='application/pdf')
    
    return render_template('generate_paper.html')
