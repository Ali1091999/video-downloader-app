from flask import Blueprint, request, jsonify
import yt_dlp
import os
import tempfile
import re
from urllib.parse import urlparse

video_bp = Blueprint('video', __name__)

def is_valid_url(url):
    """التحقق من صحة الرابط"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_platform_from_url(url):
    """تحديد المنصة من الرابط"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    else:
        return 'unknown'

@video_bp.route('/video-info', methods=['POST'])
def get_video_info():
    """الحصول على معلومات الفيديو دون تحميله"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400
        
        if not is_valid_url(url):
            return jsonify({'error': 'الرابط غير صحيح'}), 400
        
        platform = get_platform_from_url(url)
        
        # إعدادات yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # استخراج المعلومات المهمة
                video_info = {
                    'title': info.get('title', 'غير متوفر'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'غير متوفر'),
                    'view_count': info.get('view_count', 0),
                    'platform': platform,
                    'formats': []
                }
                
                # استخراج الصيغ المتاحة
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none':  # فقط الفيديوهات
                            format_info = {
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext'),
                                'quality': fmt.get('height', 'غير محدد'),
                                'filesize': fmt.get('filesize', 0),
                                'format_note': fmt.get('format_note', '')
                            }
                            video_info['formats'].append(format_info)
                
                return jsonify({'success': True, 'data': video_info})
                
            except Exception as e:
                error_msg = str(e)
                if 'Private video' in error_msg:
                    return jsonify({'error': 'هذا الفيديو خاص ولا يمكن تحميله'}), 400
                elif 'Video unavailable' in error_msg:
                    return jsonify({'error': 'الفيديو غير متوفر'}), 400
                elif 'not supported' in error_msg.lower():
                    return jsonify({'error': 'هذه المنصة غير مدعومة حالياً'}), 400
                else:
                    return jsonify({'error': f'خطأ في استخراج معلومات الفيديو: {error_msg}'}), 500
                    
    except Exception as e:
        return jsonify({'error': f'خطأ في الخادم: {str(e)}'}), 500

@video_bp.route('/download', methods=['POST'])
def download_video():
    """تحميل الفيديو"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400
        
        if not is_valid_url(url):
            return jsonify({'error': 'الرابط غير صحيح'}), 400
        
        # إنشاء مجلد مؤقت للتحميل
        temp_dir = tempfile.mkdtemp()
        
        # إعدادات yt-dlp للتحميل
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # تحميل الفيديو
                info = ydl.extract_info(url, download=True)
                
                # البحث عن الملف المحمل
                downloaded_files = os.listdir(temp_dir)
                if not downloaded_files:
                    return jsonify({'error': 'فشل في تحميل الفيديو'}), 500
                
                downloaded_file = downloaded_files[0]
                file_path = os.path.join(temp_dir, downloaded_file)
                file_size = os.path.getsize(file_path)
                
                return jsonify({
                    'success': True,
                    'message': 'تم تحميل الفيديو بنجاح',
                    'filename': downloaded_file,
                    'filesize': file_size,
                    'download_path': file_path
                })
                
            except Exception as e:
                return jsonify({'error': f'خطأ في تحميل الفيديو: {str(e)}'}), 500
                
    except Exception as e:
        return jsonify({'error': f'خطأ في الخادم: {str(e)}'}), 500

@video_bp.route('/supported-sites', methods=['GET'])
def get_supported_sites():
    """الحصول على قائمة المواقع المدعومة"""
    supported_sites = [
        {
            'name': 'YouTube',
            'domains': ['youtube.com', 'youtu.be'],
            'features': ['فيديوهات عادية', 'قوائم تشغيل', 'بث مباشر']
        },
        {
            'name': 'Instagram',
            'domains': ['instagram.com'],
            'features': ['فيديوهات', 'ريلز', 'IGTV', 'قصص']
        },
        {
            'name': 'Facebook',
            'domains': ['facebook.com', 'fb.watch'],
            'features': ['فيديوهات عامة', 'فيديوهات الصفحات']
        }
    ]
    
    return jsonify({'success': True, 'sites': supported_sites})

