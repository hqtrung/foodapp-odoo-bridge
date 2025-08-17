import os
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from google.cloud import storage
from PIL import Image
from io import BytesIO
import requests


class CloudStorageService:
    """Service for uploading and managing images in Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        """Initialize Cloud Storage service"""
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'finiziapp')
        self.bucket_name = bucket_name or f"{self.project_id}-foodorder-images"
        
        # Initialize client
        self.client = storage.Client(project=self.project_id)
        self.bucket = None
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist and configure for public access"""
        try:
            self.bucket = self.client.bucket(self.bucket_name)
            # Test if bucket exists
            self.bucket.reload()
            print(f"✅ Using existing Cloud Storage bucket: {self.bucket_name}")
        except Exception:
            # Create bucket if it doesn't exist
            try:
                self.bucket = self.client.create_bucket(self.bucket_name, location="asia-southeast1")
                print(f"✅ Created new Cloud Storage bucket: {self.bucket_name}")
                
                # Make bucket publicly readable
                self._configure_public_access()
                
            except Exception as e:
                print(f"❌ Error creating bucket: {e}")
                # Try to get existing bucket anyway
                self.bucket = self.client.bucket(self.bucket_name)
    
    def _configure_public_access(self):
        """Configure bucket for public read access"""
        try:
            policy = self.bucket.get_iam_policy(requested_policy_version=3)
            policy.bindings.append({
                "role": "roles/storage.objectViewer",
                "members": ["allUsers"]
            })
            self.bucket.set_iam_policy(policy)
            print(f"✅ Configured public access for bucket: {self.bucket_name}")
        except Exception as e:
            print(f"⚠️ Could not configure public access: {e}")
    
    def upload_image_from_base64(self, base64_data: str, filename: str, 
                                folder: str = "images") -> Optional[str]:
        """Upload image from base64 data to Cloud Storage"""
        try:
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Process image with PIL to ensure it's valid and optimize
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (removes alpha channel)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Save optimized image
            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=85, optimize=True)
            optimized_data = output_buffer.getvalue()
            
            # Generate unique filename with hash
            content_hash = hashlib.md5(optimized_data).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d")
            blob_name = f"{folder}/{timestamp}/{content_hash}_{filename}.jpg"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                optimized_data,
                content_type="image/jpeg"
            )
            
            # Make blob publicly readable
            blob.make_public()
            
            # Return public URL
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            print(f"✅ Uploaded image: {blob_name}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Error uploading image {filename}: {e}")
            return None
    
    def upload_image_from_url(self, image_url: str, filename: str, 
                             folder: str = "images") -> Optional[str]:
        """Download image from URL and upload to Cloud Storage"""
        try:
            # Download image from Odoo
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Process image with PIL
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Save optimized image
            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=85, optimize=True)
            optimized_data = output_buffer.getvalue()
            
            # Generate unique filename
            content_hash = hashlib.md5(optimized_data).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d")
            blob_name = f"{folder}/{timestamp}/{content_hash}_{filename}.jpg"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                optimized_data,
                content_type="image/jpeg"
            )
            
            # Make blob publicly readable
            blob.make_public()
            
            # Return public URL
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            print(f"✅ Uploaded image from URL: {blob_name}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Error uploading image from URL {image_url}: {e}")
            return None
    
    def generate_multiple_sizes(self, base64_data: str, filename: str, 
                               folder: str = "images") -> Dict[str, str]:
        """Generate and upload multiple image sizes"""
        sizes = {
            'small': 128,
            'medium': 256, 
            'large': 512,
            'extra_large': 1024
        }
        
        urls = {}
        
        try:
            # Decode and open image
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Generate hash for consistent naming
            content_hash = hashlib.md5(image_data).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d")
            
            for size_name, size in sizes.items():
                try:
                    # Resize image maintaining aspect ratio
                    resized_image = image.copy()
                    resized_image.thumbnail((size, size), Image.Resampling.LANCZOS)
                    
                    # Save resized image
                    output_buffer = BytesIO()
                    resized_image.save(output_buffer, format="JPEG", quality=85, optimize=True)
                    resized_data = output_buffer.getvalue()
                    
                    # Upload to Cloud Storage
                    blob_name = f"{folder}/{timestamp}/{content_hash}_{filename}_{size_name}.jpg"
                    blob = self.bucket.blob(blob_name)
                    blob.upload_from_string(
                        resized_data,
                        content_type="image/jpeg"
                    )
                    
                    # Make blob publicly readable
                    blob.make_public()
                    
                    # Store public URL
                    urls[size_name] = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
                    
                except Exception as e:
                    print(f"❌ Error creating {size_name} size for {filename}: {e}")
                    continue
            
            if urls:
                print(f"✅ Generated {len(urls)} sizes for {filename}")
            
            return urls
            
        except Exception as e:
            print(f"❌ Error generating multiple sizes for {filename}: {e}")
            return {}
    
    def delete_image(self, blob_name: str) -> bool:
        """Delete image from Cloud Storage"""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            print(f"✅ Deleted image: {blob_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting image {blob_name}: {e}")
            return False
    
    def list_images(self, folder: str = "images", limit: int = 100) -> list:
        """List images in a folder"""
        try:
            blobs = self.client.list_blobs(
                self.bucket_name, 
                prefix=f"{folder}/",
                max_results=limit
            )
            
            images = []
            for blob in blobs:
                images.append({
                    'name': blob.name,
                    'public_url': f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}",
                    'size': blob.size,
                    'created': blob.time_created,
                    'updated': blob.updated
                })
            
            return images
            
        except Exception as e:
            print(f"❌ Error listing images: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check Cloud Storage service health"""
        try:
            # Test bucket access
            self.bucket.reload()
            
            # Count objects
            blobs = list(self.client.list_blobs(self.bucket_name, max_results=1))
            
            return {
                'status': 'healthy',
                'bucket_name': self.bucket_name,
                'project_id': self.project_id,
                'accessible': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'bucket_name': self.bucket_name,
                'project_id': self.project_id,
                'error': str(e),
                'accessible': False
            }