# 🎯 Voice-Based Greeting Agent - OpenCV Face Recognition System

A complete face recognition system using **OpenCV Haar Cascade** for accurate and reliable face detection, integrated with Face++ API for face matching and recognition.

## 🚀 Quick Start

### ⚡ **One-Command Setup & Launch**
```bash
# Make script executable (first time only)
chmod +x start_project.sh

# Start everything with one command!
./start_project.sh
```

**That's it!** The script will automatically:
- ✅ Set up virtual environment
- ✅ Install all dependencies
- ✅ Initialize the database
- ✅ Start the FastAPI server
- ✅ Open both HTML interfaces in your browser
- ✅ Keep everything running

### 🔧 **Manual Setup (Alternative)**
If you prefer manual setup:

```bash
# 1. Install dependencies
cd backend
pip install -r requirements-simple.txt

# 2. Initialize database
python3 init_database_sqlite.py

# 3. Start server
python3 start_server_opencv.py

# 4. Open HTML files manually
# - stark_opencv.html (Registration)
# - face_scanner_opencv.html (Face Scanner)
```

## 🎯 Features

### ✅ OpenCV Face Detection
- **Method**: Haar Cascade Classifier
- **Speed**: Fast local processing
- **Accuracy**: High for frontal, well-lit faces
- **Offline**: No internet required for detection

### ✅ Face Recognition
- **Method**: Face++ API for matching
- **Confidence**: 85% threshold for reliability
- **Database**: SQLite with employee records
- **Dynamic**: Automatic new employee registration

### ✅ User Interface
- **Real-time Camera**: Live video feed
- **Auto-scan Mode**: Continuous scanning
- **Manual Capture**: Single-shot recognition
- **Employee Display**: Complete information

## 📁 Project Structure

```
Voice Based Greeeting agent/
├── start_project.sh                 # 🚀 One-command startup script
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/           # API endpoints
│   │   │   └── recognition_opencv.py
│   │   ├── models_sqlite/           # Database models
│   │   ├── services/                # Business logic
│   │   │   ├── opencv_face_service.py
│   │   │   └── employee_service_sqlite.py
│   │   ├── main_opencv.py           # FastAPI app
│   │   ├── config_sqlite.py         # Configuration
│   │   └── database_sqlite.py       # Database setup
│   ├── start_server_opencv.py       # Server startup
│   ├── init_database_sqlite.py      # Database init
│   ├── requirements-simple.txt      # Dependencies
│   └── greeting_agent.db            # SQLite database
├── stark_opencv.html                # Employee registration
├── face_scanner_opencv.html         # Face scanner
├── .gitignore                       # Git ignore rules
└── README.md                        # This documentation
```

## 🔧 Technical Details

### 🚀 **Startup Script Features**
The `start_project.sh` script provides:
- **🔄 Automatic Setup**: Creates virtual environment and installs dependencies
- **🗄️ Database Initialization**: Sets up SQLite database with required tables
- **🌐 Server Management**: Starts FastAPI server in background
- **🖥️ Browser Integration**: Automatically opens HTML interfaces
- **📊 Status Monitoring**: Real-time server status and health checks
- **🧹 Cleanup**: Proper shutdown and cleanup on exit (Ctrl+C)
- **🎨 Colored Output**: Beautiful terminal interface with status indicators

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLite
- **Face Detection**: OpenCV Haar Cascade
- **Face Recognition**: Face++ API
- **ORM**: SQLAlchemy

### Frontend
- **HTML/CSS/JavaScript**: Vanilla web technologies
- **Camera API**: getUserMedia for video capture
- **Real-time Processing**: Canvas API for image capture

## 📖 Documentation

- **Main Documentation**: `README.md` (this file)
- **Project Requirements**: `Statement of Work - Voice-Based Greeting Agent.pdf`
- **User Stories**: `User Stories - Voice-Based Greeting Agent.pdf`

## 🎉 Current Status

✅ **Server**: Running on http://localhost:8000  
✅ **Detection**: Pure OpenCV Haar Cascade  
✅ **Database**: SQLite with all employees  
✅ **Registration**: Working with date conversion  
✅ **Recognition**: 85% confidence threshold  

## 🧪 Testing

### Test Registration
1. Open `stark_opencv.html`
2. Fill employee details
3. Upload face image
4. System detects face with OpenCV
5. Registers employee successfully

### Test Recognition
1. Open `face_scanner_opencv.html`
2. Start camera
3. Use "Capture & Recognize" or "Auto Scan Mode"
4. System detects face with OpenCV
5. Returns employee details if recognized

## 🔑 API Endpoints

- `POST /api/v1/recognition/scan-face` - Face detection and recognition
- `POST /api/v1/recognition/register` - Employee registration
- `GET /health` - Health check

## 📊 Database Schema

### Employees Table
- `employee_id` (UUID)
- `name`, `email`, `employee_number`
- `position`, `department`
- `date_of_birth`, `joining_date`
- `face_data` (Face++ token)
- `is_active`, `is_self_registered`

## 🎯 Benefits

- **🚀 Fast**: Local OpenCV processing
- **🔒 Reliable**: Consistent detection
- **💰 Cost Effective**: No API costs for detection
- **🔐 Private**: Local face detection
- **📈 Scalable**: Multiple users supported

---

**The OpenCV face detection system is fully operational and ready for production use!** 🎯