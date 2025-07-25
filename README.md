# 📹 برنامج تحميل الفيديوهات - Video Downloader

## نظرة عامة

برنامج تحميل الفيديوهات هو أداة ويب مجانية وسريعة تتيح للمستخدمين تحميل الفيديوهات من المنصات الشائعة مثل YouTube و Instagram و Facebook. يتميز البرنامج بواجهة مستخدم عربية جذابة ومتجاوبة مع جميع الأجهزة.

## المميزات الرئيسية

### 🎯 المنصات المدعومة
- **YouTube**: فيديوهات عادية، قوائم التشغيل، البث المباشر
- **Instagram**: فيديوهات المنشورات، ريلز (Reels)، IGTV، القصص
- **Facebook**: فيديوهات عامة، فيديوهات الصفحات، البث المباشر

### 🎨 واجهة المستخدم
- تصميم عربي متجاوب (RTL)
- واجهة حديثة وجذابة
- متوافق مع جميع الأجهزة (موبايل، تابلت، كمبيوتر)
- تأثيرات بصرية متقدمة وانتقالات سلسة

### ⚡ الأداء والجودة
- معاينة الفيديو قبل التحميل
- جودات متعددة (144p إلى 4K)
- صيغ مختلفة (MP4, WEBM, 3GP)
- تحميل سريع وآمن

### 🔧 التقنيات المستخدمة
- **Backend**: Python Flask + yt-dlp
- **Frontend**: HTML5, CSS3, JavaScript
- **التصميم**: Responsive Design, CSS Grid, Flexbox
- **الأمان**: CORS enabled, Input validation

## متطلبات التشغيل

### متطلبات النظام
- Python 3.11 أو أحدث
- نظام التشغيل: Windows, macOS, Linux
- ذاكرة: 512MB RAM كحد أدنى
- مساحة القرص: 100MB

### المكتبات المطلوبة
```
Flask==3.1.1
flask-cors==6.0.0
yt-dlp==2025.6.30
SQLAlchemy==2.0.36
```

## طريقة التثبيت والتشغيل

### 1. تحميل المشروع
```bash
git clone [repository-url]
cd video_downloader
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate     # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. تشغيل الخادم
```bash
python src/main.py
```

### 5. فتح البرنامج
افتح المتصفح وانتقل إلى: `http://localhost:5000`

## طريقة الاستخدام

### 1. إدخال الرابط
- انسخ رابط الفيديو من YouTube أو Instagram أو Facebook
- الصق الرابط في حقل الإدخال

### 2. معاينة الفيديو
- اضغط على زر "معاينة الفيديو"
- انتظر حتى يتم تحليل الفيديو
- ستظهر معلومات الفيديو والجودات المتاحة

### 3. اختيار الجودة والتحميل
- اختر الجودة المناسبة من القائمة
- اضغط على زر "تحميل الفيديو"
- انتظر حتى يكتمل التحميل

## هيكل المشروع

```
video_downloader/
├── src/
│   ├── main.py                 # نقطة دخول التطبيق
│   ├── routes/
│   │   ├── user.py            # مسارات المستخدم
│   │   └── video_downloader.py # مسارات تحميل الفيديو
│   ├── models/
│   │   └── user.py            # نماذج قاعدة البيانات
│   ├── static/
│   │   └── index.html         # الواجهة الأمامية
│   └── database/
│       └── app.db             # قاعدة البيانات
├── venv/                      # البيئة الافتراضية
├── requirements.txt           # متطلبات Python
└── README.md                  # هذا الملف
```

## واجهات برمجة التطبيقات (API)

### 1. الحصول على معلومات الفيديو
```
POST /api/video-info
Content-Type: application/json

{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**الاستجابة:**
```json
{
    "success": true,
    "data": {
        "title": "عنوان الفيديو",
        "duration": 180,
        "thumbnail": "رابط الصورة المصغرة",
        "uploader": "اسم الناشر",
        "view_count": 1000000,
        "platform": "youtube",
        "formats": [...]
    }
}
```

### 2. تحميل الفيديو
```
POST /api/download
Content-Type: application/json

{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "format_id": "best"
}
```

### 3. المواقع المدعومة
```
GET /api/supported-sites
```

## الأمان والخصوصية

### إجراءات الأمان
- التحقق من صحة الروابط المدخلة
- حماية من هجمات CSRF
- تشفير الاتصالات (HTTPS في الإنتاج)
- تنظيف المدخلات من الأكواد الضارة

### الخصوصية
- لا يتم حفظ الروابط أو الفيديوهات على الخادم
- لا يتم جمع بيانات شخصية
- الملفات المؤقتة يتم حذفها تلقائياً

## استكشاف الأخطاء وإصلاحها

### مشاكل شائعة وحلولها

#### 1. خطأ "الفيديو غير متوفر"
- تأكد من أن الرابط صحيح وعام
- تحقق من أن الفيديو لم يتم حذفه
- جرب رابط فيديو آخر

#### 2. خطأ "المنصة غير مدعومة"
- تأكد من أن الرابط من YouTube أو Instagram أو Facebook
- تحقق من صيغة الرابط

#### 3. بطء في التحميل
- تحقق من سرعة الإنترنت
- جرب جودة أقل
- أعد تشغيل الخادم

#### 4. خطأ في تثبيت المتطلبات
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## التطوير والمساهمة

### إضافة منصة جديدة
1. تحديث دالة `get_platform_from_url()` في `video_downloader.py`
2. إضافة معالجة خاصة إذا لزم الأمر
3. تحديث قائمة المواقع المدعومة في الواجهة

### تحسين الواجهة
1. تعديل ملف `index.html` في مجلد `static`
2. إضافة CSS جديد أو تعديل الموجود
3. تحديث JavaScript للوظائف الجديدة

### إضافة ميزات جديدة
1. إنشاء مسار جديد في مجلد `routes`
2. تحديث `main.py` لتسجيل المسار الجديد
3. تحديث الواجهة الأمامية حسب الحاجة

## النشر والاستضافة

### النشر المحلي
```bash
python src/main.py
```

### النشر على خادم
1. استخدم خادم WSGI مثل Gunicorn
2. قم بإعداد خادم ويب مثل Nginx
3. استخدم HTTPS للأمان

### النشر السحابي
- **Heroku**: سهل ومجاني للمشاريع الصغيرة
- **AWS**: مرن وقابل للتوسع
- **Google Cloud**: أداء عالي
- **DigitalOcean**: بسيط وبأسعار معقولة

## الترخيص والقانونية

### حقوق النشر
- احترم حقوق النشر للفيديوهات
- استخدم البرنامج للاستخدام الشخصي فقط
- لا تعيد توزيع المحتوى المحمي بحقوق النشر

### إخلاء المسؤولية
هذا البرنامج مخصص للأغراض التعليمية والاستخدام الشخصي فقط. المطورون غير مسؤولين عن أي استخدام غير قانوني للبرنامج.

## الدعم والمساعدة

### الحصول على المساعدة
- راجع قسم استكشاف الأخطاء أولاً
- تحقق من أن جميع المتطلبات مثبتة بشكل صحيح
- تأكد من أن الخادم يعمل على المنفذ الصحيح

### الإبلاغ عن الأخطاء
عند الإبلاغ عن خطأ، يرجى تضمين:
- نظام التشغيل المستخدم
- إصدار Python
- رسالة الخطأ الكاملة
- خطوات إعادة إنتاج المشكلة

## التحديثات المستقبلية

### ميزات مخططة
- [ ] دعم منصات إضافية (TikTok, Twitter)
- [ ] تحميل متعدد الملفات
- [ ] واجهة إدارة للتحميلات
- [ ] دعم قوائم التشغيل الطويلة
- [ ] تحسين الأداء والسرعة

### تحسينات تقنية
- [ ] إضافة نظام تخزين مؤقت
- [ ] تحسين معالجة الأخطاء
- [ ] إضافة اختبارات تلقائية
- [ ] تحسين الأمان
- [ ] دعم قواعد بيانات متقدمة

---

**تم تطوير هذا البرنامج بواسطة Manus AI**

للمزيد من المعلومات أو الدعم التقني، يرجى مراجعة الوثائق أو الاتصال بفريق التطوير.

**تاريخ آخر تحديث**: يوليو 2025
**الإصدار**: 1.0.0

