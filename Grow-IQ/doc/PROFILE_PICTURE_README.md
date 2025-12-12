# Profile Picture Upload System - Glow-IQ

A production-ready, secure profile picture upload system with modern UI/UX and comprehensive validation.

## 🚀 Features

### Core Functionality
- **File Upload**: Support for JPG, PNG, and WebP formats
- **Size Limits**: 2MB maximum file size
- **Security**: MIME type validation, secure filename generation
- **Preview**: Image preview with rotation controls
- **Drag & Drop**: Modern drag and drop interface
- **Progress Tracking**: Real-time upload progress indicators

### User Experience
- **Instant Updates**: All profile pictures update automatically across the interface
- **Responsive Design**: Works perfectly on all device sizes
- **Accessibility**: Full keyboard navigation and screen reader support
- **Error Handling**: User-friendly error messages and validation feedback
- **Fallback Support**: Graceful handling of missing images with default avatar

### Technical Features
- **Modular Architecture**: Clean separation of concerns
- **Event System**: Custom events for component communication
- **Database Integration**: Automatic profile picture URL storage
- **Cloud Ready**: Easy migration to S3 or other cloud storage
- **Production Ready**: Comprehensive error handling and logging

## 📁 File Structure

```
Glow-IQ/
├── static/
│   ├── css/
│   │   └── profile-picture-upload.css    # Modal styles
│   ├── js/
│   │   └── profile-picture-upload.js     # Upload logic
│   ├── uploads/
│   │   └── profile_pictures/             # Image storage
│   └── test-profile-picture.html         # Test page
├── templates/
│   └── home.html                         # Main template (updated)
├── models.py                             # User model (updated)
├── app.py                                # API endpoints (updated)
└── PROFILE_PICTURE_README.md             # This file
```

## 🗄️ Database Schema

### New Field Added
```sql
ALTER TABLE users ADD COLUMN profile_pic VARCHAR(500);
```

### Field Priority
The system uses a priority-based approach for profile pictures:
1. **`profile_pic`** - New field for profile pictures (highest priority)
2. **`profile_image`** - Existing field for backward compatibility
3. **Default Avatar** - Fallback to `/static/default-avatar.svg`

## 🔌 API Endpoints

### Upload Profile Picture
```
POST /api/upload-profile-picture
Content-Type: multipart/form-data
```

#### Request
- `profile_picture`: Image file (JPG, PNG, WebP, max 2MB)

#### Response
```json
{
  "success": true,
  "message": "Profile picture uploaded successfully",
  "file_url": "/static/uploads/profile_pictures/1234567890_uuid.jpg",
  "filename": "1234567890_uuid.jpg"
}
```

#### Error Responses
```json
{
  "success": false,
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

#### Error Codes
- `AUTH_REQUIRED` - User not authenticated
- `SESSION_EXPIRED` - Session expired
- `NO_FILE` - No file uploaded
- `FILE_TOO_LARGE` - File exceeds 2MB limit
- `INVALID_TYPE` - Unsupported file type
- `INVALID_EXTENSION` - Invalid file extension
- `STORAGE_ERROR` - File storage failed
- `DB_ERROR` - Database update failed
- `INTERNAL_ERROR` - Server error

## 🎨 Frontend Integration

### Basic Usage
```javascript
// Open the upload modal
profilePictureUpload.openModal();

// Listen for profile picture updates
document.addEventListener('profilePictureUpdated', function(event) {
    console.log('Profile picture updated:', event.detail.fileUrl);
    // Update your UI here
});
```

### HTML Integration
```html
<!-- Profile picture with data attribute -->
<img src="/static/default-avatar.svg" 
     alt="Profile" 
     data-profile-pic="{{ user.get_profile_pic_url() }}"
     class="profile-avatar">

<!-- Upload trigger button -->
<button onclick="profilePictureUpload.openModal()">
    <i class="fas fa-camera"></i> Update Profile Picture
</button>
```

### CSS Classes
The system automatically updates these CSS selectors:
- `.profile-avatar img`
- `.profile-pic`
- `[data-profile-pic]`

## 🔧 Configuration

### JavaScript Options
```javascript
const profilePictureUpload = new ProfilePictureUpload({
    uploadEndpoint: '/api/upload-profile-picture',
    maxFileSize: 2 * 1024 * 1024, // 2MB
    allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
    allowedExtensions: ['.jpg', '.jpeg', '.png', '.webp']
});
```

### File Storage
By default, files are stored in `/static/uploads/profile_pictures/`. To use cloud storage:

1. **Modify `save_profile_picture()` function in `app.py`**
2. **Update file URL generation**
3. **Implement cloud storage logic**

Example S3 integration:
```python
async def save_profile_picture(file, filename: str) -> dict:
    try:
        # Upload to S3
        s3_client.upload_fileobj(file, 'bucket-name', f'profile_pictures/{filename}')
        
        # Generate S3 URL
        file_url = f"https://bucket-name.s3.amazonaws.com/profile_pictures/{filename}"
        
        return {"success": True, "file_url": file_url, "message": "File saved to S3"}
    except Exception as e:
        return {"success": False, "message": f"Failed to save file: {str(e)}"}
```

## 🧪 Testing

### Test Page
Navigate to `/static/test-profile-picture.html` to test all features:

1. **Profile Display**: See multiple profile picture instances
2. **Upload Testing**: Test file validation and upload process
3. **Feature Demo**: Explore all system capabilities
4. **Integration Test**: Verify automatic updates across interface

### Manual Testing
1. **File Validation**: Try uploading invalid files (wrong type, too large)
2. **Authentication**: Test without login (should show auth error)
3. **UI Updates**: Verify all profile pictures update after upload
4. **Responsive Design**: Test on different screen sizes

## 🚀 Deployment

### Prerequisites
1. **Database Migration**: Add `profile_pic` column to users table
2. **Directory Creation**: Ensure upload directories exist
3. **Permissions**: Verify write permissions for upload directories

### Production Considerations
1. **File Cleanup**: Implement old file cleanup logic
2. **CDN Integration**: Use CDN for faster image delivery
3. **Monitoring**: Add upload metrics and error tracking
4. **Backup**: Regular backup of uploaded images

### Security Checklist
- [x] File type validation
- [x] File size limits
- [x] Secure filename generation
- [x] Authentication required
- [x] Input sanitization
- [x] Error message sanitization

## 🔄 Migration from Old System

The new system is backward compatible:

1. **Existing `profile_image` fields continue to work**
2. **New uploads use `profile_pic` field**
3. **Fallback logic ensures smooth transition**
4. **No data migration required**

## 🐛 Troubleshooting

### Common Issues

#### Upload Fails
- Check file size (must be under 2MB)
- Verify file type (JPG, PNG, WebP only)
- Ensure user is authenticated
- Check server logs for errors

#### Images Don't Update
- Verify JavaScript is loaded
- Check browser console for errors
- Ensure CSS selectors match
- Verify event listeners are attached

#### Modal Doesn't Open
- Check if `profilePictureUpload` is defined
- Verify JavaScript file is loaded
- Check for JavaScript errors in console

### Debug Mode
Enable debug logging in the browser console:
```javascript
// Check if system is loaded
console.log('Profile upload system:', typeof profilePictureUpload);

// Listen for all events
document.addEventListener('profilePictureUpdated', console.log);
```

## 📈 Performance

### Optimizations
- **Lazy Loading**: Images load only when needed
- **Efficient Updates**: DOM updates are batched
- **Minimal Dependencies**: Lightweight implementation
- **Caching**: Browser caching for uploaded images

### Monitoring
- **Upload Success Rate**: Track successful vs failed uploads
- **File Size Distribution**: Monitor average file sizes
- **User Engagement**: Track upload frequency
- **Error Rates**: Monitor validation and upload errors

## 🤝 Contributing

### Code Style
- **ES6+ JavaScript** with async/await
- **Modular CSS** with BEM methodology
- **Python PEP 8** compliance
- **Comprehensive comments** and documentation

### Testing
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test API endpoints
- **UI Tests**: Test user interactions
- **Cross-browser Testing**: Ensure compatibility

## 📄 License

This profile picture upload system is part of the Glow-IQ project and follows the same licensing terms.

## 🆘 Support

For issues or questions:
1. **Check this documentation**
2. **Review browser console for errors**
3. **Test with the provided test page**
4. **Check server logs for backend issues**

---

**Last Updated**: August 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
