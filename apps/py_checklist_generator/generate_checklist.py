import argparse, datetime, pathlib

TEMPLATES = {
 "en": "# SAHAYAM One-Page Plan\n\nName: {name}\nPhone: {phone}\n\n"
       "1) Turn on screen lock ✓\n2) Enable 2FA for: {apps}\n3) Update phone, auto-update on\n"
       "4) Bank app limits set: daily {limit}\n5) Scam rules: never share OTP, no links in SMS\n"
       "6) Backup: WhatsApp, Photos\n\nFollow-up date: {date}\n",
 "te": "# సహాయం ఒక పేజీ ప్లాన్\n\nపేరు: {name}\nఫోన్: {phone}\n\n"
       "1) స్క్రీన్ లాక్ ఆన్ ✓\n2) 2FA యాప్‌లు: {apps}\n3) ఫోన్ అప్డేట్\n"
       "4) బ్యాంక్ పరిమితి: రోజుకు {limit}\n5) మోసం నియమాలు: OTP పంచుకోదు\n"
       "6) బ్యాకప్: వాట్సాప్, ఫోటోలు\n\nఫాలో-అప్ తేదీ: {date}\n",
 "hi": "# सहायता एक-पेज योजना\n\nनाम: {name}\nफोन: {phone}\n\n"
       "1) स्क्रीन लॉक ✓\n2) 2FA ऐप्स: {apps}\n3) फोन अपडेट\n"
       "4) बैंक लिमिट: प्रतिदिन {limit}\n5) ठगी नियम: OTP कभी साझा न करें\n"
       "6) बैकअप: व्हाट्सएप, फ़ोटो\n\nफॉलो-अप दिनांक: {date}\n"
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--phone", required=True)
    p.add_argument("--apps", default="Google, WhatsApp, Bank")
    p.add_argument("--limit", default="₹5,000")
    p.add_argument("--lang", choices=["en","te","hi"], default="en")
    p.add_argument("--out", default="checklist.md")
    args = p.parse_args()

    text = TEMPLATES[args.lang].format(
        name=args.name,
        phone=args.phone,
        apps=args.apps,
        limit=args.limit,
        date=(datetime.date.today()+datetime.timedelta(days=7)).isoformat()
    )
    pathlib.Path(args.out).write_text(text, encoding="utf-8")
    print("Written", args.out)

if __name__=="__main__":
    main()
