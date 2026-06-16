import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from github_utils import fetch_pr_diff
from ai_utils import analyze_code

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'reviewpilot-dev-secret-key')


@app.route('/')
def index():
    """Render the landing page."""
    return render_template('index.html')


@app.route('/review', methods=['POST'])
def review():
    """Render the review results page."""
    return render_template('review.html')


@app.route('/api/review', methods=['POST'])
def api_review():
    """
    API endpoint for code review.
    Accepts JSON: { type: 'pr'|'snippet', url?, code?, language?, token? }
    Returns structured review JSON.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        review_type = data.get('type', '')

        if review_type == 'pr':
            # Handle GitHub PR review
            url = data.get('url', '').strip()
            token = data.get('token', '').strip() or None

            if not url:
                return jsonify({'error': 'GitHub PR URL is required'}), 400

            try:
                pr_data = fetch_pr_diff(url, token)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

            diff = pr_data['diff']
            pr_info = pr_data['pr_info']

            if not diff.strip():
                return jsonify({
                    'error': 'The pull request has no changes to review.'
                }), 400

            review = analyze_code(
                code=diff,
                input_type='pull request diff',
                pr_info=pr_info
            )
            review['pr_info'] = pr_info

        elif review_type == 'snippet':
            # Handle code snippet review
            code = data.get('code', '').strip()
            language = data.get('language', '').strip() or None

            if not code:
                return jsonify({'error': 'Code snippet is required'}), 400

            if len(code) < 10:
                return jsonify({
                    'error': 'Code snippet is too short for meaningful analysis. '
                             'Please provide at least a few lines of code.'
                }), 400

            review = analyze_code(
                code=code,
                input_type='code snippet',
                language=language
            )

        else:
            return jsonify({
                'error': 'Invalid review type. Use "pr" or "snippet".'
            }), 400

        return jsonify(review)

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
