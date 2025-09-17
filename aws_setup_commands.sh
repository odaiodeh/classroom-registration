#!/bin/bash

# أوامر إعداد AWS EC2 للمدرسة الجماهيرية
# AWS EC2 Setup Commands for School Registration App

echo "🌟 بدء إعداد خادم المدرسة على AWS EC2"
echo "🌟 Starting School Server Setup on AWS EC2"

# الخطوة 1: تحديث النظام
echo "📦 تحديث النظام..."
sudo apt update && sudo apt upgrade -y

# الخطوة 2: تثبيت المتطلبات الأساسية
echo "🔧 تثبيت المتطلبات الأساسية..."
sudo apt install -y python3 python3-pip python3-venv git nginx curl wget htop

# الخطوة 3: إنشاء مستخدم التطبيق (اختياري)
echo "👤 إعداد مجلد التطبيق..."
cd ~
mkdir -p school-app
cd school-app

# الخطوة 4: رفع ملفات التطبيق
echo "📂 نسخ ملفات التطبيق..."
echo "⚠️  يجب رفع ملفات التطبيق إلى هذا المجلد: $(pwd)"
echo "⚠️  استخدم: scp -i your-key.pem -r /path/to/classes ubuntu@YOUR_EC2_IP:~/school-app/"

# الخطوة 5: إعداد البيئة الافتراضية (سيتم تنفيذها بعد رفع الملفات)
cat << 'EOF' > setup_app.sh
#!/bin/bash
echo "🐍 إنشاء البيئة الافتراضية..."
python3 -m venv venv
source venv/bin/activate

echo "📥 تثبيت متطلبات Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔒 إعداد الصلاحيات..."
chmod +x start_server.sh

# الحصول على IP العام
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "🌐 IP العام: $PUBLIC_IP"

# إعداد متغير البيئة
echo "export PUBLIC_URL=http://$PUBLIC_IP:5002" >> ~/.bashrc
echo "تم إعداد البيئة بنجاح!"
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 لتشغيل التطبيق:"
echo "   ./start_server.sh"
echo ""
echo "🌐 الروابط:"
echo "   التطبيق: http://$PUBLIC_IP:5002"
echo "   التسجيل: http://$PUBLIC_IP:5002/register"
echo "   QR Code: http://$PUBLIC_IP:5002/qr_code"
EOF

chmod +x setup_app.sh

# الخطوة 6: إعداد جدار الحماية
echo "🔥 إعداد جدار الحماية..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 5002
sudo ufw --force enable

# الخطوة 7: إعداد خدمة systemd
echo "⚙️  إعداد خدمة النظام..."
cat << 'EOF' > school-app.service
[Unit]
Description=School Registration App - المدرسة الجماهيرية بئر الأمير
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/school-app
Environment=PATH=/home/ubuntu/school-app/venv/bin
ExecStart=/home/ubuntu/school-app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# الخطوة 8: معلومات الخطوات التالية
echo ""
echo "✅ تم إكمال الإعداد الأولي!"
echo "📋 الخطوات التالية:"
echo "1. ارفع ملفات التطبيق إلى: ~/school-app/"
echo "2. نفذ: ./setup_app.sh"
echo "3. نفذ: ./start_server.sh"
echo ""
echo "🔧 لتثبيت كخدمة نظام:"
echo "sudo cp school-app.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable school-app"
echo "sudo systemctl start school-app"
echo ""
echo "📱 تحقق من IP العام:"
curl -s http://169.254.169.254/latest/meta-data/public-ipv4
echo ""
