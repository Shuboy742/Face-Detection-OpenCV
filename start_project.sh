#!/bin/bash

# Voice-Based Greeting Agent - Easy Startup Script
# This script sets up and starts the entire project with one command

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}🎯 Voice-Based Greeting Agent${NC}"
    echo -e "${PURPLE}🚀 Easy Startup Script${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
check_port() {
    if command_exists netstat; then
        netstat -tuln | grep -q ":$1 "
    elif command_exists ss; then
        ss -tuln | grep -q ":$1 "
    else
        # Fallback: try to connect to the port
        timeout 1 bash -c "</dev/tcp/localhost/$1" 2>/dev/null
    fi
}

# Function to wait for server to start
wait_for_server() {
    local port=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for server to start on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            print_success "Server is running on port $port!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "Server failed to start within 30 seconds"
    return 1
}

# Function to open HTML files
open_html_files() {
    print_status "Opening HTML interfaces..."
    
    # Get the absolute path of the HTML files
    local project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local registration_file="$project_dir/stark_opencv.html"
    local scanner_file="$project_dir/face_scanner_opencv.html"
    
    # Check if files exist
    if [ ! -f "$registration_file" ]; then
        print_error "Registration file not found: $registration_file"
        return 1
    fi
    
    if [ ! -f "$scanner_file" ]; then
        print_error "Scanner file not found: $scanner_file"
        return 1
    fi
    
    # Try to open files with default browser
    if command_exists xdg-open; then
        print_success "Opening Registration Interface..."
        xdg-open "$registration_file" 2>/dev/null &
        sleep 2
        print_success "Opening Face Scanner Interface..."
        xdg-open "$scanner_file" 2>/dev/null &
    elif command_exists open; then
        print_success "Opening Registration Interface..."
        open "$registration_file" 2>/dev/null &
        sleep 2
        print_success "Opening Face Scanner Interface..."
        open "$scanner_file" 2>/dev/null &
    elif command_exists start; then
        print_success "Opening Registration Interface..."
        start "$registration_file" 2>/dev/null &
        sleep 2
        print_success "Opening Face Scanner Interface..."
        start "$scanner_file" 2>/dev/null &
    else
        print_warning "Could not automatically open HTML files."
        print_status "Please manually open these files in your browser:"
        echo -e "${CYAN}Registration:${NC} $registration_file"
        echo -e "${CYAN}Face Scanner:${NC} $scanner_file"
    fi
}

# Function to setup virtual environment
setup_venv() {
    local venv_dir="backend/venv"
    
    if [ ! -d "$venv_dir" ]; then
        print_status "Creating virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    cd backend
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please run setup first."
        exit 1
    fi
    
    # Install requirements
    if [ -f "requirements-simple.txt" ]; then
        pip install -r requirements-simple.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements-simple.txt not found"
        exit 1
    fi
    
    cd ..
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    cd backend
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Initialize database
    if [ -f "init_database_sqlite.py" ]; then
        python3 init_database_sqlite.py
        print_success "Database initialized successfully"
    else
        print_error "Database initialization script not found"
        exit 1
    fi
    
    cd ..
}

# Function to start server
start_server() {
    print_status "Starting FastAPI server..."
    
    cd backend
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Check if server is already running
    if check_port 8000; then
        print_warning "Server is already running on port 8000"
        print_status "Killing existing server process..."
        pkill -f "uvicorn.*main_opencv" || true
        sleep 2
    fi
    
    # Start server in background
    if [ -f "start_server_opencv.py" ]; then
        print_status "Starting server in background..."
        python3 start_server_opencv.py &
        SERVER_PID=$!
        echo $SERVER_PID > ../server.pid
        print_success "Server started with PID: $SERVER_PID"
    else
        print_error "Server startup script not found"
        exit 1
    fi
    
    cd ..
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    if [ -f "server.pid" ]; then
        SERVER_PID=$(cat server.pid)
        if kill -0 $SERVER_PID 2>/dev/null; then
            print_status "Stopping server (PID: $SERVER_PID)..."
            kill $SERVER_PID
            sleep 2
        fi
        rm -f server.pid
    fi
    
    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "stark_opencv.html" ] || [ ! -f "face_scanner_opencv.html" ]; then
        print_error "Please run this script from the project root directory"
        print_status "Expected files: stark_opencv.html, face_scanner_opencv.html"
        exit 1
    fi
    
    # Check if Python 3 is installed
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Setup steps
    print_status "Setting up Voice-Based Greeting Agent..."
    
    setup_venv
    install_dependencies
    init_database
    start_server
    
    # Wait for server to be ready
    if wait_for_server 8000; then
        print_success "🎉 Voice-Based Greeting Agent is ready!"
        echo ""
        echo -e "${GREEN}✅ Server Status:${NC} Running on http://localhost:8000"
        echo -e "${GREEN}✅ Health Check:${NC} http://localhost:8000/health"
        echo ""
        echo -e "${CYAN}📋 Available Interfaces:${NC}"
        echo -e "   • ${YELLOW}Employee Registration:${NC} stark_opencv.html"
        echo -e "   • ${YELLOW}Face Scanner:${NC} face_scanner_opencv.html"
        echo ""
        
        # Open HTML files
        open_html_files
        
        echo ""
        echo -e "${PURPLE}🎯 Project is ready to use!${NC}"
        echo -e "${CYAN}Press Ctrl+C to stop the server${NC}"
        echo ""
        
        # Keep script running
        while true; do
            sleep 1
            if ! kill -0 $SERVER_PID 2>/dev/null; then
                print_error "Server process died unexpectedly"
                break
            fi
        done
    else
        print_error "Failed to start the server"
        exit 1
    fi
}

# Run main function
main "$@"
