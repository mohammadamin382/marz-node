"""
Multilingual text content for the bot
"""

TEXTS = {
    'en': {
        # Start and language selection
        'welcome': "🎉 Hey there! Welcome to your awesome Marzban Node Manager! 🚀\n\nI'm here to make managing your nodes super easy and fun! 😊",
        'select_language': "🌍 First things first - which language would you like to chat in?",
        'language_selected': "🎯 Perfect! We're all set with English now!",

        # Main menu
        'main_menu': "🏠 What would you like to do today?",
        'main_menu_desc': "Pick whatever you need - I'm here to help! 😄",
        'add_panel': "➕ Add New Panel",
        'manage_nodes': "🔧 Manage My Nodes",
        'admin_panel': "👑 Admin Stuff",
        'backup_data': "💾 Backup Everything",
        'statistics': "📊 Show Me Stats",

        # Panel management
        'panel_type': "Cool! What kind of panel are we adding today?",
        'marzban_panel': "🚀 Marzban Panel",
        'enter_panel_url': "Awesome! Now just paste your panel URL here (no need for /dashboard or anything extra):",
        'enter_username': "Great! What's the admin username? (Make sure it has sudo powers! 💪):",
        'enter_password': "Perfect! And the password please:",
        'enter_panel_name': "Nice! Give this panel a cool name so we can remember it:",
        'panel_saved': "🎉 Boom! Your panel is saved and ready to rock!",
        'panel_connection_failed': "😅 Oops! Couldn't connect to that panel. Double-check those details for me?",

        # Node management
        'select_panel': "Which panel should we work with today?",
        'no_panels': "🤔 Looks like you haven't added any panels yet. Let's fix that!",
        'node_management': "🔧 Node Management Center",
        'list_nodes': "📋 Show All Nodes",
        'get_node_info': "ℹ️ Node Details",
        'add_new_node': "➕ Add Fresh Node",
        'nodes_list': "📋 Here are your nodes",
        'no_nodes': "🤷‍♂️ No nodes found yet. Ready to create some?",
        'node_info': "ℹ️ Node Information",
        'reconnect_node': "🔄 Reconnect",
        'delete_node': "🗑️ Remove",
        'update_node': "🔄 Refresh Info",
        'back': "⬅️ Go Back",

        # Node installation
        'install_type': "How do you want to install this node?",
        'single_install': "🖥️ Just One Server",
        'bulk_install': "📦 Multiple Servers",
        'enter_ssh_ip': "What's the server IP address?",
        'enter_ssh_port': "SSH port? (22 is the usual, but you tell me!):",
        'enter_ssh_username': "Username for SSH access:",
        'auth_method': "How should I log in?",
        'password_auth': "🔒 With Password",
        'ssh_key_auth': "🔑 SSH Key",
        'enter_ssh_password': "SSH password please:",
        'enter_ssh_key': "🔑 Now send your SSH private key:\n\n💡 Note: Make sure to send the PRIVATE key, not the public one!\n📝 You can upload the file or copy-paste the text",
        'port_config': "Port setup time!",
        'custom_ports': "⚙️ I'll Choose Ports",
        'random_ports': "🎲 Surprise Me!",
        'enter_node_port': "Node port number:",
        'enter_api_port': "API port number:",
        'enter_node_name': "What should we call this node?",
        'random_name': "🎲 Pick Random Name",
        'installing_node': "🚀 Installing your node now... Grab some coffee! ☕",
        'node_installed': "🎉 Woohoo! Your node is up and running!",
        'installation_failed': "😔 Something went wrong: {error}\n\nDon't worry, we can try again!",

        # Admin features
        'admin_only': "🚫 Hey! This is admin-only territory. Nice try though! 😉",
        'not_sudo': "🔒 You'll need sudo powers for this one, my friend!",
        'backup_created': "💾 Backup complete! Everything's safe and sound!",
        'stats_title': "📊 Here's what's happening",
        'total_panels': "Panels: {count}",
        'total_nodes': "Nodes: {count}",
        'active_sessions': "Active users: {count}",

        # Errors
        'error_occurred': "😅 Oops! Something hiccupped: {error}",
        'invalid_url': "🤔 That URL doesn't look right to me...",
        'connection_timeout': "⏰ Taking too long to connect. Let's try again?",
        'authentication_failed': "🔑 Login didn't work. Check those credentials?",
        'node_not_found': "🔍 Can't find that node anywhere...",
        'operation_cancelled': "✋ No worries, operation cancelled!",

        # Success messages
        'operation_successful': "✅ Perfect! Everything went smoothly!",
        'node_reconnected': "🔄 Node is back online and happy!",
        'node_deleted': "🗑️ Node successfully deleted!",
        'node_updated': "🔄 Node information updated!",

        # SSH validation
        'invalid_ssh_key_format': "❌ Invalid key format! Key should start with -----BEGIN",
        'testing_ssh_connection': "🔄 Testing SSH connection...",
        'ssh_test_success': "✅ Yay! SSH connection successful!",
        'ssh_test_failed': "❌ SSH connection failed: {error}",
    },

    'fa': {
        # Start and language selection
        'welcome': "🎉 سلام دوست عزیز! به منیجر فوق‌العاده نودهای مرزبان خوش اومدی! 🚀\n\nاینجام تا مدیریت نودهات رو خیلی راحت و لذت‌بخش کنم! 😊",
        'select_language': "🌍 اول از همه بگو چه زبونی دوست داری باهاش حرف بزنیم؟",
        'language_selected': "🎯 عالی! حالا همه چیز فارسیه!",

        # Main menu
        'main_menu': "🏠 امروز چیکار می‌خوای بکنیم؟",
        'main_menu_desc': "هر چی نیاز داری انتخاب کن - اینجام کمکت کنم! 😄",
        'add_panel': "➕ پنل جدید اضافه کن",
        'manage_nodes': "🔧 نودهام رو مدیریت کن",
        'admin_panel': "👑 بخش ادمین",
        'backup_data': "💾 همه چیز رو بک‌آپ کن",
        'statistics': "📊 آمارها رو نشونم بده",

        # Panel management
        'panel_type': "چه نوع پنلی می‌خوای اضافه کنی؟",
        'marzban_panel': "🚀 پنل مرزبان",
        'enter_panel_url': "فوق‌العاده! حالا لینک پنلت رو بفرست (بدون /dashboard یا چیز اضافی):",
        'enter_username': "عالی! یوزرنیم ادمین چیه؟ (مطمئن شو sudo داشته باشه! 💪):",
        'enter_password': "خوبه! حالا پسوردش رو بده:",
        'enter_panel_name': "قشنگ! یه اسم خفن برای این پنل انتخاب کن:",
        'panel_saved': "🎉 باریکلا! پنلت ذخیره شد و آماده کاره!",
        'panel_connection_failed': "😅 اوه! نتونستم به پنل وصل شم. یه بار دیگه اطلاعات رو چک کن؟",

        # Node management
        'select_panel': "با کدوم پنل کار کنیم؟",
        'no_panels': "🤔 هنوز پنلی نساختی! بیا یکی بسازیم!",
        'node_management': "🔧 مرکز کنترل نودها",
        'list_nodes': "📋 همه نودها رو نشون بده",
        'get_node_info': "ℹ️ جزئیات نود",
        'add_new_node': "➕ نود تازه اضافه کن",
        'nodes_list': "📋 اینا نودهای تو هستن",
        'no_nodes': "🤷‍♂️ هنوز نودی نیست. می‌خوای بسازیم؟",
        'node_info': "ℹ️ اطلاعات نود",
        'reconnect_node': "🔄 دوباره وصل کن",
        'delete_node': "🗑️ حذف کن",
        'update_node': "🔄 اطلاعات رو بروز کن",
        'back': "⬅️ برگرد",

        # Node installation
        'install_type': "چطوری می‌خوای نود رو نصب کنی؟",
        'single_install': "🖥️ فقط یه سرور",
        'bulk_install': "📦 چندتا سرور",
        'enter_ssh_ip': "آی‌پی سرور چیه؟",
        'enter_ssh_port': "پورت SSH؟ (معمولاً 22 هست، ولی تو بگو!):",
        'enter_ssh_username': "یوزرنیم SSH:",
        'auth_method': "چطوری لاگین کنم؟",
        'password_auth': "🔒 با پسورد",
        'ssh_key_auth': "🔑 با کلید SSH",
        'enter_ssh_password': "پسورد SSH رو بده:",
        'enter_ssh_key': "🔑 حالا کلید خصوصی SSH رو بفرست (Private Key):\n\n💡 نکته: حتماً کلید خصوصی رو بفرست, نه عمومی!\n📝 می‌تونی فایل رو آپلود کنی یا متنش رو کپی کنی",
        'port_config': "حالا پورت‌ها رو تنظیم کنیم!",
        'custom_ports': "⚙️ خودم پورت انتخاب می‌کنم",
        'random_ports': "🎲 هر چی شد!",
        'enter_node_port': "پورت نود:",
        'enter_api_port': "پورت API:",
        'enter_node_name': "چه اسمی براش بذاریم؟",
        'random_name': "🎲 اسم تصادفی انتخاب کن",
        'installing_node': "🚀 دارم نودت رو نصب می‌کنم... یه چایی بخور! ☕",
        'node_installed': "🎉 یول! نودت آماده و کار می‌کنه!",
        'installation_failed': "😔 مشکلی پیش اومد: {error}\n\nنگران نباش، دوباره امتحان می‌کنیم!",

        # Admin features
        'admin_only': "🚫 داداش اینجا فقط واسه ادمین‌هاست! خوب بود ولی! 😉",
        'not_sudo': "🔒 برای این کار باید sudo داشته باشی دوست من!",
        'backup_created': "💾 بک‌آپ کامل شد! همه چیز امنه!",
        'stats_title': "📊 اینا چیزایی هست که داری",
        'total_panels': "پنل‌ها: {count}",
        'total_nodes': "نودها: {count}",
        'active_sessions': "کاربرای آنلاین: {count}",

        # Errors
        'error_occurred': "😅 اوپس! یه چیزی خراب شد: {error}",
        'invalid_url': "🤔 این لینک یکم عجیبه...",
        'connection_timeout': "⏰ خیلی طول کشید. دوباره امتحان کنیم؟",
        'authentication_failed': "🔑 لاگین نشد. اطلاعات رو چک کن؟",
        'node_not_found': "🔍 این نود رو پیدا نکردم...",
        'operation_cancelled': "✋ مشکلی نیست، کنسل شد!",

        # Success messages
        'operation_successful': "✅ عالی! همه چیز درست انجام شد!",
        'node_reconnected': "🔄 نود دوباره آنلاین شد و خوشحاله!",
        'node_deleted': "🗑️ نود با موفقیت حذف شد!",
        'node_updated': "🔄 اطلاعات نود به‌روزرسانی شد!",

        # SSH validation
        'invalid_ssh_key_format': "❌ فرمت کلید اشتباه! کلید باید با -----BEGIN شروع بشه",
        'testing_ssh_connection': "🔄 دارم اتصال SSH رو تست می‌کنم...",
        'ssh_test_success': "✅ یه‌هو! اتصال SSH موفق بود!",
        'ssh_test_failed': "❌ اتصال SSH ناموفق: {error}",
    },

    'ru': {
        # Start and language selection
        'welcome': "🎉 Привет, дружище! Добро пожаловать в супер-менеджер узлов Marzban! 🚀\n\nЯ здесь, чтобы сделать управление узлами легким и приятным! 😊",
        'select_language': "🌍 Для начала - на каком языке будем общаться?",
        'language_selected': "🎯 Отлично! Теперь говорим по-русски!",

        # Main menu
        'main_menu': "🏠 Что делаем сегодня?",
        'main_menu_desc': "Выбирай что нужно - я тут, чтобы помочь! 😄",
        'add_panel': "➕ Добавить панель",
        'manage_nodes': "🔧 Управлять узлами",
        'admin_panel': "👑 Админка",
        'backup_data': "💾 Бэкап всего",
        'statistics': "📊 Показать статистику",

        # Panel management
        'panel_type': "Классно! Какую панель добавляем?",
        'marzban_panel': "🚀 Панель Marzban",
        'enter_panel_url': "Супер! Скинь URL панели (без /dashboard и прочего):",
        'enter_username': "Отлично! Какой админский логин? (нужны права sudo! 💪):",
        'enter_password': "Прекрасно! А теперь пароль:",
        'enter_panel_name': "Круто! Придумай крутое имя для панели:",
        'panel_saved': "🎉 Бум! Панель сохранена и готова к работе!",
        'panel_connection_failed': "😅 Упс! Не смог подключиться. Проверь данные?",

        # Node management
        'select_panel': "С какой панелью работаем?",
        'no_panels': "🤔 Панелей пока нет. Давай это исправим!",
        'node_management': "🔧 Центр управления узлами",
        'list_nodes': "📋 Показать все узлы",
        'get_node_info': "ℹ️ Детали узла",
        'add_new_node': "➕ Добавить новый узел",
        'nodes_list': "📋 Вот твои узлы",
        'no_nodes': "🤷‍♂️ Узлов пока нет. Создаем?",
        'node_info': "ℹ️ Информация об узле",
        'reconnect_node': "🔄 Переподключить",
        'delete_node': "🗑️ Удалить",
        'update_node': "🔄 Обновить инфо",
        'back': "⬅️ Назад",

        # Node installation
        'install_type': "Как устанавливаем узел?",
        'single_install': "🖥️ Один сервер",
        'bulk_install': "📦 Несколько серверов",
        'enter_ssh_ip': "Какой IP сервера?",
        'enter_ssh_port': "SSH порт? (обычно 22, но ты скажи!):",
        'enter_ssh_username': "Логин для SSH:",
        'auth_method': "Как заходить?",
        'password_auth': "🔒 По паролю",
        'ssh_key_auth': "🔑 SSH ключ",
        'enter_ssh_password': "SSH пароль:",
        'enter_ssh_key': "🔑 Теперь отправь свой приватный SSH ключ:\n\n💡 Важно: Отправляй именно приватный ключ, а не публичный!\n📝 Можешь загрузить файл или скопировать текст",
        'port_config': "Настраиваем порты!",
        'custom_ports': "⚙️ Сам выберу порты",
        'random_ports': "🎲 Удиви меня!",
        'enter_node_port': "Порт узла:",
        'enter_api_port': "API порт:",
        'enter_node_name': "Как назовем узел?",
        'random_name': "🎲 Случайное имя",
        'installing_node': "🚀 Устанавливаю узел... Попей кофейку! ☕",
        'node_installed': "🎉 Ура! Узел работает!",
        'installation_failed': "😔 Что-то пошло не так: {error}\n\nНе переживай, попробуем еще!",

        # Admin features
        'admin_only': "🚫 Эй! Это только для админов. Хорошая попытка! 😉",
        'not_sudo': "🔒 Тебе нужны права sudo для этого, друг!",
        'backup_created': "💾 Бэкап готов! Все в безопасности!",
        'stats_title': "📊 Вот что происходит",
        'total_panels': "Панели: {count}",
        'total_nodes': "Узлы: {count}",
        'active_sessions': "Активных пользователей: {count}",

        # Errors
        'error_occurred': "😅 Упс! Что-то сломалось: {error}",
        'invalid_url': "🤔 URL какой-то странный...",
        'connection_timeout': "⏰ Слишком долго подключается. Попробуем еще?",
        'authentication_failed': "🔑 Не получилось войти. Проверь данные?",
        'node_not_found': "🔍 Узел не найден...",
        'operation_cancelled': "✋ Все ок, операция отменена!",

        # Success messages
        'operation_successful': "✅ Готово! Все прошло отлично!",
        'node_reconnected': "🔄 Узел снова онлайн и счастлив!",
        'node_deleted': "🗑️ Узел успешно удален!",
        'node_updated': "🔄 Информация об узле обновлена!",

        # SSH validation
        'invalid_ssh_key_format': "❌ Invalid key format! Key should start with -----BEGIN",
        'testing_ssh_connection': "🔄 Testing SSH connection...",
        'ssh_test_success': "✅ Yay! SSH connection successful!",
        'ssh_test_failed': "❌ SSH connection failed: {error}",
    },

    'ar': {
        # Start and language selection
        'welcome': "🎉 أهلاً صديقي! مرحباً بك في مدير عقد Marzban الرائع! 🚀\n\nأنا هنا لأجعل إدارة العقد سهلة وممتعة! 😊",
        'select_language': "🌍 أولاً - بأي لغة تود أن نتحدث؟",
        'language_selected': "🎯 ممتاز! الآن نتحدث بالعربية!",

        # Main menu
        'main_menu': "🏠 ماذا نفعل اليوم؟",
        'main_menu_desc': "اختر ما تحتاجه - أنا هنا للمساعدة! 😄",
        'add_panel': "➕ إضافة لوحة جديدة",
        'manage_nodes': "🔧 إدارة العقد",
        'admin_panel': "👑 لوحة الإدارة",
        'backup_data': "💾 نسخ احتياطي لكل شيء",
        'statistics': "📊 إظهار الإحصائيات",

        # Panel management
        'panel_type': "رائع! أي نوع من اللوحات نضيف؟",
        'marzban_panel': "🚀 لوحة Marzban",
        'enter_panel_url': "ممتاز! الصق رابط اللوحة هنا (بدون /dashboard أو أي إضافات):",
        'enter_username': "عظيم! ما هو اسم المستخدم الإداري؟ (تأكد من وجود صلاحيات sudo! 💪):",
        'enter_password': "رائع! والآن كلمة المرور:",
        'enter_panel_name': "جميل! اختر اسماً رائعاً لهذه اللوحة:",
        'panel_saved': "🎉 بووم! تم حفظ اللوحة وهي جاهزة للعمل!",
        'panel_connection_failed': "😅 أوه! لم أستطع الاتصال باللوحة. تحقق من البيانات؟",

        # Node management
        'select_panel': "مع أي لوحة نعمل اليوم؟",
        'no_panels': "🤔 يبدو أنك لم تضف أي لوحات بعد. دعنا نصلح هذا!",
        'node_management': "🔧 مركز إدارة العقد",
        'list_nodes': "📋 إظهار جميع العقد",
        'get_node_info': "ℹ️ تفاصيل العقدة",
        'add_new_node': "➕ إضافة عقدة جديدة",
        'nodes_list': "📋 هذه هي عقدك",
        'no_nodes': "🤷‍♂️ لا توجد عقد بعد. جاهز لإنشاء البعض؟",
        'node_info': "ℹ️ معلومات العقدة",
        'reconnect_node': "🔄 إعادة الاتصال",
        'delete_node': "🗑️ إزالة",
        'update_node': "🔄 تحديث المعلومات",
        'back': "⬅️ رجوع",

        # Node installation
        'install_type': "كيف تود تثبيت هذه العقدة؟",
        'single_install': "🖥️ سيرفر واحد فقط",
        'bulk_install': "📦 عدة سيرفرات",
        'enter_ssh_ip': "ما هو عنوان IP للسيرفر؟",
        'enter_ssh_port': "منفذ SSH؟ (عادة 22، لكن أخبرني!):",
        'enter_ssh_username': "اسم المستخدم لـ SSH:",
        'auth_method': "كيف أسجل الدخول؟",
        'password_auth': "🔒 بكلمة المرور",
        'ssh_key_auth': "🔑 مفتاح SSH",
        'enter_ssh_password': "كلمة مرور SSH:",
        'enter_ssh_key': "🔑 الآن أرسل مفتاح SSH الخاص (Private Key):\n\n💡 ملاحظة: تأكد من إرسال المفتاح الخاص وليس العام!\n📝 يمكنك رفع الملف أو نسخ النص",
        'port_config': "وقت إعداد المنافذ!",
        'custom_ports': "⚙️ سأختار المنافذ",
        'random_ports': "🎲 فاجئني!",
        'enter_node_port': "رقم منفذ العقدة:",
        'enter_api_port': "رقم منفذ API:",
        'enter_node_name': "ماذا نسمي هذه العقدة؟",
        'random_name': "🎲 اختر اسماً عشوائياً",
        'installing_node': "🚀 أقوم بتثبيت العقدة الآن... اشرب قهوة! ☕",
        'node_installed': "🎉 يااااي! العقدة تعمل الآن!",
        'installation_failed': "😔 حدث خطأ: {error}\n\nلا تقلق، يمكننا المحاولة مرة أخرى!",

        # Admin features
        'admin_only': "🚫 هاي! هذا للإداريين فقط. محاولة جيدة! 😉",
        'not_sudo': "🔒 تحتاج صلاحيات sudo لهذا يا صديقي!",
        'backup_created': "💾 النسخ الاحتياطي مكتمل! كل شيء آمن!",
        'stats_title': "📊 هذا ما يحدث",
        'total_panels': "اللوحات: {count}",
        'total_nodes': "العقد: {count}",
        'active_sessions': "المستخدمون النشطون: {count}",

        # Errors
        'error_occurred': "😅 أوبس! حدث خطأ: {error}",
        'invalid_url': "🤔 هذا الرابط يبدو غريباً...",
        'connection_timeout': "⏰ وقت طويل للاتصال. نحاول مرة أخرى؟",
        'authentication_failed': "🔑 فشل تسجيل الدخول. تحقق من البيانات؟",
        'node_not_found': "🔍 لم أجد هذه العقدة...",
        'operation_cancelled': "✋ لا مشكلة، تم إلغاء العملية!",

        # Success messages
        'operation_successful': "✅ انتهينا! كل شيء سار بشكل مثالي!",
        'node_reconnected': "🔄 عقدتك عادت أونلاين وسعيدة!",
        'node_deleted': "🗑️ تم حذف العقدة بنجاح!",
        'node_updated': "🔄 تم تحديث معلومات العقدة!",

        # SSH validation
        'invalid_ssh_key_format': "❌ Invalid key format! Key should start with -----BEGIN",
        'testing_ssh_connection': "🔄 Testing SSH connection...",
        'ssh_test_success': "✅ Yay! SSH connection successful!",
        'ssh_test_failed': "❌ SSH connection failed: {error}",
    }
}

# Supported languages list
SUPPORTED_LANGUAGES = ['en', 'fa', 'ru', 'ar']

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """Get localized text by key and language"""
    text = TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text
