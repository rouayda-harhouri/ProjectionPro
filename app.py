from flask import Flask,Response, render_template, request, redirect, url_for, session, send_from_directory, abort, jsonify, send_file
from pyproj import Proj, transform, Transformer
import folium

app = Flask(__name__)
app.secret_key = "q4s57DSF42s45S555ssZ236"

users = [
    {
        "username": "rouayda-marwa",
        "password": "admin",
        "firstname": "Admin",
        "lastname": "Application",
        "email": "rouaydamarwaa@projection.pro"
    },
        
   

# Define available projections
projections = {
    "mercator": "EPSG:3857",
    "robinson": "+proj=robin +lon_0=0 +datum=WGS84 +units=m +no_defs",
    "lambert": "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +datum=WGS84 +units=m +no_defs",
    "gnomonic": "+proj=gnom +lon_0=0 +datum=WGS84 +units=m +no_defs",
    "azimuthal": "+proj=aeqd +lat_0=0 +lon_0=0 +datum=WGS84 +units=m +no_defs"
}

# Coordinate conversion function
def convert_coordinates(from_proj, to_proj, lat, lon):
    from pyproj import Transformer
    transformer = Transformer.from_crs(from_proj, to_proj)
    x, y = transformer.transform(lat, lon)
    return x, y

# Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        for user in users:
            if (email == user['email'] and password == user['password']):
                session["user"] = user
                return redirect(url_for("systems"))
        return render_template("login.html", error = True)
    if "user" not in session:
        return render_template("login.html")
    else:
        return redirect(url_for("systems"))

# Health status
@app.route("/health", methods=["HEAD", "OPTION", "GET"])
def health():
    return "Server is running..."

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    try:
        # Serve the requested file from the static folder
        return send_from_directory('static', filename)
    except Exception:
        # Return a 404 error if the file does not exist
        abort(404)

# Coordinate conversion page
@app.route("/converter", methods=["GET", "POST"])
def converter():
    if "user" not in session:
        return redirect(url_for("login"))
    
    result = None
    if request.method == "POST":
        data = request.json
        try:
            from_system = projections[data['fromSystem']]
            to_system = projections[data['toSystem']]
            longitude = float(data['longitude'])
            latitude = float(data['latitude'])

            # Convert coordinates using pyproj
            transformer = Transformer.from_crs(from_system, to_system, always_xy=True)
            new_longitude, new_latitude = transformer.transform(longitude, latitude)

            # Generate JSON response
            return {
                "from_coords": {"projection": from_system, "latitude": latitude, "longitude": longitude},
                "to_coords": {"projection": to_system, "latitude": new_latitude, "longitude": new_longitude}
            }
        except KeyError:
            return jsonify({'error': 'Invalid projection system'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template("converter.html", projections=projections.keys(), result=result, current_path=request.path)

@app.route("/map", methods=["GET"])
def serve_html_map_direct():
    try:
        # Extract query parameters
        longitude = float(request.args.get("longitude"))
        latitude = float(request.args.get("latitude"))
        projection = request.args.get("projection", "Unknown Projection")

        # Create a Folium map
        my_map = folium.Map(location=[latitude, longitude], zoom_start=12)
        folium.Marker([latitude, longitude], popup=f"{projection}").add_to(my_map)

        # Render the map's HTML content
        html_content = my_map.get_root().render()

        # Return the HTML content as a response
        return Response(html_content, content_type="text/html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Projections systems page
@app.route("/systems")
def systems():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("systems.html", current_path=request.path)

# Source Code page
@app.route("/source")
def source():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("source.html", current_path=request.path)

# Profile page
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", current_path=request.path, user = session['user'])


# About page
@app.route("/about")
def about():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("about.html", current_path=request.path)

# Logout route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
