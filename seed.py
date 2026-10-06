"""Fills MongoDB with the content that is currently written inside the React portfolio,
so the website looks the same after you connect it. Safe to run many times: it only adds what is missing.

Run:  python seed.py
"""
import os
import shutil

from app import create_app, extensions
from app.config import Config
from app.utils.auth import hash_password
from app.utils.text import slugify, utcnow

HERE = os.path.dirname(os.path.abspath(__file__))


def copy_image(name):
    """Copy a starter image into the uploads folder and register it in the media collection."""
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    target = os.path.join(Config.UPLOAD_DIR, name)
    if not os.path.exists(target):
        shutil.copy(os.path.join(HERE, "seed_assets", name), target)
    db = extensions.db
    if not db["media"].find_one({"filename": name}):
        db["media"].insert_one({"filename": name, "original_name": name, "url": f"/uploads/{name}",
                                "file_type": "image/avif", "size": os.path.getsize(target), "created_at": utcnow()})
    return f"/uploads/{name}"


def add_many(name, items):
    db = extensions.db
    if db[name].count_documents({}) == 0:
        now = utcnow()
        for i, item in enumerate(items):
            db[name].insert_one({**item, "display_order": i, "is_active": True, "created_at": now, "updated_at": now})


def seed():
    app = create_app()  # connects to MongoDB and creates indexes
    db = extensions.db
    now = utcnow()

    if not db["users"].find_one({}):
        db["users"].insert_one({"email": Config.ADMIN_EMAIL.lower(), "password_hash": hash_password(Config.ADMIN_PASSWORD),
                                "created_at": now})
        print(f"Created admin {Config.ADMIN_EMAIL}. CHANGE THE DEFAULT PASSWORD AFTER YOUR FIRST LOGIN.")

    profile = copy_image("profile.avif")

    if not db["about"].find_one({}):
        db["about"].insert_one({
            "name": "Darsh Patel", "title": "Python Developer",
            "hero_text": "I build powerful, scalable, and secure applications that automate tasks, manage data, and solve problems for users.",
            "profile_image": profile, "journey_title": "My Journey",
            "journey_text": (
                "I started with a curiosity for coding and a passion for solving problems with Python. As I explored development, "
                "I began building projects, learning backend technologies, and creating practical solutions that turn ideas into reality. "
                "I'm constantly improving my skills and exploring new technologies to build smarter, more efficient applications.\n\n"
                "With every project, I strive to write cleaner code, explore new technologies, and develop solutions that make a real difference. "
                "From building backend systems to automating repetitive tasks, I enjoy turning complex challenges into simple, reliable, "
                "and efficient applications while continuously growing as a developer."),
            "email": "support@emma.sample.com", "phone": "+91 123456789", "location": "New Delhi, Ashok Nagar",
            "github_url": "", "linkedin_url": "", "twitter_url": "", "dribbble_url": "", "resume_url": "",
            "cta_primary_text": "View Work", "cta_secondary_text": "Contact Me", "created_at": now, "updated_at": now})

    add_many("highlights", [
        {"title": "Innovative", "icon": "FaLightbulb", "description": "I love creating unique solutions to complex problems with cutting-edge technologies."},
        {"title": "Design Oriented", "icon": "FaPaintBrush", "description": "Beautiful design and user experience are at the heart of everything I create."},
        {"title": "Clean Code", "icon": "FaCode", "description": "I write maintainable, efficient code following best practices and modern patterns."},
    ])

    add_many("skills", [
        {"title": "Frontend Development", "icon": "FaReact", "description": "Building responsive and interactive user interfaces with modern frameworks.", "tags": ["React", "Vue.js", "Angular", "TypeScript"]},
        {"title": "Backend Development", "icon": "FaServer", "description": "Creating robust server-side applications and RESTful APIs.", "tags": ["Node.js", "Express", "Django", "Laravel"]},
        {"title": "Database Management", "icon": "FaDatabase", "description": "Designing and optimizing databases for performance and scalability.", "tags": ["MongoDB", "PostgreSQL", "MySQL", "Firebase"]},
        {"title": "Mobile Development", "icon": "FaMobileAlt", "description": "Building cross-platform mobile applications with modern tools.", "tags": ["React Native", "Flutter", "Ionic", "Swift"]},
        {"title": "Cloud & DevOps", "icon": "FaCloud", "description": "Deploying and managing applications in cloud environments.", "tags": ["AWS", "Docker", "Kubernetes", "CI/CD"]},
        {"title": "Tools & Technologies", "icon": "FaTools", "description": "Essential tools and technologies I use in my development workflow.", "tags": ["Git & GitHub", "Webpack", "Figma", "Jest"]},
    ])

    if db["projects"].count_documents({}) == 0:
        starter = [
            ("E-Commerce Platform", "A full-featured online store with shopping cart, user authentication, and payment processing.", ["React", "Node.js", "MongoDB", "Stripe"]),
            ("Task Management App", "A productivity application with drag-and-drop functionality and real-time updates.", ["Vue.js", "Firebase", "Tailwind CSS", "WebSockets"]),
            ("Fitness Tracker", "A mobile app for tracking workouts, nutrition, and health metrics.", ["React Native", "GraphQL", "MySQL", "Chart.js"]),
            ("Portfolio Website", "A personal portfolio to showcase projects, skills, and blogs with dark/light mode support.", ["Next.js", "Tailwind CSS", "Framer Motion", "Markdown"]),
            ("Chat App", "A real-time chat application with group messaging, emojis, and file sharing.", ["Socket.IO", "React", "Node.js", "MongoDB"]),
            ("AI Image Generator", "Generate images using AI prompts powered by OpenAI's DALL·E model and Cloudinary.", ["React", "OpenAI API", "Cloudinary", "Tailwind CSS"]),
        ]
        for i, (title, description, tech) in enumerate(starter):
            db["projects"].insert_one({
                "title": title, "slug": slugify(title), "description": description, "full_description": "",
                "image": copy_image(f"project{i + 1}.avif"), "tech": tech, "demo_url": "", "github_url": "",
                "featured": False, "published": True, "display_order": i, "created_at": now, "updated_at": now})

    add_many("experience", [
        {"role": "Senior Frontend Developer", "company": "TechCorp Inc.", "duration": "2020 - Present", "description": "Leading frontend development for enterprise clients, implementing modern frameworks, and mentoring junior developers."},
        {"role": "Web Developer", "company": "Digital Solutions LLC", "duration": "2018 - 2020", "description": "Developed and maintained web applications for various clients, focusing on responsive design and performance optimization."},
        {"role": "Junior Developer", "company": "StartUp Ventures", "duration": "2016 - 2018", "description": "Started my career building basic websites and gradually took on more complex projects as I expanded my skill set."},
    ])

    for key, value in {"site_name": "Darsh Patel", "footer_text": "© 2025 Darsh Patel. All rights reserved."}.items():
        db["settings"].update_one({"key": key}, {"$setOnInsert": {"value": value}}, upsert=True)

    print("Seed finished.")


if __name__ == "__main__":
    seed()
