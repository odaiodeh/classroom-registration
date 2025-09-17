# نشر التطبيق على Amazon EC2
# Deploy to Amazon EC2

## 🚀 خطوات النشر على AWS

### 1. إنشاء خادم EC2

1. **سجل دخول إلى AWS Console**
   - اذهب إلى [AWS Console](https://aws.amazon.com/console/)
   - سجل دخول أو أنشئ حساب جديد

2. **أنشئ EC2 Instance**
   ```
   - اختر "EC2" من الخدمات
   - انقر "Launch Instance"
   - اختر "Ubuntu Server 22.04 LTS"
   - Instance Type: t2.micro (مجاني)
   - Storage: 8GB (افتراضي)
   ```

3. **إعدادات الأمان (Security Group)**
   ```
   - SSH: Port 22 (من عنوان IP الخاص بك)
   - HTTP: Port 80 (من أي مكان)
   - Custom: Port 5002 (من أي مكان) - للتطبيق
   ```

4. **إنشاء Key Pair**
   - أنشئ مفتاح جديد وحمله (.pem file)
   - احفظه في مكان آمن

### 2. الاتصال بالخادم

```bash
# غير الصلاحيات للمفتاح
chmod 400 your-key.pem

# اتصل بالخادم
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 3. تثبيت المتطلبات على الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3 python3-pip python3-venv git -y

# تثبيت nginx (اختياري للإنتاج)
sudo apt install nginx -y
```

### 4. رفع التطبيق للخادم

**الطريقة الأولى: Git (الأفضل)**
```bash
# إنشاء مجلد للتطبيق
mkdir ~/school-app
cd ~/school-app

# استنساخ المشروع (إذا كان على GitHub)
git clone YOUR_GITHUB_REPO .

# أو ارفع الملفات يدوياً باستخدام scp
```

**الطريقة الثانية: رفع مباشر**
```bash
# من جهازك المحلي، ارفع الملفات
scp -i your-key.pem -r /path/to/your/classes ubuntu@YOUR_EC2_IP:~/school-app/
```

### 5. إعداد التطبيق على الخادم

```bash
# الانتقال لمجلد التطبيق
cd ~/school-app

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# تعيين متغير البيئة للرابط العام
export PUBLIC_URL="http://YOUR_EC2_PUBLIC_IP:5002"

# تشغيل التطبيق
python app.py
```

### 6. تشغيل التطبيق كخدمة (للإنتاج)

**إنشاء ملف خدمة systemd:**

```bash
sudo nano /etc/systemd/system/school-app.service
```

**محتوى الملف:**
```ini
[Unit]
Description=School Registration App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/school-app
Environment=PATH=/home/ubuntu/school-app/venv/bin
Environment=PUBLIC_URL=http://YOUR_EC2_PUBLIC_IP:5002
ExecStart=/home/ubuntu/school-app/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**تفعيل الخدمة:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable school-app
sudo systemctl start school-app
sudo systemctl status school-app
```

### 7. إعداد Nginx (اختياري - للإنتاج)

```bash
sudo nano /etc/nginx/sites-available/school-app
```

**محتوى الملف:**
```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**تفعيل الإعداد:**
```bash
sudo ln -s /etc/nginx/sites-available/school-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🌐 الوصول للتطبيق

بعد النشر، سيكون التطبيق متاحاً على:

- **مباشرة:** `http://YOUR_EC2_PUBLIC_IP:5002`
- **عبر Nginx:** `http://YOUR_EC2_PUBLIC_IP`

## 📱 QR Code

QR Code سيعرض الآن:
- `http://YOUR_EC2_PUBLIC_IP:5002/register` (مباشرة)
- أو `http://YOUR_EC2_PUBLIC_IP/register` (عبر Nginx)

## 🔧 تحديث التطبيق

```bash
# الاتصال بالخادم
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# تحديث الكود
cd ~/school-app
git pull  # إذا كنت تستخدم Git

# إعادة تشغيل الخدمة
sudo systemctl restart school-app
```

## 💰 تكلفة AWS

- **t2.micro**: مجاني لمدة سنة (للحسابات الجديدة)
- **بعد السنة**: حوالي $10/شهر
- **البيانات**: مجانية للاستخدام المحدود

## 🔒 نصائح الأمان

1. **غير كلمة المرور الافتراضية** في التطبيق
2. **استخدم HTTPS** في الإنتاج
3. **احدث النظام** بانتظام
4. **راقب الوصول** للخادم

## 🆘 حل المشاكل

**إذا لم يعمل التطبيق:**
```bash
# تحقق من حالة الخدمة
sudo systemctl status school-app

# تحقق من السجلات
sudo journalctl -u school-app -f

# تحقق من البورت
sudo netstat -tlnp | grep 5002
```

**إذا لم يعمل QR Code:**
```bash
# تأكد من تعيين PUBLIC_URL
echo $PUBLIC_URL

# أو عينه يدوياً
export PUBLIC_URL="http://YOUR_EC2_PUBLIC_IP:5002"
```
