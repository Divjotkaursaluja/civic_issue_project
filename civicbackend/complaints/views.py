from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import Complaint, Department
from complaints.models import AdminUser
from django.core.files.storage import default_storage   # ❤️ ADD THIS
from math import sqrt
from django.db.models import Q
from django.db.models import Max
from django.core.mail import send_mail
from django.contrib.auth.models import User
import json
from ai_model.views import classify_image


from .models import Complaint
from .utils import is_nearby
@csrf_exempt
def check_duplicate_complaint(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)

    title = data.get("title")
    latitude = float(data.get("latitude"))
    longitude = float(data.get("longitude"))

    RADIUS = 0.001  # ~100 meters

    complaints = Complaint.objects.filter(title=title) 
    for c in complaints:
        if c.latitude is None or c.longitude is None:
            continue

        distance = sqrt(
            (c.latitude - latitude) ** 2 +
            (c.longitude - longitude) ** 2
        )

        if distance <= RADIUS:
            return JsonResponse({
                "duplicate": True,
                "complaint": {
                    "id": c.id,
                   "image": request.build_absolute_uri(c.image.url) if c.image else None,
                    "description": c.description,
                    "votes": c.votes,
                }
            })

    return JsonResponse({"duplicate": False})

@csrf_exempt
def create_complaint(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    title = request.POST.get("title")
    description = request.POST.get("description")

    # Handle optional latitude/longitude
    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")
    user_email = request.POST.get("user_email")
    print("Received user_email:", user_email)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "Image file required"}, status=400)

    # 🔍 Check for duplicate (only if coordinates provided)
    force_create = request.POST.get("force_create")
    if latitude and longitude:
        latitude = float(latitude)
        longitude = float(longitude)

        existing_complaints = Complaint.objects.filter(
            title__iexact=title
        ).exclude(status="Solved")

        for c in existing_complaints:
            if c.latitude and c.longitude:
                if is_nearby(latitude, longitude, c.latitude, c.longitude):

                    # ✅ ONLY return duplicate if user is NOT submitting form
                    if not request.POST.get("submit_anyway"):
                        return JsonResponse({
                            "duplicate": True,
                            "complaint": {
                                "id": c.id,
                                "image": c.image.url if c.image else None,
                                "description": c.description,
                                "votes": c.votes
                            }
                        })

    # ✅ No duplicate → proceed with AI classification
    try:
        # Save the uploaded file
        file_path = default_storage.save("complaint_images/" + file.name, file)
        full_path = default_storage.path(file_path)

        # Classify the image using AI
        predicted_class, confidence = classify_image(full_path);

        # Find the department based on predicted class
        department = None
        if predicted_class and predicted_class != "unknown":
            try:
                department = Department.objects.get(name__iexact=predicted_class)
            except Department.DoesNotExist:
                pass  
        title_map = {
            "Overflowing garbage bins": "trash_bins",
            "Broken streetlight": "streetlight",
            "Potholes": "potholes",
            "Water leakages": "water_leakage"
        }

        if not department:
            mapped_slug = title_map.get(title)

            if mapped_slug:
                try:
                    department = Department.objects.get(name__iexact=mapped_slug)
                except Department.DoesNotExist:
                    department = None

        # Create the complaint with prediction
        complaint = Complaint.objects.create(
            title=title,
            description=description,
            image=file,
            latitude=latitude,
            longitude=longitude,
            votes=1,
            status="Pending",
            predicted_class=predicted_class,
            department=department,
            user_email=user_email
           
        )

        return JsonResponse({
            "duplicate": False,
            "complaint_id": complaint.id,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "department": department.name if department else None
        })
      
    except Exception as e:
        return JsonResponse({
            "error": f"AI classification failed: {str(e)}"
        }, status=500)
    
@csrf_exempt
def list_all_complaints(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    complaints = Complaint.objects.all().order_by("-created_at")
    data = []

    for c in complaints:
        data.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "image": c.image.url if c.image else None,
            "status": c.status,
            "votes": c.votes,
            "department": c.department.name if c.department else None,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        })

 
    return JsonResponse({"complaints": data}, safe=False)
@csrf_exempt
@csrf_exempt
def complaint_heatmap_data(request):
    complaints = Complaint.objects.all()

    points = []
    for c in complaints:
        if c.latitude and c.longitude:
            points.append({
                "lat": c.latitude,
                "lng": c.longitude,
                "intensity": c.votes if c.votes else 1
            })

    return JsonResponse({"points": points})

    return JsonResponse({"points": data})



@csrf_exempt
def list_complaints_by_department(request, dept_slug):

    complaints = Complaint.objects.filter(
        department__name__iexact=dept_slug
    ).order_by("-created_at")

    data = []

    for c in complaints:

        votes = c.votes or 0

        if votes >= 5:
            intensity = "High"
        elif votes >= 3:
            intensity = "Medium"
        else:
            intensity = "Low"

        data.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "predicted": c.predicted_class,
            "status": c.status,
            "votes": votes,
            "intensity": intensity,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "image_url": c.image.url if c.image else None
        })

    return JsonResponse({"complaints": data})


@csrf_exempt
def update_complaint_status(request, complaint_id):

    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)

    data = json.loads(request.body)
    new_status = data.get("status")

    if new_status not in ["Pending", "In Progress", "Solved"]:
        return JsonResponse({"error": "Invalid status"}, status=400)

    # update complaint status
    complaint.status = new_status
    complaint.save()

    print("Status updated:", complaint.id, new_status)
    print("User email:", complaint.user_email)

    # send email notification
    if complaint.user_email:
        try:
            send_mail(
                "Complaint Status Updated",
                f"Your complaint '{complaint.title}' status is now '{new_status}'.",
                "yourgmail@gmail.com",
                [complaint.user_email],
                fail_silently=False,   # better for debugging
            )
            print("Email sent successfully")

        except Exception as e:
            print("Email error:", e)

    return JsonResponse({"message": "Status updated successfully"})


@csrf_exempt
def admin_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
        username = body.get("username")
        password = body.get("password")
        department = body.get("department")

        print("REQUEST DATA:", body)

        # DEBUG PRINT — CHECK YOUR DATABASE
        print("DB USERS:", list(AdminUser.objects.values()))

        admin = AdminUser.objects.filter(
            username=username,
            password=password,
            department=department
        ).first()

        print("MATCH FOUND:", admin)

        if not admin:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        return JsonResponse({
            "message": "Login successful",
            "token": "fake-jwt-token",
            "department": department
        })

    except Exception as e:
        print("ERROR:", str(e))
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
def vote_up_complaint(request, complaint_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)

    complaint.votes += 1
    complaint.save()

    return JsonResponse({
        "message": "Vote added",
        "votes": complaint.votes
    })


@csrf_exempt
def predict_image(request):
    
    print("/predict/ HIT - method:", request.method)
    

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        if 'file' not in request.FILES:
            return JsonResponse({"error": "Image file missing"}, status=400)

        file = request.FILES['file']
        print("Received file:", file.name)

        file_path = default_storage.save("uploads/" + file.name, file)

        predicted_class, confidence = classify_image(default_storage.path(file_path))

        return JsonResponse({
            "predicted_class": predicted_class,
            "confidence": confidence,
        })

    except Exception as e:
        print("ERROR in prediction:", str(e))
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def complaint_counts(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    data = {}

    departments = [
        "streetlight",
        "potholes",
        "trash_bins",
        "water_leakage",
        "higher_department"
    ]

    for dept in departments:
        if dept == "higher_department":
            qs = Complaint.objects.all()
        else:
            qs = Complaint.objects.filter(department__name__iexact=dept)

        data[dept] = {
            "pending": qs.filter(status="Pending").count(),
            "in_progress": qs.filter(status="In Progress").count(),
            "solved": qs.filter(status="Solved").count(),
        }

    return JsonResponse(data)
