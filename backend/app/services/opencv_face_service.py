import cv2
import numpy as np
import base64
import io
import logging
from typing import Dict, Any, List, Optional
from PIL import Image
import requests

logger = logging.getLogger(__name__)

class OpenCVFaceDetectionService:
    """Pure OpenCV Haar Cascade face detection service"""
    
    def __init__(self):
        # Load OpenCV Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            logger.error("Could not load Haar cascade classifier. Check path.")
            raise IOError("Could not load Haar cascade classifier.")
        logger.info("OpenCV Haar cascade classifier loaded successfully.")
        
        # Face++ API for face recognition (we still need this for face matching)
        from app.config_sqlite import settings
        self.api_key = settings.facepp_api_key
        self.api_secret = settings.facepp_api_secret
        self.faceset_token = settings.facepp_faceset_token
        
        # Face++ API endpoints
        self.detect_url = "https://api-us.faceplusplus.com/facepp/v3/detect"
        self.search_url = "https://api-us.faceplusplus.com/facepp/v3/search"
        self.faceset_add_url = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
        self.faceset_create_url = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
        self.faceset_get_url = "https://api-us.faceplusplus.com/facepp/v3/faceset/getfacesets"
        
        logger.info(f"Initialized OpenCV Face Detection Service")

    def detect_faces_opencv(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Detect faces using OpenCV Haar Cascade only
        Returns a list of detected face rectangles (x, y, w, h)
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.warning("OpenCV failed to decode image data.")
                return []

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with improved parameters for better accuracy
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,      # How much the image size is reduced at each image scale
                minNeighbors=5,       # How many neighbors each candidate rectangle should have
                minSize=(30, 30),     # Minimum possible object size
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            detected_faces = []
            for (x, y, w, h) in faces:
                # Calculate face quality metrics
                face_roi = gray[y:y+h, x:x+w]
                
                # Check if face is large enough (minimum 50x50 pixels)
                if w >= 50 and h >= 50:
                    detected_faces.append({
                        'x': int(x),
                        'y': int(y), 
                        'width': int(w),
                        'height': int(h),
                        'area': int(w * h),
                        'quality': 'good' if w >= 100 and h >= 100 else 'acceptable'
                    })
            
            logger.info(f"OpenCV detected {len(detected_faces)} valid faces")
            return detected_faces
            
        except Exception as e:
            logger.error(f"OpenCV face detection error: {e}")
            return []

    async def get_face_token_from_facepp(self, image_data: bytes) -> Optional[str]:
        """
        Get face_token from Face++ API for a detected face
        This is needed for face recognition/matching
        """
        try:
            # Validate and resize image before sending to Face++ API
            processed_image_data = self._validate_and_resize_image(image_data)
            if not processed_image_data:
                logger.error("Image validation/resizing failed")
                return None
            
            response = requests.post(
                self.detect_url,
                data={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret
                },
                files={'image_file': processed_image_data},
                timeout=10
            )
            
            result = response.json()
            logger.info(f"Face++ detect response: {result}")

            if 'faces' in result and len(result['faces']) > 0:
                face_token = result['faces'][0]['face_token']
                logger.info(f"Face++ detected face, token: {face_token[:10]}...")
                return face_token
            
            logger.warning("No face detected by Face++ API.")
            return None
            
        except Exception as e:
            logger.error(f"Face++ detection error: {e}")
            return None

    def _validate_and_resize_image(self, image_data: bytes) -> Optional[bytes]:
        """
        Validate and resize image to meet Face++ API requirements:
        - Max file size: 2MB
        - Min dimensions: 100x100 pixels
        - Max dimensions: 4096x4096 pixels
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.error("Failed to decode image data")
                return None
            
            height, width = img.shape[:2]
            logger.info(f"Original image size: {width}x{height}")
            
            # Check minimum dimensions
            if width < 100 or height < 100:
                logger.error(f"Image too small: {width}x{height}. Minimum is 100x100")
                return None
            
            # Check maximum dimensions and resize if needed
            max_size = 2048  # Conservative max size for Face++ API
            if width > max_size or height > max_size:
                # Calculate new dimensions maintaining aspect ratio
                if width > height:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                else:
                    new_height = max_size
                    new_width = int(width * max_size / height)
                
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized image to: {new_width}x{new_height}")
            
            # Encode back to JPEG with quality 85 (good balance of quality vs size)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            success, encoded_img = cv2.imencode('.jpg', img, encode_param)
            
            if not success:
                logger.error("Failed to encode image")
                return None
            
            encoded_bytes = encoded_img.tobytes()
            
            # Check final file size (should be well under 2MB)
            file_size_mb = len(encoded_bytes) / (1024 * 1024)
            logger.info(f"Final image size: {file_size_mb:.2f} MB")
            
            if file_size_mb > 2:
                logger.error(f"Image still too large after resizing: {file_size_mb:.2f} MB")
                return None
            
            return encoded_bytes
            
        except Exception as e:
            logger.error(f"Image validation/resizing error: {e}")
            return None

    async def detect_and_validate_face(self, image_data: bytes) -> Dict[str, Any]:
        """
        Primary face detection method using OpenCV Haar Cascade
        Validates face quality and gets face_token for recognition
        """
        try:
            # Step 1: Detect faces using OpenCV
            opencv_faces = self.detect_faces_opencv(image_data)
            
            if not opencv_faces:
                logger.warning("No faces detected by OpenCV")
                return {
                    'status': 'no_face_detected',
                    'message': 'No face detected in the image. Please ensure your face is clearly visible.',
                    'opencv_faces': [],
                    'face_token': None
                }
            
            # Step 2: Validate face quality
            best_face = max(opencv_faces, key=lambda f: f['area'])
            
            if best_face['area'] < 2500:  # Less than 50x50 pixels
                logger.warning(f"Face too small: {best_face['area']} pixels")
                return {
                    'status': 'face_too_small',
                    'message': 'Face detected but too small. Please move closer to the camera.',
                    'opencv_faces': opencv_faces,
                    'face_token': None
                }
            
            # Step 3: Get face_token from Face++ for recognition
            face_token = await self.get_face_token_from_facepp(image_data)
            
            if not face_token:
                logger.warning("OpenCV detected face but Face++ could not process it")
                return {
                    'status': 'face_processing_failed',
                    'message': 'Face detected but could not be processed. Please try again.',
                    'opencv_faces': opencv_faces,
                    'face_token': None
                }
            
            logger.info(f"Successfully detected and validated face: {best_face['quality']} quality, {best_face['area']} pixels")
            
            return {
                'status': 'face_detected',
                'message': 'Face detected successfully',
                'opencv_faces': opencv_faces,
                'face_token': face_token,
                'best_face': best_face
            }
            
        except Exception as e:
            logger.error(f"Face detection and validation error: {e}")
            return {
                'status': 'error',
                'message': f'Face detection failed: {str(e)}',
                'opencv_faces': [],
                'face_token': None
            }

    async def create_faceset_if_not_exists(self) -> str:
        """Create a FaceSet if it doesn't exist or validate the existing one"""
        try:
            # First, try to get existing facesets
            response = requests.post(
                self.faceset_get_url,
                data={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret
                },
                timeout=10
            )

            result = response.json()
            logger.info(f"Face++ get facesets response: {result}")

            if 'facesets' in result and len(result['facesets']) > 0:
                faceset_token = result['facesets'][0]['faceset_token']
                logger.info(f"Using existing faceset: {faceset_token}")
                return faceset_token

            # Create new faceset if none exists
            response = requests.post(
                self.faceset_create_url,
                data={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                    'display_name': 'opencv_greeting_agent_faceset',
                    'outer_id': 'opencv_greeting_agent'
                },
                timeout=10
            )

            result = response.json()
            logger.info(f"Face++ create faceset response: {result}")

            if 'faceset_token' in result:
                faceset_token = result['faceset_token']
                logger.info(f"Created new faceset: {faceset_token}")
                return faceset_token
            else:
                logger.error(f"Failed to create faceset: {result}")
                return None

        except Exception as e:
            logger.error(f"Error creating/validating faceset: {e}")
            return None

    async def search_face(self, face_token: str) -> Optional[Dict[str, Any]]:
        """Search for matching face in FaceSet"""
        try:
            # Get or create faceset dynamically
            faceset_token = await self.create_faceset_if_not_exists()
            if not faceset_token:
                logger.error("Could not get faceset token")
                return None
            
            response = requests.post(
                self.search_url,
                data={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                    'face_token': face_token,
                    'faceset_token': faceset_token
                },
                timeout=10
            )
            
            result = response.json()
            logger.info(f"Face++ search response: {result}")
            
            if 'results' in result and len(result['results']) > 0:
                # Return the best match
                best_match = result['results'][0]
                confidence = best_match.get('confidence', 0)
                found_face_token = best_match.get('face_token', face_token)
                
                # Get user_id from face details
                user_id = ''
                try:
                    detail_response = requests.post(
                        'https://api-us.faceplusplus.com/facepp/v3/face/getdetail',
                        data={
                            'api_key': self.api_key,
                            'api_secret': self.api_secret,
                            'face_token': found_face_token
                        },
                        timeout=10
                    )
                    detail_result = detail_response.json()
                    user_id = detail_result.get('user_id', '')
                    logger.info(f"Face detail user_id: {user_id}")
                except Exception as e:
                    logger.warning(f"Could not get face detail: {str(e)}")
                
                logger.info(f"Face matched with confidence: {confidence}, user_id: {user_id}")
                return {
                    'confidence': confidence,
                    'user_id': user_id,
                    'face_token': found_face_token
                }
            
            logger.info("No matching face found in FaceSet")
            return None
            
        except Exception as e:
            logger.error(f"Face search error: {str(e)}")
            raise Exception(f"Face search failed: {str(e)}")

    async def add_face_to_faceset(self, face_token: str, employee_id: str) -> bool:
        """Add face to company FaceSet and set user_id"""
        try:
            # Get or create faceset dynamically
            faceset_token = await self.create_faceset_if_not_exists()
            if not faceset_token:
                logger.error("Could not get faceset token for adding face")
                return False
            
            # Step 1: Add face to FaceSet
            response = requests.post(
                self.faceset_add_url,
                data={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                    'faceset_token': faceset_token,
                    'face_tokens': face_token
                },
                timeout=10
            )
            
            result = response.json()
            logger.info(f"Face++ add face response: {result}")
            
            face_added = result.get('face_added', 0)
            if face_added > 0:
                logger.info(f"Successfully added face to FaceSet")
                
                # Step 2: Set user_id for the face token
                user_id_response = requests.post(
                    'https://api-us.faceplusplus.com/facepp/v3/face/setuserid',
                    data={
                        'api_key': self.api_key,
                        'api_secret': self.api_secret,
                        'face_token': face_token,
                        'user_id': employee_id
                    },
                    timeout=10
                )
                
                user_id_result = user_id_response.json()
                logger.info(f"Face++ set user_id response: {user_id_result}")
                
                if 'user_id' in user_id_result:
                    logger.info(f"Successfully linked face to employee {employee_id}")
                    return True
                else:
                    logger.error(f"Failed to set user_id for face: {user_id_result}")
                    return False
            else:
                logger.error(f"Failed to add face to FaceSet: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Add face to FaceSet error: {str(e)}")
            return False

    async def identify_or_register(self, image_data: bytes) -> Dict[str, Any]:
        """
        Main method: Detect face with OpenCV, then identify or register
        """
        try:
            # Step 1: Detect and validate face using OpenCV
            detection_result = await self.detect_and_validate_face(image_data)
            
            if detection_result['status'] != 'face_detected':
                return {
                    'status': 'detection_failed',
                    'message': detection_result['message'],
                    'employee_id': None,
                    'confidence': None,
                    'temp_id': None
                }
            
            face_token = detection_result['face_token']
            
            # Step 2: Search for existing face
            search_result = await self.search_face(face_token)
            
            if search_result and search_result.get('confidence', 0) > 60:  # Flexible confidence threshold for lighting variations
                employee_id = search_result.get('user_id')
                confidence = search_result.get('confidence', 0)
                
                if employee_id:
                    logger.info(f"Face recognized with {confidence}% confidence for employee {employee_id}")
                    return {
                        'status': 'recognized',
                        'message': f'Face recognized with {confidence}% confidence',
                        'employee_id': employee_id,
                        'confidence': confidence,
                        'temp_id': face_token
                    }
            
            # Step 3: New face detected
            logger.info("New face detected, registration required")
            return {
                'status': 'new_employee',
                'message': 'New face detected. Please complete registration.',
                'employee_id': None,
                'confidence': None,
                'temp_id': face_token
            }
            
        except Exception as e:
            logger.error(f"Face identification/registration error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Face processing failed: {str(e)}',
                'employee_id': None,
                'confidence': None,
                'temp_id': None
            }
