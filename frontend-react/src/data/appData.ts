export type Language = 'en' | 'ar';

export interface DiagnosticResponse {
  status: string;
  pii_scrubbed: boolean;
  is_out_of_scope: boolean;
  image_count?: number;
  image_urls?: string[];
  customer_en: string;
  customer_ar: string;
  response_en: string;
  response_ar: string;
  hardware_assessment: string;
  policy_context: string;
  agent_history: string[];
  latency_seconds: number;
}

export interface ChatTurn {
  id: string;
  timestamp: string;
  userQuery: string;
  userImages: { preview: string; name: string }[];
  diagnostic: DiagnosticResponse;
  pickupTicketId?: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userQuery: string;
  images: { name: string; dataUrl: string }[];
  diagnostic: DiagnosticResponse;
}

export interface PickupRequestEntry {
  id: string;
  createdAt: string;
  customerName: string;
  mobileNumber: string;
  dohaLocation: string;
  deviceIssue: string;
  status: string;
}

export interface CatalogCard {
  id: string;
  category: 'smartphones' | 'gaming' | 'gadgets';
  badgeEn: string;
  badgeAr: string;
  titleEn: string;
  titleAr: string;
  subtitleEn: string;
  subtitleAr: string;
  sampleQueryEn: string;
  sampleQueryAr: string;
}

export const CATALOG_CARDS: CatalogCard[] = [
  {
    id: 'smartphones',
    category: 'smartphones',
    badgeEn: 'Smartphones & Tablets',
    badgeAr: 'الهواتف والأجهزة اللوحية',
    titleEn: 'iPhone, Samsung Galaxy & iPad Repair',
    titleAr: 'صيانة آيفون وسامسونج وآيباد',
    subtitleEn:
      'Cracked glass, OLED display lines, swollen batteries, or USB-C liquid corrosion triage.',
    subtitleAr:
      'فحص كسر الشاشة، خطوط OLED، انتفاخ البطارية، أو تآكل منفذ الشحن بسبب السوائل.',
    sampleQueryEn:
      'My iPhone screen cracked and the USB-C port has moisture corrosion. What is the repair timeline under Qatar law?',
    sampleQueryAr:
      'شاشة هاتفي آيفون مكسورة ومنفذ الشحن متأثر بالرطوبة. ما هي مدة الإصلاح وفق القانون القطري؟',
  },
  {
    id: 'gaming',
    category: 'gaming',
    badgeEn: 'Computers & Gaming',
    badgeAr: 'الكمبيوتر وأجهزة الألعاب',
    titleEn: 'MacBook, PS5 & Nintendo Switch Care',
    titleAr: 'العناية بماك بوك وبلايستيشن 5 وسويتش',
    subtitleEn:
      'Damaged HDMI/USB-C ports, Joy-Con/controller drift, overheating, or display faults.',
    subtitleAr:
      'أعطال منافذ HDMI، ارتفاع الحرارة، أعطال الشاشة، أو مشاكل وحدات التحكم.',
    sampleQueryEn:
      'My PS5 HDMI port is damaged and not outputting video. How long does Doha Service Center repair take?',
    sampleQueryAr:
      'منفذ HDMI في جهاز PS5 تالف ولا يعرض صورة. كم يستغرق الإصلاح في مركز صيانة الدوحة؟',
  },
  {
    id: 'gadgets',
    category: 'gadgets',
    badgeEn: 'Home & Smart Gadgets',
    badgeAr: 'الأجهزة الذكية والمنزلية',
    titleEn: 'Smart TVs, Watches & Power Gadgets',
    titleAr: 'الشاشات الذكية والساعات والإكسسوارات',
    subtitleEn:
      '2-year statutory warranty (Law No. 8/2008), 15-day loaner rule, and 6-month spare-parts guarantee.',
    subtitleAr:
      'ضمان قانوني سنتان (قانون 8/2008)، قاعدة الجهاز البديل بعد 15 يوماً، وضمان 6 أشهر على القطع.',
    sampleQueryEn:
      'My smartwatch stopped charging after 4 months with no physical damage. Am I covered under the 2-year Qatar warranty?',
    sampleQueryAr:
      'ساعتي الذكية توقفت عن الشحن بعد 4 أشهر دون أي كسر. هل يشملها ضمان السنتين في قطر؟',
  },
];

export const LABELS = {
  en: {
    brandName: 'Doha Connect',
    brandTag: 'DEVICES • GAMING • SMART CARE',
    nav1: 'Smartphones & Tablets',
    nav2: 'Computers & Gaming',
    nav3: 'Doha Service Center',
    nav4: 'Consumer Rights (Law 8)',
    heroBadge: 'Doha Connect Authorized Care • dohaconnect.qa',
    heroTitle: 'Smart Device Diagnostics & Qatar Warranty Support',
    heroSub:
      'Instant AI photo triage for smartphones, tablets, laptops, gaming consoles, and smart gadgets—grounded in Qatar Consumer Protection Law No. 8 (2008) & Ministerial Decision No. 68 (2012).',
    heroPrimaryBtn: 'Start AI Device Triage',
    heroSecondaryBtn: 'Upload Defect Photos',
    sectionTitle: 'Supported Devices & Repair Triage',
    sectionSub:
      'Select a category below to test an instant diagnosis or upload up to 4 photos in the assistant.',
    tryPromptBtn: 'Diagnose This Issue',
    slaTitle: 'Your Qatar Consumer Rights at Doha Connect',
    sla1Title: '2-Year Statutory Warranty',
    sla1Desc: 'Manufacturing defects covered under Qatar Law No. 8 of 2008.',
    sla2Title: '3–5 Business Day Repairs',
    sla2Desc: 'Standard turnaround after written quote approval with 6-month parts warranty.',
    sla3Title: '15-Day Loaner Guarantee',
    sla3Desc: 'Free replacement device if a warranty repair exceeds 15 days (Art. 8).',
    floatingBtn: 'Doha Connect AI Care',
    chatTitle: 'Doha Connect AI Assistant',
    chatSub: 'Multi-Photo Hardware & SLA Support',
    chatWelcome:
      'Marhaba! Welcome to Doha Connect Service Center (dohaconnect.qa). Describe any issue with your smartphone, tablet, laptop, gaming console, or smart gadget—or upload up to 4 photos.',
    chatPlaceholder: 'Describe device issue or ask warranty SLA...',
    sendBtn: 'Send',
    blockedBadge: 'Outside Doha Connect Scope',
  },
  ar: {
    brandName: 'دوحة كونكت',
    brandTag: 'الأجهزة • الألعاب • الصيانة الذكية',
    nav1: 'الهواتف والأجهزة اللوحية',
    nav2: 'الكمبيوتر والألعاب',
    nav3: 'مركز صيانة الدوحة',
    nav4: 'حقوق المستهلك (قانون 8)',
    heroBadge: 'مركز صيانة دوحة كونكت المعتمد • dohaconnect.qa',
    heroTitle: 'التشخيص الذكي للأجهزة ودعم الضمان في قطر',
    heroSub:
      'فحص فوري بالصور للهواتف، الأجهزة اللوحية، اللابتوب، أجهزة الألعاب، والأجهزة الذكية وفق قانون حماية المستهلك القطري رقم 8 (2008) والقرار الوزاري 68 (2012).',
    heroPrimaryBtn: 'ابدأ فحص الجهاز الآن',
    heroSecondaryBtn: 'إرفاق صور العطل',
    sectionTitle: 'الأجهزة المدعومة وخدمات الصيانة',
    sectionSub:
      'اختر فئة أدناه لتجربة التشخيص الفوري أو أرفق حتى 4 صور للعطل في المساعد الذكي.',
    tryPromptBtn: 'تشخيص هذه الحالة',
    slaTitle: 'حقوقك الاستهلاكية في دوحة كونكت',
    sla1Title: 'ضمان قانوني لمدة سنتين',
    sla1Desc: 'تغطية العيوب المصنعية بموجب قانون حماية المستهلك رقم 8 لسنة 2008.',
    sla2Title: 'إصلاح خلال 3–5 أيام عمل',
    sla2Desc: 'بعد الموافقة على التقدير المكتوب مع ضمان 6 أشهر على القطع المستبدلة.',
    sla3Title: 'جهاز بديل بعد 15 يوماً',
    sla3Desc: 'جهاز بديل مجاني إذا تجاوز إصلاح الضمان 15 يوماً (المادة 8).',
    floatingBtn: 'مساعد دوحة كونكت',
    chatTitle: 'مساعد دوحة كونكت الذكي',
    chatSub: 'تشخيص الأعطال بالصور وضمان الجودة',
    chatWelcome:
      'مرحباً بك في مركز صيانة دوحة كونكت (dohaconnect.qa)! صف أي عطل في هاتفك أو جهازك اللوحي أو اللابتوب أو جهاز الألعاب أو أرفق حتى 4 صور.',
    chatPlaceholder: 'صف عطل الجهاز أو اسأل عن شروط الضمان...',
    sendBtn: 'إرسال',
    blockedBadge: 'خارج نطاق دوحة كونكت',
  },
};