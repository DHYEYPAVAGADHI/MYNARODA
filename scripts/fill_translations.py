#!/usr/bin/env python3
"""
Auto-fill translation .po files for Green Naroda campaign.
Fills Gujarati (gu) and Hindi (hi) translations for all known strings.
Run: python scripts/fill_translations.py
"""

import re
import os
import sys

# ─── Core translations dictionary ─────────────────────────────────────────────
# Format: { "english msgid": ("gujarati msgstr", "hindi msgstr") }

TRANSLATIONS = {
    # Site / Nav
    "Green Naroda": ("ગ્રીન નારોદા", "ग्रीन नरोदा"),
    "Clean Naroda": ("ક્લીન નારોદા", "क्लीन नरोदा"),
    "Green Naroda Campaign": ("ગ્રીન નારોદા ઝુંબેશ", "ग्रीन नरोदा अभियान"),
    "mynaroda — Green Naroda Campaign | Government of Gujarat": (
        "mynaroda — ગ્રીન નારોદા ઝુંબેશ | ગુજરાત સરકાર",
        "mynaroda — ग्रीन नरोदा अभियान | गुजरात सरकार"
    ),
    "Mission": ("મિશન", "मिशन"),
    "Trees": ("વૃક્ષો", "वृक्ष"),
    "Gallery": ("ફોટો ગેલરી", "फोटो गैलरी"),
    "Events": ("ઇવેન્ટ્સ", "कार्यक्रम"),
    "Volunteers": ("સ્વયંસેવકો", "स्वयंसेवक"),
    "News": ("સમાચાર", "समाचार"),
    "Contact": ("સંપર્ક", "संपर्क"),
    "Sign In": ("સાઇન ઇન", "साइन इन"),
    "Join Movement": ("અભિયાનમાં જોડાઓ", "आंदोलन से जुड़ें"),
    "My Dashboard": ("મારું ડેશબોર્ડ", "मेरा डैशबोर्ड"),
    "Home": ("હોમ", "होम"),

    # Dashboard
    "Dashboard Overview": ("ડેશબોર્ડ ઓવરવ્યૂ", "डैशबोर्ड अवलोकन"),
    "My Planted Trees": ("મારા વૃક્ષો", "मेरे लगाए वृक्ष"),
    "My Uploaded Photos": ("મારા ફોટો", "मेरी अपलोड की गई तस्वीरें"),
    "My Certificates": ("મારા પ્રમાણપત્રો", "मेरे प्रमाण पत्र"),
    "Registered Events": ("નોંધાયેલ ઇવેન્ટ્સ", "पंजीकृत कार्यक्रम"),
    "Notifications": ("સૂચનાઓ", "सूचनाएं"),
    "Edit Profile": ("પ્રોફાઇલ સંપાદિત કરો", "प्रोफाइल संपादित करें"),
    "User Dashboard": ("વપરાશકર્તા ડેશબોર્ડ", "उपयोगकर्ता डैशबोर्ड"),
    "Welcome back,": ("પુનઃ સ્વાગત,", "वापस स्वागत,"),
    "Thank you for contributing to Naroda's civic green cover. Track your trees and upcoming drives below.": (
        "નારોદાના હરિયાળા આવરણ માટે તમારા યોગદાન બદલ આભાર. નીચે તમારા વૃક્ષો અને ઉપડી આવી રહેલ ઇવેન્ટ્સ ટ્રૅક કરો.",
        "नरोदा के हरित आवरण में योगदान देने के लिए धन्यवाद। अपने वृक्षों और आगामी अभियानों की जानकारी नीचे देखें।"
    ),
    "Trees Planted": ("વૃક્ષ ઉગાડ્યા", "वृक्ष लगाए"),
    "Verified contributions": ("ચકાસાયેલ યોગદાન", "सत्यापित योगदान"),
    "Volunteer Hours": ("સ્વયંસેવક કલાકો", "स्वयंसेवक घंटे"),
    "Hours contributed": ("ફાળો આપેલ કલાકો", "योगदान किए गए घंटे"),
    "Certificates": ("પ્રમાણપત્રો", "प्रमाण पत्र"),
    "Digital certificates earned": ("ડિજિટલ પ્રમાણપત્રો", "अर्जित डिजिटल प्रमाण पत्र"),
    "Recent Activity": ("તાજેતરની પ્રવૃત્તિ", "हाल की गतिविधि"),
    "No activities recorded. Start by logging a newly planted tree!": (
        "કોઈ પ્રવૃત્તિ નોંધાઈ નથી. નવા ઉગાડેલ વૃક્ષ નોંધ કરીને શરૂ કરો!",
        "कोई गतिविधि दर्ज नहीं। नव रोपित वृक्ष दर्ज करके शुरुआत करें!"
    ),

    # Trees tab
    "My Tree Contributions": ("મારા વૃક્ષ યોગદાન", "मेरा वृक्ष योगदान"),
    "Summary of all trees logged under your account.": (
        "તમારા ખાતા હેઠળ નોંધાયેલ તમામ વૃક્ષોનો સારાંશ.",
        "आपके खाते के तहत दर्ज सभी वृक्षों का सारांश।"
    ),
    "Log a New Tree": ("નવો વૃક્ષ નોંધ કરો", "नया वृक्ष दर्ज करें"),
    "Total Logged": ("કુલ નોંધાયેલ", "कुल दर्ज"),
    "Verified": ("ચકાસાયેલ", "सत्यापित"),
    "Pending Review": ("સમીક્ષા બાકી", "समीक्षा लंबित"),
    "Rejected": ("નકારાયેલ", "अस्वीकृत"),
    "How Verification Works": ("ચકાસણી કેવી રીતે કાર્ય કરે છે", "सत्यापन कैसे काम करता है"),
    "Trees you log are initially marked Pending Review. A campaign field officer or administrator verifies the record by checking the GPS location and photo evidence. Verified trees count towards the 28,855 Trees mission.": (
        "તમે નોંધ કરેલ વૃક્ષો શરૂઆતમાં 'સમીક્ષા બાકી' તરીકે ચિહ્નિત થાય છે. ઝુંબેશ ક્ષેત્ર અધિકારી GPS સ્થান અને ફોટો પ્રમાણ ચકાસીને રેકોર્ડ ચકાસે છે. ચકાસાયેલ વૃક્ષો 28,855 વૃક્ષ મિશન તરફ ગણાય છે.",
        "आपके द्वारा दर्ज वृक्ष शुरू में 'समीक्षा लंबित' के रूप में चिह्नित होते हैं। अभियान क्षेत्र अधिकारी GPS स्थान और फोटो साक्ष्य जांचकर रिकॉर्ड सत्यापित करता है। सत्यापित वृक्ष 28,855 वृक्ष मिशन में गिने जाते हैं।"
    ),
    "Campaign Contribution Progress": ("ઝુંબેશ યોગદાન પ્રગતિ", "अभियान योगदान प्रगति"),
    "Your verified trees as a share of the national mission.": (
        "રાષ્ટ્રીય મિશનના ભાગ રૂપે તમારા ચકાસાયેલ વૃક્ષો.",
        "राष्ट्रीय मिशन के हिस्से के रूप में आपके सत्यापित वृक्ष।"
    ),
    "total trees goal": ("કુલ વૃક્ષ લક્ષ્ય", "कुल वृक्ष लक्ष्य"),

    # Gallery tab
    "My Submitted Photographs": ("મારી રજૂ કરેલ છબીઓ", "मेरी प्रस्तुत तस्वीरें"),
    "Photos pending review will not appear in the public gallery until approved by an administrator.": (
        "સમીક્ષા બાકી ફોટો સંચાલક દ્વારા મંજૂર ન થાય ત્યાં સુધી જાહેર ગેલેરીમાં દેખાશે નહીં.",
        "समीक्षा लंबित तस्वीरें व्यवस्थापक द्वारा अनुमोदित होने तक सार्वजनिक गैलरी में नहीं दिखेंगी।"
    ),
    "Upload Photo": ("ફોટો અપલોડ કરો", "फोटो अपलोड करें"),
    "You have not submitted any photographs yet.": (
        "તમે હજી સુધી કોઈ છબી સબમિટ કરી નથી.",
        "आपने अभी तक कोई तस्वीर सबमिट नहीं की है।"
    ),

    # Certificates tab
    "My Digital Certificates": ("મારા ડિજિટલ પ્રમાણપત્રો", "मेरे डिजिटल प्रमाण पत्र"),
    "Verification No:": ("ચકાસણી ક્રમ:", "सत्यापन संख्या:"),
    "Issued at:": ("જારી કરવામાં આવ્યું:", "जारी किया गया:"),
    "Verify Certificate": ("પ્રમાણપત્ર ચકાસો", "प्रमाण पत्र सत्यापित करें"),
    "No certificates have been issued under your account.": (
        "તમારા ખાતા હેઠળ કોઈ પ્રમાણપત્ર જારી કરવામાં આવ્યા નથી.",
        "आपके खाते के तहत कोई प्रमाण पत्र जारी नहीं किया गया है।"
    ),

    # Events tab
    "My Registered Events and Drives": ("મારા નોંધાયેલ ઇવેન્ટ્સ", "मेरे पंजीकृत कार्यक्रम और अभियान"),
    "Show this pass at entrance": ("પ્રવેશ દ્વારે આ પાસ બતાવો", "प्रवेश पर यह पास दिखाएं"),
    "Registered": ("નોંધાયેલ", "पंजीकृत"),
    "Cancelled": ("રદ", "रद्द"),
    "You have not registered for any plantation drives.": (
        "તમે કોઈ વૃક્ષારોપણ ઝુંબેશ માટે નોંધણી કરી નથી.",
        "आपने किसी वृक्षारोपण अभियान के लिए पंजीकरण नहीं किया है।"
    ),

    # Notifications tab
    "Notifications": ("સૂચનાઓ", "सूचनाएं"),
    "View Details": ("વિગત જુઓ", "विवरण देखें"),
    "Your notification inbox is empty.": (
        "તમારું સૂચના ઇનબૉક્સ ખાલી છે.",
        "आपका सूचना इनबॉक्स खाली है।"
    ),

    # Login / Auth
    "Sign in": ("સાઇન ઇન", "साइन इन"),
    "to continue to mynaroda": ("mynaroda ચાલુ રાખવા", "mynaroda जारी रखने के लिए"),
    "Localhost Development Mode": ("લોકલ ડેવલપમેન્ट મોડ", "लोकल डेवलपमेंट मोड"),
    "Email or phone": ("ઇ-મેઇલ અથવા ફોન", "ईमेल या फोन"),
    "Enter your email address": ("ઇ-મેઇલ સરનામું દાખલ કરો", "अपना ईमेल पता दर्ज करें"),
    "Full name": ("પૂર્ણ નામ", "पूरा नाम"),
    "Your full name": ("તમારું પૂર્ણ નામ", "आपका पूरा नाम"),
    "optional": ("વૈકલ્પિક", "वैकल्पिक"),
    "Not your computer? Use a private browsing window to sign in.": (
        "આ તમારો કમ્પ્યૂટર નથી? ખાનગી બ્રાઉઝિંગ વિન્ડોનો ઉપયોગ કરો.",
        "यह आपका कंप्यूटर नहीं है? साइन इन करने के लिए निजी ब्राउज़िंग विंडो का उपयोग करें।"
    ),
    "Learn more": ("વધુ જાણો", "और जानें"),
    "Use password instead": ("તેના બદલે પાસવર્ડ ઉપયોગ કરો", "इसके बजाय पासवर्ड का उपयोग करें"),
    "Next": ("આગળ", "अगला"),
    "Privacy": ("ગોપનીયતા", "गोपनीयता"),
    "Terms": ("નિયમો", "शर्तें"),
    "Official portal of": ("સત્તાવાર પોર્ટલ", "का आधिकारिक पोर्टल"),
    "Green Naroda Campaign, Government of Gujarat": (
        "ગ્રીન નારોદા ઝુંબેશ, ગુજરાત સરકાર",
        "ग्रीन नरोदा अभियान, गुजरात सरकार"
    ),

    # Login form
    "Welcome Back": ("પુનઃ સ્વાગત", "वापस स्वागत"),
    "Sign in to track your trees and events.": (
        "તમારા વૃક્ષો અને ઇવેન્ટ્સ ટ્રૅક કરવા સાઇન ઇન કરો.",
        "अपने वृक्षों और कार्यक्रमों को ट्रैक करने के लिए साइन इन करें।"
    ),
    "Continue with Google": ("Google સાથે ચાલુ રાખો", "Google से जारी रखें"),
    "Or continue with email": ("અથવા ઇ-મેઇલ સાથે ચાલુ રાખો", "या ईमेल से जारी रखें"),
    "Email address": ("ઇ-મેઇલ સરનામું", "ईमेल पता"),
    "Password": ("પાસવર્ડ", "पासवर्ड"),
    "Remember me": ("મને યાદ રાખો", "मुझे याद रखें"),
    "Forgot your password?": ("પાસવર્ડ ભૂલ્યા?", "पासवर्ड भूल गए?"),
    "Don't have an account?": ("ખાતું નથી?", "खाता नहीं है?"),
    "Sign up now": ("હવે સાઇન અપ કરો", "अभी साइन अप करें"),
    "Invalid email or password. Please try again.": (
        "અયોગ્ય ઇ-મેઇલ અથવા પાસવર્ડ. ફરી પ્રયાસ કરો.",
        "अमान्य ईमेल या पासवर्ड। कृपया पुनः प्रयास करें।"
    ),

    # Gallery submit
    "Submit Photograph": ("ફોટો સબમિટ કરો", "तस्वीर सबमिट करें"),
    "Submit Plantation Photograph": ("વૃક્ષારોપણ ફોટો સબમિટ કરો", "वृक्षारोपण तस्वीर सबमिट करें"),
    "Share your plantation drive photographs. All submissions are reviewed by an administrator before appearing in the public gallery.": (
        "તમારી વૃક્ષારોπण ઝুंবेश ফোটো শেয়ার করুন। তমাম সবমিশন সংচালক দ্বারা পর্যালোচনা করা হয় সর্বজনীন গ্যালারিতে প্রকাশিত হওয়ার আগে।",
        "अपनी वृक्षारोपण अभियान की तस्वीरें साझा करें। सभी प्रस्तुतियां सार्वजनिक गैलरी में दिखाई देने से पहले एक व्यवस्थापक द्वारा समीक्षा की जाती हैं।"
    ),
    "Pending Administrator Approval": ("સંચાલક મંजૂરી બાકી", "व्यवस्थापक अनुमोदन लंबित"),
    "Your submitted photograph will be reviewed by the campaign administrator. Upon approval, it will appear in the public gallery and campaign reports.": (
        "તમારી સબમિટ કરેલ ફોટો ઝుんबेশ संचालक द्वारा समीक्षा की जाएगी। मंजूरी के बाद, यह सार्वजनिक गैलरी और अभियान रिपोर्ट में दिखाई देगी।",
        "आपकी प्रस्तुत तस्वीर की अभियान व्यवस्थापक द्वारा समीक्षा की जाएगी। अनुमोदन पर, यह सार्वजनिक गैलरी और अभियान रिपोर्ट में दिखाई देगी।"
    ),
    "Photograph Title": ("ફોટો શીર્ષક", "तस्वीर का शीर्षक"),
    "E.g. Neem tree planting at Naroda Cross Roads": (
        "ઉ.દા. નારોδа ক্রস রোডসে নীম গাছ রোপণ",
        "उदा. नरोदा क्रॉस रोड्स पर नीम वृक्ष रोपण"
    ),
    "Campaign Theme / Category": ("ઝुंबेश विषय / श्रेणी", "अभियान विषय / श्रेणी"),
    "— Select a category —": ("— श्रेणी चुनें —", "— श्रेणी चुनें —"),
    "Location Name": ("स्थान नाम", "स्थान का नाम"),
    "E.g. Naroda East, Ward 12": ("उदा. नरोदा ईस्ट, वार्ड 12", "उदा. नरोदा ईस्ट, वार्ड 12"),
    "Photograph File": ("ফोटো ফাইল", "तस्वीर फ़ाइल"),
    "Click to select or drag an image here": (
        "ছবি নির্বাচন করতে ক্লিক করুন বা এখানে টেনে আনুন",
        "एक छवि चुनने के लिए क्लिक करें या यहां खींचें"
    ),
    "JPEG, PNG, WebP — Maximum 10 MB": ("JPEG, PNG, WebP — अधिकतम 10 MB", "JPEG, PNG, WebP — अधिकतम 10 MB"),
    "Submit for Administrator Review": ("व्यवस्थापक समीक्षा के लिए सबमिट करें", "व्यवस्थापक समीक्षा के लिए सबमिट करें"),
    "By submitting, you confirm this photograph was taken during a Green Naroda campaign activity.": (
        "सबमिट करके आप पुष्टि करते हैं कि यह तस्वीर ग्रीन नरोदा अभियान गतिविधि के दौरान ली गई थी।",
        "सबमिट करके आप पुष्टि करते हैं कि यह तस्वीर ग्रीन नरोदा अभियान गतिविधि के दौरान ली गई थी।"
    ),

    # Campaign gallery
    "Campaign Photo Gallery": ("ઝুंबेश ফোটো গ্যালারি", "अभियान फोटो गैलरी"),
    "A visual log of our collective plantation drive. Uploaded by citizens and volunteers.": (
        "আমাদের যৌথ বৃক্ষরোপণ অভিযানের দৃশ্যমান লগ। নাগরিক এবং স্বেচ্ছাসেবীদের দ্বারা আপলোড করা হয়েছে।",
        "हमारे सामूहिक वृक्षारोपण अभियान का एक दृश्य लॉग। नागरिकों और स्वयंसेवकों द्वारा अपलोड किया गया।"
    ),
    "All Photos": ("तमाम छायाचित्र", "सभी तस्वीरें"),
    "Filter Category": ("श्रेणी फ़िल्टर करें", "श्रेणी फ़िल्टर करें"),
    "Filter Album/Collection": ("एल्बम / संग्रह फ़िल्टर करें", "एल्बम / संग्रह फ़िल्टर करें"),
    "Search location, photographer...": ("स्थान, फोटोग्राफर खोजें...", "स्थान, फोटोग्राफर खोजें..."),
    "Search": ("खोजें", "खोजें"),
    "Submit Photo": ("ফোटো সাবমিট করুন", "तस्वीर सबमिट करें"),
    "No approved gallery photos match your criteria.": (
        "आपके मानदंड से कोई अनुमोदित गैलरी तस्वीर मेल नहीं खाती।",
        "आपके मानदंड से कोई अनुमोदित गैलरी तस्वीर मेल नहीं खाती।"
    ),

    # Footer
    "Celebrating India's 80th Independence Day by planting 28,855 trees across Naroda, Ahmedabad.": (
        "ভারতের ৮০তম স্বাধীনতা দিবস উপলক্ষে নারোদা, আহমেদাবাদ জুড়ে ২৮,৮৫৫টি গাছ লাগিয়ে উদযাপন।",
        "नरोदा, अहमदाबाद में 28,855 पेड़ लगाकर भारत के 80वें स्वतंत्रता दिवस का जश्न मनाना।"
    ),
    "Campaign": ("ઝुंबेश", "अभियान"),
    "Tree Tracker": ("वृक्ष ट्रैकर", "वृक्ष ट्रैकर"),
    "Plant a Tree": ("वृक्ष लगाएं", "वृक्ष लगाएं"),
    "Photo Gallery": ("ফোটো গ্যালারি", "फोटो गैलरी"),
    "Volunteer Portal": ("স্বেচ্ছাসেবী পোর্টাল", "स्वयंसेवक पोर्टल"),
    "Environmental Impact": ("পরিবেশগত প্রভাব", "पर्यावरणीय प्रभाव"),
    "Information": ("তথ্য", "जानकारी"),
    "About Campaign": ("ঝুনবেশ সম্পর্কে", "अभियान के बारे में"),
    "News & Updates": ("সমাচার ও আপডেট", "समाचार और अपडेट"),
    "FAQ": ("FAQ", "FAQ"),
    "Contact Us": ("আমাদের সাথে যোগাযোগ করুন", "हमसे संपर्क करें"),
    "A civic environmental campaign.": (
        "একটি নাগরিক পরিবেশ অভিযান।",
        "एक नागरिक पर्यावरण अभियान।"
    ),
    "Admin": ("প্রশাসন", "प्रशासन"),
    "Sitemap": ("সাইটম্যাপ", "साइटमैप"),

    # Personal info strings
    "Personal info": ("ব্যক্তিগত তথ্য", "व्यक्तिगत जानकारी"),
    "Permissions & Roles": ("অনুমতি ও ভূমিকা", "अनुमतियां और भूमिकाएं"),
    "Important dates": ("গুরুত্বপূর্ণ তারিখ", "महत्वपूर्ण तिथियां"),

    # Profile
    "Edit Profile": ("প্রোফাইল সম্পাদনা করুন", "प्रोफाइल संपादित करें"),
    "Profile updated successfully.": ("প্রোফাইল সফলভাবে আপডেট হয়েছে।", "प्रोफाइल सफलतापूर्वक अपडेट की गई।"),
    "Phone number verified successfully.": ("ফোন নম্বর সফলভাবে যাচাই হয়েছে।", "फोन नंबर सफलतापूर्वक सत्यापित किया गया।"),
    "Invalid OTP. Please try again.": ("অবৈধ OTP। পুনরায় চেষ্টা করুন।", "अमान्य OTP। कृपया पुनः प्रयास करें।"),

    # Approval statuses
    "Approved": ("मंजूर", "अनुमोदित"),
    "Pending Review": ("समीक्षा बाकी", "समीक्षा लंबित"),
    "Rejected": ("नकारायेल", "अस्वीकृत"),

    # Welcome message
    "Welcome! You are now signed in as %(name)s.": (
        "સ્વાગત! તમે %(name)s તરીકે સાઈન ઇન કર્યું.",
        "स्वागत! आप %(name)s के रूप में साइन इन हैं।"
    ),
    "Please enter a valid email address.": (
        "કૃपया वैध ईमेल पता दर्ज करें।",
        "कृपया एक मान्य ईमेल पता दर्ज करें।"
    ),
    "Your photograph has been submitted for review. It will appear in the public gallery once approved by an administrator.": (
        "तमारी छायाचित्र समीक्षा के लिए सबमिट कर दी गई है। व्यवस्थापक द्वारा अनुमोदित होने पर यह सार्वजनिक गैलरी में दिखाई देगी।",
        "आपकी तस्वीर समीक्षा के लिए सबमिट कर दी गई है। व्यवस्थापक द्वारा अनुमोदित होने पर यह सार्वजनिक गैलरी में दिखाई देगी।"
    ),
}


def fill_po_file(filepath: str, lang: str, index: int):
    """Read a .po file and fill in translated msgstr values for known msgids."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix header
    if lang == "gu":
        content = content.replace(
            '"Language: \\n"',
            '"Language: gu\\n"'
        ).replace(
            "# SOME DESCRIPTIVE TITLE.",
            "# mynaroda — Green Naroda Campaign — Gujarati Translation"
        ).replace(
            "\"Language-Team: LANGUAGE <LL@li.org>\\n\"",
            "\"Language-Team: Gujarati <gu@mynaroda.in>\\n\""
        )
    elif lang == "hi":
        content = content.replace(
            '"Language: \\n"',
            '"Language: hi\\n"'
        ).replace(
            "# SOME DESCRIPTIVE TITLE.",
            "# mynaroda — Green Naroda Campaign — Hindi Translation"
        ).replace(
            "\"Language-Team: LANGUAGE <LL@li.org>\\n\"",
            "\"Language-Team: Hindi <hi@mynaroda.in>\\n\""
        )

    # Replace #, fuzzy header
    content = content.replace("#, fuzzy\nmsgid \"\"\n", "msgid \"\"\n", 1)

    # Fill in translations for known msgids
    count = 0
    for msgid, translations in TRANSLATIONS.items():
        msgstr = translations[index]
        # Escape special chars
        escaped_msgid = msgid.replace('"', '\\"')
        escaped_msgstr = msgstr.replace('"', '\\"')
        # Simple replacement: msgid "..." \n msgstr "" → msgid "..." \n msgstr "translated"
        old = f'msgid "{escaped_msgid}"\nmsgstr ""\n'
        new = f'msgid "{escaped_msgid}"\nmsgstr "{escaped_msgstr}"\n'
        if old in content:
            content = content.replace(old, new)
            count += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [{lang}] Filled {count} translations in {filepath}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gu_po = os.path.join(base, "locale", "gu", "LC_MESSAGES", "django.po")
    hi_po = os.path.join(base, "locale", "hi", "LC_MESSAGES", "django.po")

    print("Filling translations...")
    fill_po_file(gu_po, "gu", 0)
    fill_po_file(hi_po, "hi", 1)
    print("Done. Now run: python manage.py compilemessages")
