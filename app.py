import requests
from flask import Flask, render_template, request, jsonify

# The API endpoint for vehicle registration data
API_URL = "https://tobi-rc-api.vercel.app/?rc_number="

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def vehicle_lookup():
    """
    Handles both GET (initial page load) and POST (form submission) requests.
    """
    details = None
    error = None

    if request.method == "POST":
        # Get the vehicle number from the web form
        rc = request.form.get("rc_number", "").strip()
        url = API_URL + rc

        if not rc:
            error = "Please enter a vehicle registration number."
        else:
            print(f"Fetching data for vehicle: {rc}")
            try:
                # 1. Fetch data from the external API
                res = requests.get(url, timeout=10)
                res.raise_for_status()

                data = res.json()
                details = data.get("details")

                # 2. Handle missing / empty data
                if not details or all(v in (None, "", "NA") for v in details.values()):
                    details = None  # Clear details if not found
                    error = f"⚠️ Data not found for vehicle number: {rc}"
                
                # We won't save to 'karim.txt' in a web app, 
                # but you could log it to a database if needed.

            except requests.exceptions.ConnectionError:
                error = "❌ Unable to connect to the external data server."
            except requests.exceptions.Timeout:
                error = "❌ Request timed out."
            except ValueError:
                error = "❌ Invalid response received from the external server."
            except requests.exceptions.HTTPError as e:
                 error = f"❌ HTTP Error fetching data: {e}"
            except Exception as e:
                error = f"❌ An unexpected error occurred: {e}"

    # Render the HTML template, passing the results/errors
    return render_template("index.html", details=details, error=error)

if __name__ == "__main__":
    # In a production environment, you would use a more robust server (like Gunicorn)
    app.run(debug=True)