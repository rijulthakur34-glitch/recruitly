import json
from jinja2 import Template

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI Candidate Shortlist</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background-color: #f9fafb; color: #333; }
    h1 { color: #111827; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
    th, td { border: 1px solid #e5e7eb; padding: 12px; text-align: left; }
    th { background-color: #f3f4f6; font-weight: 600; color: #374151; }
    .score { font-size: 1.1em; font-weight: bold; }
    .justification { display: block; font-size: 0.85em; color: #6b7280; margin-top: 4px; }
    .hire { color: #059669; font-weight: bold; }
    .no-hire { color: #dc2626; font-weight: bold; }
</style>
</head>
<body>
    <h1>AI Candidate Shortlist Report</h1>
    <table>
        <tr>
            <th>Candidate Name</th>
            <th>Total Score (Weighted)</th>
            <th>Skills (30%)</th>
            <th>Experience (25%)</th>
            <th>Education (15%)</th>
            <th>Projects (20%)</th>
            <th>Communication (10%)</th>
            <th>Recommendation</th>
        </tr>
        {% for c in candidates %}
        <tr>
            <td><strong>{{ c.name }}</strong></td>
            <td class="score">{{ c.total_score }} / 10</td>
            <td>
                <span class="score">{{ c.skills_match.score }}</span>
                <span class="justification">{{ c.skills_match.justification }}</span>
            </td>
            <td>
                <span class="score">{{ c.experience_relevance.score }}</span>
                <span class="justification">{{ c.experience_relevance.justification }}</span>
            </td>
            <td>
                <span class="score">{{ c.education_certs.score }}</span>
                <span class="justification">{{ c.education_certs.justification }}</span>
            </td>
            <td>
                <span class="score">{{ c.project_portfolio.score }}</span>
                <span class="justification">{{ c.project_portfolio.justification }}</span>
            </td>
            <td>
                <span class="score">{{ c.communication_quality.score }}</span>
                <span class="justification">{{ c.communication_quality.justification }}</span>
            </td>
            <td class="{{ 'hire' if c.recommendation == 'Hire' else 'no-hire' }}">
                {{ c.recommendation }}
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def generate_html_report_str(results: list) -> str:
    template = Template(HTML_TEMPLATE)
    return template.render(candidates=results)
