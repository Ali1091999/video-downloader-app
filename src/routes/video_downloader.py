from flask import Blueprint, request, jsonify
import yt_dlp
import os
import tempfile
import re
import time
import random
from urllib.parse import urlparse
import logging

video_bp = Blueprint('video', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def get_enhanced_ydl_opts(platform='youtube'):
    """الحصول على إعدادات yt-dlp محسنة حسب المنصة"""
    
    # User agents متنوعة لتجنب الكشف
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    ]
    
    # قائمة بالبروكسيات (يمكن تحديثها بانتظام)
    proxies = [
        "http://42.118.74.84:16000",
        "http://113.160.132.195:8080", 
        "http://144.22.175.58:1080",
        "http://200.174.198.86:8888",
        "http://223.135.156.183:8080",
        "http://57.129.81.201:8080",
        "http://13.211.233.22:36619",
        "http://8.221.138.11:3129",
        "http://123.141.181.8:5031",
        "http://181.129.183.19:53281"
    ]

    def get_random_proxy():
        return random.choice(proxies) if proxies else None

        base_opts = {
            'quiet': False,  # تمكين الرسائل للتشخيص
            'no_warnings': False,
            'extract_flat': False,
            'user_agent': random.choice(user_agents),
            'referer': 'https://www.youtube.com/',
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'nocheckcertificate': True, # تجاهل أخطاء شهادة SSL
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }

    # إضافة البروكسي إذا كان متاحاً
    if get_random_proxy():
        base_opts['proxy'] = get_random_proxy()

    # إعدادات خاصة بـ YouTube
    if platform == 'youtube':
        youtube_opts = {
            'format': 'best[height<=720]/best',  # تحديد جودة معقولة
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],  # تخطي بعض التنسيقات المعقدة
                    'player_client': ['android', 'web'],  # استخدام عملاء متعددين
                }
            }
        }
        base_opts.update(youtube_opts)
    
    return base_opts

def extract_with_fallback(url, platform):
    """استخراج معلومات الفيديو مع آليات احتياطية متعددة"""
    
    # قائمة بالبروكسيات للاختبار
    proxies = [
        "http://42.118.74.84:16000",
        "http://113.160.132.195:8080", 
        "http://144.22.175.58:1080",
        "http://200.174.198.86:8888",
        "http://223.135.156.183:8080"
    ]
    
    # المحاولة الأولى: مع البروكسيات
    for i, proxy in enumerate(proxies[:3]):  # جرب أول 3 بروكسيات فقط
        try:
            logger.info(f"Attempting to extract {url} with proxy {proxy} (attempt {i+1})")
            ydl_opts = get_enhanced_ydl_opts(platform)
            ydl_opts['proxy'] = proxy
            ydl_opts['socket_timeout'] = 30  # مهلة زمنية أقصر
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info(f"Successfully extracted info for {url} using proxy {proxy}")
                return info, None
                
        except Exception as e:
            logger.warning(f"Proxy {proxy} failed for {url}: {str(e)}")
            continue
    
    # المحاولة الثانية: بدون بروكسي مع إعدادات محسنة
    try:
        logger.info(f"Attempting to extract {url} without proxy with enhanced settings")
        ydl_opts = get_enhanced_ydl_opts(platform)
        # إزالة البروكسي إذا كان موجوداً
        ydl_opts.pop('proxy', None)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            logger.info(f"Successfully extracted info for {url} without proxy")
            return info, None
            
    except Exception as e:
        logger.warning(f"Enhanced extraction without proxy failed for {url}: {str(e)}")
        
        # المحاولة الثالثة: إعدادات أساسية مع تأخير
        try:
            logger.info(f"Attempting basic extraction for {url} after delay")
            time.sleep(random.uniform(2, 5))  # تأخير عشوائي أطول
            
            basic_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'worst',  # جودة أقل قد تعمل بشكل أفضل
                'socket_timeout': 60,
                'retries': 5,
            }
            
            with yt_dlp.YoutubeDL(basic_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info(f"Basic extraction successful for {url}")
                return info, None
                
        except Exception as e2:
            logger.error(f"All extraction methods failed for {url}: {str(e2)}")
            return None, str(e2)

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
        logger.info(f"Processing {platform} URL: {url}")
        
        # استخراج المعلومات مع آليات احتياطية
        info, error = extract_with_fallback(url, platform)
        
        if info is None:
            # تحليل نوع الخطأ وإرجاع رسالة مناسبة
            if 'Private video' in error:
                return jsonify({'error': 'هذا الفيديو خاص ولا يمكن تحميله'}), 400
            elif 'Video unavailable' in error or 'content isn\'t available' in error.lower():
                return jsonify({'error': 'الفيديو غير متوفر أو محظور في هذه المنطقة'}), 400
            elif 'Sign in' in error:
                return jsonify({'error': 'هذا الفيديو يتطلب تسجيل دخول'}), 400
            elif 'age' in error.lower():
                return jsonify({'error': 'هذا الفيديو مقيد بالعمر'}), 400
            else:
                return jsonify({'error': f'خطأ في استخراج معلومات الفيديو: {error}'}), 500
        
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
            seen_qualities = set()
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none':  # فقط الفيديوهات
                    quality = fmt.get('height', 'غير محدد')
                    if quality not in seen_qualities:
                        format_info = {
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'quality': quality,
                            'filesize': fmt.get('filesize', 0),
                            'format_note': fmt.get('format_note', '')
                        }
                        video_info['formats'].append(format_info)
                        seen_qualities.add(quality)
        
        logger.info(f"Successfully processed {url}")
        return jsonify({'success': True, 'data': video_info})
        
    except Exception as e:
        logger.error(f"Unexpected error in get_video_info: {str(e)}")
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
        
        platform = get_platform_from_url(url)
        logger.info(f"Downloading {platform} video: {url}")
        
        # إنشاء مجلد مؤقت للتحميل
        temp_dir = tempfile.mkdtemp()
        
        # إعدادات yt-dlp للتحميل
        ydl_opts = get_enhanced_ydl_opts(platform)
        ydl_opts.update({
            'format': format_id,
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # تحميل الفيديو
                info = ydl.extract_info(url, download=True)
                
                # البحث عن الملف المحمل
                downloaded_files = os.listdir(temp_dir)
                if not downloaded_files:
                    return jsonify({'error': 'فشل في تحميل الفيديو'}), 500
                
                downloaded_file = downloaded_files[0]
                file_path = os.path.join(temp_dir, downloaded_file)
                file_size = os.path.getsize(file_path)
                
                logger.info(f"Successfully downloaded {url}")
                return jsonify({
                    'success': True,
                    'message': 'تم تحميل الفيديو بنجاح',
                    'filename': downloaded_file,
                    'filesize': file_size,
                    'download_path': file_path
                })
                
        except Exception as e:
            logger.error(f"Download failed for {url}: {str(e)}")
            return jsonify({'error': f'خطأ في تحميل الفيديو: {str(e)}'}), 500
                
    except Exception as e:
        logger.error(f"Unexpected error in download_video: {str(e)}")
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

@video_bp.route('/debug-info', methods=['POST'])
def debug_video_info():
    """نقطة نهاية للتشخيص مع معلومات مفصلة"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400
        
        platform = get_platform_from_url(url)
        
        # إعدادات مفصلة للتشخيص
        debug_opts = {
            'quiet': False,
            'verbose': True,
            'extract_flat': False,
            'dump_single_json': False,
            'no_warnings': False,
        }
        
        debug_info = {
            'url': url,
            'platform': platform,
            'yt_dlp_version': yt_dlp.version.__version__,
            'extraction_log': []
        }
        
        try:
            with yt_dlp.YoutubeDL(debug_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                debug_info['success'] = True
                debug_info['title'] = info.get('title', 'غير متوفر')
                debug_info['available_formats'] = len(info.get('formats', []))
                
        except Exception as e:
            debug_info['success'] = False
            debug_info['error'] = str(e)
            debug_info['error_type'] = type(e).__name__
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': f'خطأ في التشخيص: {str(e)}'}), 500


