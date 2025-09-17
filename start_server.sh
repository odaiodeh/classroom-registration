#!/bin/bash

# بدء تشغيل خادم المدرسة
# Start School Server Script

echo "🚀 بدء تشغيل خادم المدرسة الجماهيرية..."
echo "🚀 Starting School Registration Server..."

# تحديد الرابط العام إذا لم يكن معين
if [ -z "$PUBLIC_URL" ]; then
    # محاولة الحصول على IP العام للـ EC2
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
    
    if [ ! -z "$PUBLIC_IP" ]; then
        export PUBLIC_URL="http://$PUBLIC_IP:5002"
        echo "✅ تم تحديد الرابط العام: $PUBLIC_URL"
    else
        echo "⚠️  لم يتم العثور على IP عام، سيتم استخدام الرابط المحلي"
    fi
fi

# التأكد من وجود البيئة الافتراضية
if [ ! -d "venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
pip install -r requirements.txt

# إنشاء مجلد logs إذا لم يكن موجود
mkdir -p logs

# بدء التطبيق
echo "🌟 بدء تشغيل التطبيق..."
echo "📱 الرابط: ${PUBLIC_URL:-http://localhost:5002}"
echo "📱 QR Code: ${PUBLIC_URL:-http://localhost:5002}/qr_code"
echo ""
echo "اضغط Ctrl+C لإيقاف الخادم"
echo "Press Ctrl+C to stop the server"
echo ""

# تشغيل التطبيق مع تسجيل الأخطاء
python app.py 2>&1 | tee logs/app.log
