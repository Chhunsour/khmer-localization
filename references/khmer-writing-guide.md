# Practical Khmer UI Writing Guide

This reference provides UI copy conventions, vocabulary, and writing patterns for creating natural, intuitive Khmer language interfaces. It helps AI coding agents avoid wooden, literal machine translations and adopt the contemporary digital standard used across modern Cambodian applications (e.g., Bakong, ABA Mobile, Wing Bank, PassApp).

> [!NOTE]
> Translations in this guide are battle-tested recommendations for digital product interfaces. They should be reviewed by a native Khmer speaker to match the specific tone, domain, and context of your application.

---

## 1. Core Principles of Natural Khmer UI Copy

### 1.1 Clarity and Conciseness
Khmer words can be longer visually and syllable-wise than their English counterparts. On mobile screens (320px–430px wide), verbose phrasing wraps onto 3 or 4 lines, pushing interactive controls below the fold.
- **English:** "Please click the button below to confirm your subscription order"
- **Awkward Literal:** សូមចុចប៊ូតុងខាងក្រោមដើម្បីបញ្ជាក់ការបញ្ជាទិញជាវរបស់អ្នក
- **Natural Concise:** បញ្ជាក់ការជាវ (Confirm Subscription)

### 1.2 Action-Oriented Phrasing
For buttons and menu actions, prefer direct, active verbs rather than noun phrases or passive voice.
- Use **រក្សាទុក** (Save) instead of **ការធ្វើការរក្សាទុក** (The act of doing saving).
- Use **ចូលគណនី** (Log In) instead of **ចុះហត្ថលេខាលើ** (Sign signature on paper).
- Use **ចុះឈ្មោះ** (Sign Up / Register) instead of **ការចុះបញ្ជីឈ្មោះ** (Registration of name).

### 1.3 Polite but Modern Tone
Modern Cambodian tech apps use a respectful yet direct tone. The polite particle **សូម** (*saom* — "please") is essential for form validation instructions, permissions requests, and destructive confirmations, but should be omitted from compact buttons and table headers to save screen real estate.
- Button: **លុប** (Delete) — concise.
- Confirmation dialog: **តើអ្នកពិតជាចង់លុបទិន្នន័យនេះមែនទេ?** (Are you sure you want to delete this data?) — respectful.
- Form helper: **សូមបញ្ចូលលេខសម្ងាត់យ៉ាងតិច ៨ ខ្ទង់** (Please enter a password of at least 8 characters) — clear and polite.

### 1.4 Punctuation in Digital Khmer
- **Spaces:** Khmer script does not use spaces between words within a clause or phrase. A space (`U+0020`) functions like a comma or phrase separator.
- **Word Wrapping:** Use the Zero-Width Space (`U+200B` / `ZWSP`) between words in HTML or UI layouts to allow graceful line wrapping without splitting syllables.
- **Full Stop (Khan - ៕ `U+17D4`):** Traditional Khmer full stop. Used at the end of complete paragraphs, formal announcements, or policy texts. In compact UI microcopy (tooltips, small hints), it is often omitted or replaced by standard UI convention.
- **Colon (Camnuc Pii Kuuh - ៖ `U+17D6`):** Traditional Khmer colon. Used before lists or descriptions (e.g. `ស្ថានភាព៖ សកម្ម`).
- **Repetition (Lek Too - ៗ `U+17D7`):** Duplicates the preceding word (e.g., `ញឹកញាប់ៗ` = frequently; `ផ្សេងៗ` = various).
- **Question Mark (?):** Widely adopted in modern web and mobile apps for interrogative prompts (e.g., `ភ្លេចពាក្យសម្ងាត់?` — Forgot password?).

---

## 2. Navigation Labels

| English | Natural Khmer | Context & Design Notes |
| :--- | :--- | :--- |
| **Home** | ទំព័រដើម | Standard main landing tab/page. |
| **Dashboard** | ផ្ទាំងគ្រប់គ្រង | Administrative overview or central portal. |
| **Explore / Discover** | ស្វែងរក / ស្វែងយល់ | Content discovery feed. |
| **Notifications** | ការជូនដំណឹង | Bell icon tab or activity center. |
| **Messages / Chat** | សារ | In-app messaging or inbox. |
| **Profile / Account** | គណនី / ប្រវត្តិរូប | Use `គណនី` (Account) or `ប្រវត្តិរូប` (User profile). |
| **Settings** | ការកំណត់ | Global configuration and preferences. |
| **History** | ប្រវត្តិ | Transaction history (`ប្រវត្តិប្រតិបត្តិការ`) or audit log. |
| **Reports** | របាយការណ៍ | Analytics and metric exports. |
| **Help & Support** | ជំនួយ និងការគាំទ្រ | Support center, FAQ, or live agent chat. |

---

## 3. Buttons and Primary Actions

| English | Natural Khmer | Context & Best Practices |
| :--- | :--- | :--- |
| **Submit** | ដាក់ស្នើ / បញ្ជូន | Use `ដាក់ស្នើ` for applications/forms; `បញ្ជូន` for sending messages/data. |
| **Save** | រក្សាទុក | Standard persistence action. |
| **Save Changes** | រក្សាទុកការផ្លាស់ប្តូរ | Explicit form change confirmation. |
| **Cancel** | បោះបង់ | Dismiss dialog or abort current flow without saving. |
| **Delete** | លុប / លុបចេញ | Destructive action. |
| **Confirm** | បញ្ជាក់ | Final confirmation before execution. |
| **Continue** | បន្ត | Multi-step wizard progression. |
| **Next** | បន្ទាប់ | Pagination or step navigation. |
| **Back** | ថយក្រោយ / ត្រឡប់ | Return to previous screen. |
| **Edit** | កែសម្រួល / កែប្រែ | Modify existing record. |
| **Add / Create** | បន្ថែម / បង្កើត | `បន្ថែម` (Add item); `បង្កើត` (Create new account/entity). |
| **Search** | ស្វែងរក | Search input button or placeholder. |
| **Filter** | ចម្រាញ់ | Narrowing lists or facet search. |
| **Sort** | តម្រៀប | Ordering items (e.g. date, price). |
| **Download** | ទាញយក | File/document export. |
| **Upload** | ផ្ទុកឡើង | File attachment or image upload. |
| **Log In / Sign In** | ចូល / ចូលគណនី | Modern authentication standard. |
| **Sign Up / Register** | ចុះឈ្មោះ | Account creation. |
| **Log Out / Sign Out** | ចាកចេញ | Session termination. |
| **Close** | បិទ | Modal or drawer dismissal. |

---

## 4. Form Labels and Inputs

| English | Natural Khmer | Input Guidance |
| :--- | :--- | :--- |
| **Full Name** | ឈ្មោះពេញ | Default single name field. |
| **First Name** | នាម | Given name. |
| **Last Name / Family Name** | គោត្តនាម | Surname (in Cambodia, surname conventionally precedes given name). |
| **Email Address** | អាសយដ្ឋានអ៊ីមែល / អ៊ីមែល | `អ៊ីមែល` is universally understood in digital UI. |
| **Phone Number** | លេខទូរស័ព្ទ | Core identification attribute in Cambodia. |
| **Password** | ពាក្យសម្ងាត់ | Masked security credential. |
| **Confirm Password** | បញ្ជាក់ពាក្យសម្ងាត់ | Credential verification. |
| **Current Password** | ពាក្យសម្ងាត់បច្ចុប្បន្ន | Required for credential updates. |
| **Date of Birth** | ថ្ងៃខែឆ្នាំកំណើត | Standard date selector (DD/MM/YYYY). |
| **Gender / Sex** | ភេទ | Male (`ប្រុស`), Female (`ស្រី`), Other (`ផ្សេងទៀត`). |
| **Address** | អាសយដ្ឋាន | Physical address. |
| **Province / City** | រាជធានី-ខេត្ត | Phnom Penh is a municipality (`រាជធានី`); others are provinces (`ខេត្ត`). |
| **District / Khan** | ក្រុង/ស្រុក/ខណ្ឌ | `ខណ្ឌ` in Phnom Penh; `ក្រុង/ស្រុក` in provinces. |
| **Commune / Sangkat** | ឃុំ/សង្កាត់ | `សង្កាត់` in urban centers; `ឃុំ` in rural districts. |
| **Amount** | ចំនួនទឹកប្រាក់ | Financial transaction input. |
| **Remark / Note** | ចំណាំ / ការពិពណ៌នា | Optional transaction memo. |

---

## 5. Form Validation and Error Messages

Validation messages should state clearly what went wrong and provide actionable guidance.

| English | Natural Khmer |
| :--- | :--- |
| **This field is required** | សូមបំពេញព័ត៌មាននេះ |
| **Please enter a valid email address** | សូមបញ្ចូលអាសយដ្ឋានអ៊ីមែលដែលត្រឹមត្រូវ |
| **Please enter a valid phone number** | សូមបញ្ចូលលេខទូរស័ព្ទដែលត្រឹមត្រូវ |
| **Password must be at least 8 characters** | ពាក្យសម្ងាត់ត្រូវមានយ៉ាងតិច ៨ ខ្ទង់ |
| **Passwords do not match** | ពាក្យសម្ងាត់ទាំងពីរមិនត្រូវគ្នាទេ |
| **The amount exceeds your available balance** | ចំនួនទឹកប្រាក់លើសពីសមតុល្យដែលអាចប្រើបាន |
| **Invalid verification code (OTP)** | លេខកូដផ្ទៀងផ្ទាត់ (OTP) មិនត្រឹមត្រូវ |
| **Code expired. Please request a new one.** | លេខកូដបានផុតកំណត់។ សូមស្នើសុំលេខកូដថ្មី។ |

---

## 6. Success, Alert, and System Feedback

| English | Natural Khmer | Usage Note |
| :--- | :--- | :--- |
| **Saved successfully** | រក្សាទុកបានជោគជ័យ | Toast notification or alert. |
| **Updated successfully** | បានកែប្រែដោយជោគជ័យ | Record update feedback. |
| **Account created successfully** | គណនីត្រូវបានបង្កើតដោយជោគជ័យ | Onboarding completion. |
| **Payment received** | ទទួលបានការទូទាត់រួចរាល់ | Transaction confirmation. |
| **Something went wrong. Please try again.** | មានបញ្ហាបច្ចេកទេសកើតឡើង សូមព្យាយាមម្តងទៀត | User-friendly generic error (never expose raw stack traces). |
| **Network connection failed** | មិនអាចភ្ជាប់បណ្តាញបានទេ | Offline or connectivity issue. |
| **Session expired. Please log in again.** | វគ្គប្រើប្រាស់បានផុតកំណត់ សូមចូលគណនីម្តងទៀត | Token expiration or auth timeout. |

---

## 7. Empty States and Informational Placeholders

When a list or table contains no records, provide helpful, reassuring guidance rather than a blank container.

| English | Natural Khmer |
| :--- | :--- |
| **No data available** | មិនមានទិន្នន័យទេ |
| **No notifications yet** | មិនទាន់មានការជូនដំណឹងនៅឡើយទេ |
| **No transaction history** | មិនទាន់មានប្រវត្តិប្រតិបត្តិការនៅឡើយទេ |
| **No search results found** | រកមិនឃើញលទ្ធផលស្វែងរកទេ |
| **Your cart is empty** | កន្ត្រកទំនិញរបស់អ្នកទទេ |

---

## 8. Onboarding, Help, and Microcopy

| English | Natural Khmer | Context |
| :--- | :--- | :--- |
| **Welcome** | សូមស្វាគមន៍ | App opening or splash screen. |
| **Get Started** | ចាប់ផ្តើម | Initial CTA button. |
| **Skip** | រំលង | Bypass onboarding tutorial. |
| **Learn More** | ស្វែងយល់បន្ថែម | Deep-link to documentation. |
| **Terms of Service** | លក្ខខណ្ឌនៃការប្រើប្រាស់ | Legal agreement. |
| **Privacy Policy** | គោលការណ៍ឯកជនភាព | Legal disclosure. |
| **Contact Us** | ទាក់ទងមកយើងខ្ញុំ | Customer service link. |
| **Loading...** | កំពុងដំណើរការ... / កំពុងផ្ទុក... | Spinner or skeleton placeholder. |
