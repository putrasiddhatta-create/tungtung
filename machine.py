import os
import threading
import pandas as pd
import numpy as np


# HTML Template with beautiful CSS (Bootstrap) and Javascript for dynamic interactivity
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Sleep Insights Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #0f172a;
            color: #f1f5f9;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
        }
        .form-label {
            color: #cbd5e1;
            font-weight: 500;
        }
        .btn-custom {
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
        }
        .btn-custom:hover {
            background-color: #2563eb;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="text-center mb-5">
            <h1 class="fw-bold text-primary">🌙 Sleep Insights & Forecast Portal</h1>
            <p class="text-muted">Enter your personalized demographics and sleep metrics to predict total sleep and analyze habits.</p>
        </div>

        <div class="row g-4">
            <!-- Left Side Panel Inputs -->
            <div class="col-lg-6">
                <div class="card p-4 shadow-sm">
                    <h4 class="mb-4 text-warning">🛠️ Lifestyle Inputs</h4>
                    <form id="predictionForm">
                        <div class="mb-3">
                            <label class="form-label">Bedtime Phone Screen Time (Minutes)</label>
                            <input type="range" class="form-range" id="screenTime" min="0" max="300" value="60" oninput="this.nextElementSibling.value = this.value">
                            <output class="text-info d-block mt-1">60</output> mins
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Screen Brightness (%)</label>
                            <input type="range" class="form-range" id="brightness" min="0" max="100" value="50" oninput="this.nextElementSibling.value = this.value">
                            <output class="text-info d-block mt-1">50</output> %
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Age</label>
                            <input type="range" class="form-range" id="age" min="10" max="100" value="30" oninput="this.nextElementSibling.value = this.value">
                            <output class="text-info d-block mt-1">30</output> years old
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Caffeine Post-5pm (mg)</label>
                            <input type="range" class="form-range" id="caffeine" min="0" max="300" value="50" oninput="this.nextElementSibling.value = this.value">
                            <output class="text-info d-block mt-1">50</output> mg
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Physical Activity (Minutes)</label>
                            <input type="range" class="form-range" id="activity" min="0" max="180" value="30" oninput="this.nextElementSibling.value = this.value">
                            <output class="text-info d-block mt-1">30</output> mins
                        </div>
                    </form>
                </div>
            </div>

            <!-- Right Side Dashboard Results -->
            <div class="col-lg-6">
                <div class="card p-4 shadow-sm h-100 d-flex flex-column justify-content-between">
                    <div>
                        <h4 class="text-success mb-4">📊 AI Prediction Insights</h4>
                        <div class="mb-4">
                            <h5>Predicted Total Sleep:</h5>
                            <h2 class="display-4 fw-bold text-info" id="sleepResult">Calculating...</h2>
                        </div>
                        <div class="alert alert-secondary text-dark" role="alert" id="adviceBox">
                            Adjust the inputs to update the recommendation model.
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <canvas id="impactChart" style="max-height: 200px;"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let chart;

        function initChart() {
            const ctx = document.getElementById('impactChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Phone Time', 'Brightness', 'Caffeine', 'Exercise'],
                    datasets: [{
                        label: 'Estimated Loss/Gain Hours',
                        data: [0, 0, 0, 0],
                        backgroundColor: ['rgba(239, 68, 68, 0.7)', 'rgba(239, 68, 68, 0.7)', 'rgba(239, 68, 68, 0.7)', 'rgba(34, 197, 94, 0.7)'],
                        borderColor: ['#ef4444', '#ef4444', '#ef4444', '#22c55e'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        async function fetchPrediction() {
            const screenTime = document.getElementById('screenTime').value;
            const brightness = document.getElementById('brightness').value;
            const age = document.getElementById('age').value;
            const caffeine = document.getElementById('caffeine').value;
            const activity = document.getElementById('activity').value;

            const response = await fetch(`/predict?screentime=${screenTime}&brightness=${brightness}&age=${age}&caffeine=${caffeine}&activity=${activity}`);
            const data = await response.json();

            document.getElementById('sleepResult').innerText = data.predicted_sleep.toFixed(2) + ' Hours';
            document.getElementById('adviceBox').innerHTML = `<strong>Habit Advice:</strong> ${data.advice}`;
            document.getElementById('adviceBox').className = `alert ${data.predicted_sleep < 6 ? 'alert-danger' : 'alert-success'}`;

            // Update chart data
            chart.data.datasets[0].data = [
                parseFloat(data.impacts.phone),
                parseFloat(data.impacts.brightness),
                parseFloat(data.impacts.caffeine),
                parseFloat(data.impacts.exercise)
            ];
            chart.update();
        }

        // Bind listeners to trigger prediction updates on UI input interaction
        document.querySelectorAll('.form-range').forEach(input => {
            input.addEventListener('input', fetchPrediction);
        });

        window.onload = () => {
            initChart();
            fetchPrediction();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_content)

@app.route('/predict')
def predict():
    # Retrieve URL params
    screentime = float(request.args.get('screentime', 60))
    brightness = float(request.args.get('brightness', 50))
    age = float(request.args.get('age', 30))
    caffeine = float(request.args.get('caffeine', 50))
    activity = float(request.args.get('activity', 30))

    # Use the pre-trained linear regression model from variable environment
    input_features = [[screentime, brightness, age, caffeine, activity]]
    predicted_hours = lr_model.predict(input_features)[0]

    # Compute real-time weight impacts based on coefficients
    impacts = {
        'phone': screentime * lr_model.coef_[0],
        'brightness': brightness * lr_model.coef_[1],
        'caffeine': caffeine * lr_model.coef_[3],
        'exercise': activity * lr_model.coef_[4]
    }

    # Dynamically generate interactive clinical advice
    if predicted_hours < 6.0:
        advice = "Your predicted sleep is quite low. Try minimizing evening phone minutes and lowering your screen brightness!"
    elif predicted_hours >= 7.5:
        advice = "Excellent! This routine yields a healthy and highly restorative sleep schedule."
    else:
        advice = "Your sleep schedule is acceptable, but you can improve it further by capping screen time and caffeine post-5 PM."

    return jsonify({
        'predicted_sleep': predicted_hours,
        'impacts': impacts,
        'advice': advice
    })

# Run the Flask app in a background thread to prevent blocking Google Colab cells
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Check if port is running or run
thread = threading.Thread(target=run_flask)
thread.daemon = True
thread.start()

